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


from unittest.mock import patch

from api_v2.tests.cluster.base import ClusterBaseTestCase
from cm.models import Upgrade
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from adcm.tests.base import APPLICATION_JSON


class TestUpgrade(ClusterBaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.upgrade = Upgrade.objects.create(
            name="test_upgrade",
            bundle=self.bundle,
            min_version="1",
            max_version="99",
            state_available="any",
            action=self.action,
        )

    def test_list_upgrades_success(self):
        response: Response = self.client.get(
            path=reverse(viewname="v2:upgrade-list", kwargs={"cluster_pk": self.cluster_1.pk}),
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_retrieve_success(self):
        response: Response = self.client.get(
            path=reverse(viewname="v2:upgrade-detail", kwargs={"cluster_pk": self.cluster_1.pk, "pk": self.upgrade.pk}),
        )

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_run_success(self):
        with patch("api_v2.upgrade.views.do_upgrade"):
            response: Response = self.client.post(
                path=reverse(
                    viewname="v2:upgrade-run",
                    kwargs={"cluster_pk": self.cluster_1.pk, "pk": self.upgrade.pk},
                ),
                data={
                    "host_component_map": [
                        {
                            "id": self.hostcomponent.pk,
                            "host_id": self.host.pk,
                            "component_id": self.component.pk,
                            "service_id": self.service.pk,
                        },
                    ],
                    "config": {"additional_prop_1": {}},
                    "attr": {},
                    "is_verbose": True,
                },
                content_type=APPLICATION_JSON,
            )

        self.assertEqual(response.status_code, HTTP_200_OK)