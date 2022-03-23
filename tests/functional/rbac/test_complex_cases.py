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

"""Test complex RBAC cases"""

# pylint: disable=no-self-use, too-many-arguments

from typing import Iterable

import allure
import pytest
from adcm_client.objects import ADCMClient

from tests.functional.rbac.conftest import create_policy, BusinessRoles as BR, as_user_objects, is_allowed, is_denied
from tests.functional.tools import AnyADCMObject


class TestTwoUsers:
    """Test permissions when two non-superusers are in play"""

    _SECOND_USER_CREDS = ("second_user", "password")

    @pytest.fixture()
    def first_user(self, user):
        """Wrap first non-superuser"""
        return user

    @pytest.fixture()
    def second_user(self, sdk_client_fs):
        """Create second non-superuser"""
        return sdk_client_fs.user_create(*self._SECOND_USER_CREDS)

    @pytest.fixture()
    def second_user_sdk(self, adcm_fs, second_user):  # pylint: disable=unused-argument
        """ADCM Client for second non-superuser"""
        username, password = self._SECOND_USER_CREDS
        return ADCMClient(url=adcm_fs.url, user=username, password=password)

    # pylint: disable=too-many-locals

    def test_grant_role_to_users_withdraw_from_one(
        self, sdk_client_fs, user_sdk, second_user_sdk, first_user, second_user, prepare_objects, second_objects
    ):
        """
        Assign role to two users
        Remove role from one of them
        Check permissions are correct
        """
        cluster, service, component, provider, host = prepare_objects
        objects_wo_service = [cluster, component, provider, host, *second_objects]
        admin_client, first_client, second_client = sdk_client_fs, user_sdk, second_user_sdk

        with allure.step('Create policy assigned to both users'):
            policy = create_policy(admin_client, BR.EditServiceConfigurations, [service], [first_user, second_user], [])

        with allure.step('Check that config of only one service can be edited by both users'):
            self._edit_is_allowed_to(first_client, [service])
            self._edit_is_allowed_to(second_client, [service])
            self._edit_is_denied_to(first_client, objects_wo_service)
            self._edit_is_denied_to(second_client, objects_wo_service)

        with allure.step('Remove one of users from policy'):
            policy.update(user=[{'id': second_user.id}])

        with allure.step('Check that only one of users can edit config of one service'):
            self._edit_is_allowed_to(second_client, [service])
            self._edit_is_denied_to(second_client, objects_wo_service)
            self._edit_is_denied_to(first_client, [*prepare_objects, *second_objects])

    def test_change_users_in_groups(
        self, sdk_client_fs, user_sdk, second_user_sdk, first_user, second_user, prepare_objects, second_objects
    ):
        """
        Add two users to groups
        Create policies assigned to groups
        Change users in groups
        """
        cluster, service, component, provider, host = prepare_objects
        objects_wo_service = [cluster, component, provider, host, *second_objects]
        objects_wo_cluster = [service, component, provider, host, *second_objects]
        admin_client, first_client, second_client = sdk_client_fs, user_sdk, second_user_sdk

        with allure.step('Create two groups with one user in each'):
            first_group = admin_client.group_create('First Group', user=[{'id': first_user.id}])
            second_group = admin_client.group_create('Second Group', user=[{'id': second_user.id}])

        with allure.step('Create two policies and assign separate group to each'):
            create_policy(admin_client, BR.EditServiceConfigurations, [service], [], [first_group])
            create_policy(admin_client, BR.EditClusterConfigurations, [cluster], [], [second_group])

        with allure.step('Check that one user have access only to service config and another only to cluster config'):
            self._edit_is_allowed_to(first_client, [service])
            self._edit_is_allowed_to(second_client, [cluster])
            self._edit_is_denied_to(first_client, objects_wo_service)
            self._edit_is_denied_to(second_client, objects_wo_cluster)

        with allure.step('Swap users in groups'):
            first_group.update(user=[{'id': second_user.id}])
            second_group.update(user=[{'id': first_user.id}])

        with allure.step('Check that permissions were swapped'):
            self._edit_is_allowed_to(first_client, [cluster])
            self._edit_is_allowed_to(second_client, [service])
            self._edit_is_denied_to(first_client, objects_wo_cluster)
            self._edit_is_denied_to(second_client, objects_wo_service)

    def test_grant_different_permissions_to_two_users(
        self, sdk_client_fs, user_sdk, second_user_sdk, first_user, second_user, prepare_objects, second_objects
    ):
        """
        Give one user one permission
        Give another user second permission
        Check they don't mix
        """
        cluster, service, component, provider, host = prepare_objects
        objects_wo_service = [cluster, component, provider, host, *second_objects]
        objects_wo_cluster = [service, component, provider, host, *second_objects]
        admin_client, first_client, second_client = sdk_client_fs, user_sdk, second_user_sdk

        with allure.step('Create two policies and assign separate group to each'):
            first_policy = create_policy(admin_client, BR.EditServiceConfigurations, [service], [first_user], [])
            second_policy = create_policy(admin_client, BR.EditClusterConfigurations, [cluster], [second_user], [])

        with allure.step(
            'Check that one user have access only to cluster config change, another user to service config change'
        ):
            self._edit_is_allowed_to(first_client, [service])
            self._edit_is_allowed_to(second_client, [cluster])
            self._edit_is_denied_to(first_client, objects_wo_service)
            self._edit_is_denied_to(second_client, objects_wo_cluster)

        with allure.step('Change users in policies'):
            first_policy.update(user=[{'id': second_user.id}])
            second_policy.update(user=[{'id': first_user.id}])

        with allure.step('Check that permissions were swapped'):
            self._edit_is_allowed_to(first_client, [cluster])
            self._edit_is_allowed_to(second_client, [service])
            self._edit_is_denied_to(first_client, objects_wo_cluster)
            self._edit_is_denied_to(second_client, objects_wo_service)

    def test_reassign_policies_between_two_users(
        self, sdk_client_fs, user_sdk, second_user_sdk, first_user, second_user, prepare_objects, second_objects
    ):
        """
        Grant policy to one user
        Grant it to both
        Grant it to another user
        """
        cluster, service, component, provider, host = prepare_objects
        objects_wo_service = [cluster, component, provider, host, *second_objects]
        admin_client, first_client, second_client = sdk_client_fs, user_sdk, second_user_sdk

        with allure.step('Create policy assigned to one user'):
            policy = create_policy(admin_client, BR.EditServiceConfigurations, [service], [first_user], [])

        with allure.step('Check that user have access only to service config change'):
            self._edit_is_allowed_to(first_client, [service])
            self._edit_is_denied_to(first_client, objects_wo_service)
            self._edit_is_denied_to(second_client, [*prepare_objects, *second_objects])

        with allure.step('Grant access to both users to edit service config'):
            policy.update(user=[{'id': first_user.id}, {'id': second_user.id}])

        with allure.step('Check that both users have access only to service config change'):
            self._edit_is_allowed_to(first_client, [service])
            self._edit_is_allowed_to(second_client, [service])
            self._edit_is_denied_to(first_client, objects_wo_service)
            self._edit_is_denied_to(second_client, objects_wo_service)

        with allure.step('Remove first user from policy'):
            policy.update(user=[{'id': second_user.id}])

        with allure.step('Check that another user now have access only to service config edit'):
            self._edit_is_allowed_to(second_client, [service])
            self._edit_is_denied_to(second_client, objects_wo_service)
            self._edit_is_denied_to(first_client, [*prepare_objects, *second_objects])

    # pylint: enable=too-many-locals

    def _edit_is_allowed_to(self, user_client: ADCMClient, objects: Iterable[AnyADCMObject]):
        user_client.reread()
        for obj in as_user_objects(user_client, *objects):
            is_allowed(obj, BR.edit_config_of(obj))

    def _edit_is_denied_to(self, user_client: ADCMClient, objects: Iterable[AnyADCMObject]):
        user_client.reread()
        for obj in objects:
            is_denied(obj, BR.edit_config_of(obj), client=user_client)