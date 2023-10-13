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
from api.job.views import VIEW_JOBLOG_PERMISSION
from api_v2.job.serializers import JobRetrieveSerializer
from api_v2.task.serializers import JobListSerializer
from api_v2.views import CamelCaseGenericViewSet
from cm.models import JobLog
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from adcm.permissions import check_custom_perm, get_object_for_user


class JobViewSet(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin, CamelCaseGenericViewSet
):  # pylint: disable=too-many-ancestors
    queryset = JobLog.objects.select_related("task__action").order_by("pk")
    serializer_class = JobListSerializer
    filter_backends = []

    def get_serializer_class(self):
        if self.action == "retrieve":
            return JobRetrieveSerializer

        return super().get_serializer_class()

    @action(methods=["post"], detail=True)
    def terminate(self, request: Request, pk: int) -> Response:
        job: JobLog = get_object_for_user(request.user, VIEW_JOBLOG_PERMISSION, JobLog, id=pk)
        check_custom_perm(request.user, "change", JobLog, pk)

        job.cancel()

        return Response(status=HTTP_200_OK)
