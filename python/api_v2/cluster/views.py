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
    HostComponentListSerializer,
    HostComponentPostSerializer,
    ServicePrototypeSerializer,
)
from api_v2.host.serializers import HostMappingSerializer
from api_v2.service_component.serializers import ServiceComponentSerializer
from cm.models import Cluster, HostComponent, ObjectType, Prototype
from guardian.mixins import PermissionListMixin
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from adcm.permissions import VIEW_CLUSTER_PERM, DjangoModelPermissionsAudit


class ClusterViewSet(PermissionListMixin, ModelViewSet):  # pylint:disable=too-many-ancestors
    queryset = Cluster.objects.all()
    serializer_class = ClusterGetSerializer
    permission_classes = [DjangoModelPermissionsAudit]
    permission_required = [VIEW_CLUSTER_PERM]
    filterset_class = ClusterFilter

    def get_serializer_class(self):
        if self.action == "create":
            return ClusterPostSerializer

        if self.action == "partial_update":
            return ClusterPatchSerializer

        if self.action == "service_prototypes":
            return ServicePrototypeSerializer

        return self.serializer_class

    @action(methods=["get"], detail=True)
    def service_prototypes(self, request: Request, *args, **kwargs) -> Response:  # pylint: disable=unused-argument
        cluster = Cluster.objects.filter(pk=kwargs["pk"]).first()
        if not cluster:
            return Response(data=f'Cluster with pk "{kwargs["pk"]}" not found', status=HTTP_404_NOT_FOUND)

        prototypes = Prototype.objects.filter(type=ObjectType.SERVICE, bundle=cluster.prototype.bundle)
        serializer = self.get_serializer_class()(instance=prototypes, many=True)

        return Response(data=serializer.data)


class MappingViewSet(  # pylint:disable=too-many-ancestors
    PermissionListMixin,
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
):
    queryset = HostComponent.objects.all()
    serializer_class = HostComponentListSerializer
    permission_classes = [DjangoModelPermissionsAudit]
    permission_required = ["cm.view_hostcomponent"]

    def get_serializer_class(self):
        if self.action == "create":
            return HostComponentPostSerializer

        return self.serializer_class

    def list(self, request: Request, *args, **kwargs) -> Response:
        cluster = Cluster.objects.filter(pk=kwargs["cluster_pk"]).first()
        if not cluster:
            return Response(data=f'Cluster with pk "{kwargs["cluster_pk"]}" not found', status=HTTP_404_NOT_FOUND)

        self.queryset = self.queryset.filter(cluster_id=cluster.pk)

        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        cluster = Cluster.objects.filter(pk=kwargs["cluster_pk"]).first()
        if not cluster:
            return Response(data=f'Cluster with pk "{kwargs["cluster_pk"]}" not found', status=HTTP_404_NOT_FOUND)

        request.data["cluster"] = cluster.pk

        return super().create(request, *args, **kwargs)

    @action(methods=["get"], detail=False)
    def hosts(self, request: Request, *args, **kwargs) -> Response:  # pylint: disable=unused-argument
        cluster = Cluster.objects.filter(pk=kwargs["cluster_pk"]).first()
        if not cluster:
            return Response(data=f'Cluster with pk "{kwargs["cluster_pk"]}" not found', status=HTTP_404_NOT_FOUND)

        serializer = HostMappingSerializer(
            instance=[service_component.host for service_component in self.queryset.filter(cluster_id=cluster.pk)],
            many=True,
        )

        return Response(data=serializer.data)

    @action(methods=["get"], detail=False)
    def components(self, request: Request, *args, **kwargs) -> Response:  # pylint: disable=unused-argument
        cluster = Cluster.objects.filter(pk=kwargs["cluster_pk"]).first()
        if not cluster:
            return Response(data=f'Cluster with pk "{kwargs["cluster_pk"]}" not found', status=HTTP_404_NOT_FOUND)

        serializer = ServiceComponentSerializer(
            instance=[service_component.component for service_component in self.queryset.filter(cluster_id=cluster.pk)],
            many=True,
        )

        return Response(data=serializer.data)