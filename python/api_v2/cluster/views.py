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

from api_v2.cluster.filters import ClusterFilter
from api_v2.cluster.serializers import (
    ClusterGetSerializer,
    ClusterPatchSerializer,
    ClusterPostSerializer,
)
from cm.models import Cluster
from guardian.mixins import PermissionListMixin
from rest_framework.viewsets import ModelViewSet

from adcm.permissions import VIEW_CLUSTER_PERM, DjangoModelPermissionsAudit


class ClusterViewSet(PermissionListMixin, ModelViewSet):  # pylint:disable=too-many-ancestors
    queryset = Cluster.objects.all()
    permission_classes = [DjangoModelPermissionsAudit]
    permission_required = [VIEW_CLUSTER_PERM]
    filterset_class = ClusterFilter

    def get_serializer_class(self):
        if self.action == "create":
            return ClusterPostSerializer

        if self.action == "partial_update":
            return ClusterPatchSerializer

        return ClusterGetSerializer
