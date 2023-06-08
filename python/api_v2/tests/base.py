# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import tarfile
from pathlib import Path
from shutil import rmtree

from api_v2.prototype.utils import accept_license
from cm.api import add_cluster, add_host, add_host_provider, add_host_to_cluster
from cm.bundle import prepare_bundle, process_file
from cm.models import (
    ADCM,
    Bundle,
    Cluster,
    ConfigLog,
    Host,
    HostProvider,
    ObjectType,
    Prototype,
)
from django.conf import settings
from init_db import init
from rbac.upgrade.role import init_roles
from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):  # pylint: disable=too-many-instance-attributes
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        init_roles()
        init()

        adcm = ADCM.objects.first()
        config_log = ConfigLog.objects.get(obj_ref=adcm.config)
        config_log.config["auth_policy"]["max_password_length"] = 20
        config_log.save(update_fields=["config"])

    def setUp(self) -> None:
        self.client.login(username="admin", password="admin")

        cluster_bundle_1_path = settings.BASE_DIR / "python" / "api_v2" / "tests" / "bundles" / "cluster_one"
        cluster_bundle_2_path = settings.BASE_DIR / "python" / "api_v2" / "tests" / "bundles" / "cluster_two"
        provider_bundle_path = settings.BASE_DIR / "python" / "api_v2" / "tests" / "bundles" / "provider"

        self.bundle_1 = self.add_bundle(source_dir=cluster_bundle_1_path)
        self.bundle_2 = self.add_bundle(source_dir=cluster_bundle_2_path)
        self.provider_bundle = self.add_bundle(source_dir=provider_bundle_path)

        self.cluster_1 = self.add_cluster(bundle=self.bundle_1, name="cluster_1", description="cluster_1")
        self.cluster_2 = self.add_cluster(bundle=self.bundle_2, name="cluster_2", description="cluster_2")
        self.provider = self.add_provider(bundle=self.provider_bundle, name="provider", description="provider")

    def tearDown(self) -> None:
        dirs_to_clear = (
            *Path(settings.BUNDLE_DIR).iterdir(),
            *Path(settings.DOWNLOAD_DIR).iterdir(),
            *Path(settings.FILE_DIR).iterdir(),
            *Path(settings.LOG_DIR).iterdir(),
            *Path(settings.RUN_DIR).iterdir(),
            *Path(settings.VAR_DIR).iterdir(),
        )

        for item in dirs_to_clear:
            if item.is_dir():
                rmtree(item)
            else:
                if item.name != ".gitkeep":
                    item.unlink()

    @staticmethod
    def prepare_bundle_file(source_dir: Path) -> str:
        bundle_file = f"{source_dir.name}.tar"
        with tarfile.open(settings.DOWNLOAD_DIR / bundle_file, "w") as tar:
            for file in source_dir.iterdir():
                tar.add(name=file, arcname=file.name)

        return bundle_file

    def add_bundle(self, source_dir: Path) -> Bundle:
        bundle_file = self.prepare_bundle_file(source_dir=source_dir)
        bundle_hash, path = process_file(bundle_file=bundle_file)
        return prepare_bundle(bundle_file=bundle_file, bundle_hash=bundle_hash, path=path)

    @staticmethod
    def add_cluster(bundle: Bundle, name: str, description: str = "") -> Cluster:
        prototype = Prototype.objects.filter(bundle=bundle, type=ObjectType.CLUSTER).first()
        if prototype.license_path is not None:
            accept_license(prototype=prototype)
            prototype.refresh_from_db(fields=["license"])
        return add_cluster(prototype=prototype, name=name, description=description)

    @staticmethod
    def add_provider(bundle: Bundle, name: str, description: str = "") -> HostProvider:
        prototype = Prototype.objects.filter(bundle=bundle, type=ObjectType.PROVIDER).first()
        return add_host_provider(prototype=prototype, name=name, description=description)

    @staticmethod
    def add_host(bundle: Bundle, provider: HostProvider, fqdn: str, description: str = "") -> Host:
        prototype = Prototype.objects.filter(bundle=bundle, type=ObjectType.HOST).first()
        return add_host(prototype=prototype, provider=provider, fqdn=fqdn, description=description)

    @staticmethod
    def add_host_to_cluster(cluster: Cluster, host: Host) -> Host:
        return add_host_to_cluster(cluster=cluster, host=host)