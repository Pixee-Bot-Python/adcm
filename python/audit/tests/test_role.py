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
from django.urls import reverse
from rbac.models import Role, RoleTypes, User
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from adcm.tests.base import APPLICATION_JSON, BaseTestCase


class TestRole(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.role_display_name = "test_role"
        self.child = Role.objects.create(
            name="test_child_role",
            display_name="test_child_role",
            type=RoleTypes.business,
        )
        self.role = Role.objects.create(name="test_role_2", built_in=False)
        self.list_name = "rbac:role-list"
        self.detail_name = "rbac:role-detail"
        self.role_created_str = "Role created"
        self.role_updated_str = "Role updated"

    def check_log(
        self,
        log: AuditLog,
        operation_name: str,
        operation_type: AuditLogOperationType,
        operation_result: AuditLogOperationResult,
        user: User,
    ) -> None:
        self.assertEqual(log.audit_object.object_id, self.role.pk)
        self.assertEqual(log.audit_object.object_name, self.role.name)
        self.assertEqual(log.audit_object.object_type, AuditObjectType.Role)
        self.assertFalse(log.audit_object.is_deleted)
        self.assertEqual(log.operation_name, operation_name)
        self.assertEqual(log.operation_type, operation_type)
        self.assertEqual(log.operation_result, operation_result)
        self.assertIsInstance(log.operation_time, datetime)
        self.assertEqual(log.user.pk, user.pk)
        self.assertEqual(log.object_changes, {})

    def check_log_update(
        self, log: AuditLog, operation_result: AuditLogOperationResult, user: User
    ) -> None:
        return self.check_log(
            log=log,
            operation_name=self.role_updated_str,
            operation_type=AuditLogOperationType.Update,
            operation_result=operation_result,
            user=user,
        )

    def test_create(self):
        res: Response = self.client.post(
            path=reverse(self.list_name),
            data={
                "display_name": self.role_display_name,
                "child": [{"id": self.child.pk}],
            },
            content_type=APPLICATION_JSON,
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.assertEqual(log.audit_object.object_id, res.data["id"])
        self.assertEqual(log.audit_object.object_name, self.role_display_name)
        self.assertEqual(log.audit_object.object_type, AuditObjectType.Role)
        self.assertFalse(log.audit_object.is_deleted)
        self.assertEqual(log.operation_name, self.role_created_str)
        self.assertEqual(log.operation_type, AuditLogOperationType.Create)
        self.assertEqual(log.operation_result, AuditLogOperationResult.Success)
        self.assertIsInstance(log.operation_time, datetime)
        self.assertEqual(log.user.pk, self.test_user.pk)
        self.assertEqual(log.object_changes, {})

        self.client.post(
            path=reverse(self.list_name),
            data={
                "display_name": self.role_display_name,
                "child": [{"id": self.child.pk}],
            },
            content_type=APPLICATION_JSON,
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.assertFalse(log.audit_object)
        self.assertEqual(log.operation_name, self.role_created_str)
        self.assertEqual(log.operation_type, AuditLogOperationType.Create)
        self.assertEqual(log.operation_result, AuditLogOperationResult.Fail)
        self.assertIsInstance(log.operation_time, datetime)
        self.assertEqual(log.user.pk, self.test_user.pk)
        self.assertEqual(log.object_changes, {})

    def test_create_denied(self):
        with self.no_rights_user_logged_in:
            res: Response = self.client.post(
                path=reverse(self.list_name),
                data={
                    "display_name": self.role_display_name,
                    "child": [{"id": self.child.pk}],
                },
                content_type=APPLICATION_JSON,
            )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.assertEqual(res.status_code, HTTP_403_FORBIDDEN)
        self.assertFalse(log.audit_object)
        self.assertEqual(log.operation_name, self.role_created_str)
        self.assertEqual(log.operation_type, AuditLogOperationType.Create)
        self.assertEqual(log.operation_result, AuditLogOperationResult.Denied)
        self.assertIsInstance(log.operation_time, datetime)
        self.assertEqual(log.user.pk, self.no_rights_user.pk)
        self.assertEqual(log.object_changes, {})

    def test_delete(self):
        self.client.delete(
            path=reverse(self.detail_name, kwargs={"pk": self.role.pk}),
            content_type=APPLICATION_JSON,
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.check_log(
            log=log,
            operation_name="Role deleted",
            operation_type=AuditLogOperationType.Delete,
            operation_result=AuditLogOperationResult.Success,
            user=self.test_user,
        )

    def test_delete_denied(self):
        with self.no_rights_user_logged_in:
            res: Response = self.client.delete(
                path=reverse(self.detail_name, kwargs={"pk": self.role.pk}),
                content_type=APPLICATION_JSON,
            )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        assert res.status_code == HTTP_403_FORBIDDEN
        self.check_log(
            log=log,
            operation_name="Role deleted",
            operation_type=AuditLogOperationType.Delete,
            operation_result=AuditLogOperationResult.Denied,
            user=self.no_rights_user,
        )

    def test_update_put(self):
        self.client.put(
            path=reverse(self.detail_name, kwargs={"pk": self.role.pk}),
            data={
                "display_name": "new_display_name",
                "child": [{"id": self.child.pk}],
            },
            content_type=APPLICATION_JSON,
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.check_log_update(
            log=log,
            operation_result=AuditLogOperationResult.Success,
            user=self.test_user,
        )

    def test_update_put_denied(self):
        with self.no_rights_user_logged_in:
            res: Response = self.client.put(
                path=reverse(self.detail_name, kwargs={"pk": self.role.pk}),
                data={
                    "display_name": "new_display_name",
                    "child": [{"id": self.child.pk}],
                },
                content_type=APPLICATION_JSON,
            )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        assert res.status_code == HTTP_403_FORBIDDEN
        self.check_log_update(
            log=log,
            operation_result=AuditLogOperationResult.Denied,
            user=self.no_rights_user,
        )

    def test_update_patch(self):
        self.client.patch(
            path=reverse(self.detail_name, kwargs={"pk": self.role.pk}),
            data={
                "display_name": "new_display_name",
                "child": [{"id": self.child.pk}],
            },
            content_type=APPLICATION_JSON,
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        self.check_log_update(
            log=log,
            operation_result=AuditLogOperationResult.Success,
            user=self.test_user,
        )

    def test_update_patch_denied(self):
        with self.no_rights_user_logged_in:
            res: Response = self.client.patch(
                path=reverse(self.detail_name, kwargs={"pk": self.role.pk}),
                data={
                    "display_name": "new_display_name",
                    "child": [{"id": self.child.pk}],
                },
                content_type=APPLICATION_JSON,
            )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        assert res.status_code == HTTP_403_FORBIDDEN
        self.check_log_update(
            log=log,
            operation_result=AuditLogOperationResult.Denied,
            user=self.no_rights_user,
        )

    def test_update_patch_failed(self):
        res: Response = self.client.patch(
            path=reverse(self.detail_name, kwargs={"pk": self.role.pk}),
            data={
                "display_name": "new_display_name",
                "child": [{"id": -1}],
            },
            content_type=APPLICATION_JSON,
        )

        log: AuditLog = AuditLog.objects.order_by("operation_time").last()

        assert res.status_code == HTTP_400_BAD_REQUEST
        self.check_log_update(
            log=log,
            operation_result=AuditLogOperationResult.Fail,
            user=self.test_user,
        )
