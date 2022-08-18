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

from datetime import datetime

from audit.models import (
    AuditLog,
    AuditLogOperationResult,
    AuditLogOperationType,
    AuditObjectType,
)
from cm.models import (
    ADCM,
    Bundle,
    Cluster,
    ConfigLog,
    GroupConfig,
    ObjectConfig,
    Prototype,
)
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN

from adcm.tests.base import BaseTestCase


class TestConfigLog(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.config = ObjectConfig.objects.create(current=1, previous=1)
        self.bundle = Bundle.objects.create()
        prototype = Prototype.objects.create(bundle=self.bundle)
        self.cluster = Cluster.objects.create(prototype=prototype, config=self.config)
        ConfigLog.objects.create(obj_ref=self.config, config="{}")
        self.group_config = GroupConfig.objects.create(
            name="test_group_config",
            object_id=self.cluster.pk,
            object_type=ContentType.objects.get(app_label="cm", model="cluster"),
            config_id=self.config.pk,
        )

    def check_log(self, log: AuditLog) -> None:
        self.assertEqual(log.audit_object.object_id, self.cluster.pk)
        self.assertEqual(log.audit_object.object_name, self.cluster.name)
        self.assertEqual(log.audit_object.object_type, AuditObjectType.Cluster)
        self.assertFalse(log.audit_object.is_deleted)
        self.assertEqual(log.operation_name, "Cluster config log updated")
        self.assertEqual(log.operation_type, AuditLogOperationType.Update)
        self.assertEqual(log.operation_result, AuditLogOperationResult.Success)
        self.assertIsInstance(log.operation_time, datetime)
        self.assertEqual(log.user.pk, self.test_user.pk)
        self.assertIsInstance(log.object_changes, dict)

    def check_log_denied(self, log: AuditLog) -> None:
        self.assertFalse(log.audit_object)
        self.assertEqual(log.operation_name, "config log updated")
        self.assertEqual(log.operation_type, AuditLogOperationType.Update)
        self.assertEqual(log.operation_result, AuditLogOperationResult.Denied)
        self.assertIsInstance(log.operation_time, datetime)
        self.assertEqual(log.user.pk, self.no_rights_user.pk)
        self.assertIsInstance(log.object_changes, dict)

    def test_create(self):
        self.client.post(
            path=reverse("config-log-list"),
            data={"obj_ref": self.config.pk, "config": "{}"},
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.check_log(log=log)

    def test_create_denied(self):
        bundle = Bundle.objects.create(name="new_test_bundle")
        prototype = Prototype.objects.create(bundle=bundle, type="adcm")
        config = ObjectConfig.objects.create(current=1, previous=0)
        ConfigLog.objects.create(obj_ref=config, config="{}")
        ADCM.objects.create(prototype=prototype, name="ADCM", config=config)

        with self.no_rights_user_logged_in:
            res: Response = self.client.post(
                path=reverse("config-log-list"),
                data={"obj_ref": config.pk, "config": "{}"},
            )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.assertEqual(res.status_code, HTTP_403_FORBIDDEN)
        self.check_log_denied(log=log)

    def test_create_via_group_config(self):
        self.client.post(
            path=f"/api/v1/group-config/{self.group_config.pk}/"
            f"config/{self.config.pk}/config-log/",
            data={"obj_ref": self.config.pk, "config": "{}"},
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.check_log(log=log)

    def test_create_via_group_config_denied(self):
        with self.no_rights_user_logged_in:
            res: Response = self.client.post(
                path=f"/api/v1/group-config/{self.group_config.pk}/"
                f"config/{self.config.pk}/config-log/",
                data={"obj_ref": self.config.pk, "config": "{}"},
            )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.assertEqual(res.status_code, HTTP_403_FORBIDDEN)
        self.check_log_denied(log=log)
