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

from api_v2.rbac.users.constants import UserStatusChoices, UserTypeChoices
from django.db.models import QuerySet
from django_filters.rest_framework import ChoiceFilter, FilterSet
from rbac.models import User

from adcm.filters import BaseOrderingFilter


class UserOrderingFilter(BaseOrderingFilter):
    allowed_sort_column_names = {"id", "username"}


class UserFilterSet(FilterSet):
    status = ChoiceFilter(choices=UserStatusChoices.choices, method="filter_status")
    userType = ChoiceFilter(choices=UserTypeChoices.choices, method="filter_type")

    class Meta:
        model = User
        fields = ["username", "status", "userType"]

    @staticmethod
    def filter_status(queryset: QuerySet, name: str, value: str) -> QuerySet:  # pylint: disable=unused-argument
        match value:
            case UserStatusChoices.ACTIVE:
                filter_value = True
            case UserStatusChoices.BLOCKED:
                filter_value = False

        return queryset.filter(blocked_at__isnull=filter_value)

    @staticmethod
    def filter_type(queryset: QuerySet, name: str, value: str) -> QuerySet:  # pylint: disable=unused-argument
        match value:
            case UserTypeChoices.LOCAL:
                filter_value = UserTypeChoices.LOCAL.value.lower()
            case UserTypeChoices.LDAP:
                filter_value = UserTypeChoices.LDAP.value.lower()

        return queryset.filter(type=filter_value)