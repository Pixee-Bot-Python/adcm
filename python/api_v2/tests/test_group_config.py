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

from api_v2.tests.base import BaseAPITestCase
from cm.models import GroupConfig, Host, ServiceComponent
from django.contrib.contenttypes.models import ContentType
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)


class BaseClusterGroupConfigTestCase(BaseAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.cluster_1_group_config = GroupConfig.objects.create(
            name="group_config",
            object_type=ContentType.objects.get_for_model(self.cluster_1),
            object_id=self.cluster_1.pk,
        )
        self.host_fqdn = "host"
        self.host = self.add_host(bundle=self.provider_bundle, provider=self.provider, fqdn=self.host_fqdn)
        self.cluster_1_group_config.hosts.add(self.host)
        self.new_host_fqdn = "new_host"
        self.new_host = self.add_host(bundle=self.provider_bundle, provider=self.provider, fqdn=self.new_host_fqdn)
        self.add_host_to_cluster(cluster=self.cluster_1, host=self.new_host)


class BaseServiceGroupConfigTestCase(BaseClusterGroupConfigTestCase):  # pylint: disable=too-many-ancestors
    def setUp(self) -> None:
        super().setUp()

        self.service_1 = self.add_service_to_cluster(service_name="service_1", cluster=self.cluster_1)
        self.service_1_group_config = GroupConfig.objects.create(
            name="service_1_group_config",
            object_type=ContentType.objects.get_for_model(self.service_1),
            object_id=self.service_1.pk,
        )
        self.service_1_group_config.hosts.add(self.host)
        self.host_for_service = self.add_host(
            bundle=self.provider_bundle, provider=self.provider, fqdn="host_for_service"
        )
        self.add_host_to_cluster(cluster=self.cluster_1, host=self.host_for_service)

        self.component_1 = ServiceComponent.objects.get(
            cluster=self.cluster_1, service=self.service_1, prototype__name="component_1"
        )
        self.add_hostcomponent_map(
            cluster=self.cluster_1,
            hc_map=[
                {
                    "host_id": self.host_for_service.pk,
                    "service_id": self.service_1.pk,
                    "component_id": self.component_1.pk,
                }
            ],
        )


class TestClusterGroupConfig(BaseClusterGroupConfigTestCase):  # pylint: disable=too-many-ancestors
    def test_list_success(self):
        response = self.client.get(
            path=reverse(viewname="v2:cluster-group-config-list", kwargs={"cluster_pk": self.cluster_1.pk})
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.cluster_1_group_config.pk)

    def test_retrieve_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:cluster-group-config-detail",
                kwargs={"cluster_pk": self.cluster_1.pk, "pk": self.cluster_1_group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.cluster_1_group_config.pk)

    def test_create_success(self):
        response = self.client.post(
            path=reverse(viewname="v2:cluster-group-config-list", kwargs={"cluster_pk": self.cluster_1.pk}),
            data={"name": "group-config-new", "description": "group-config-new"},
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], "group-config-new")

    def test_delete_success(self):
        response = self.client.delete(
            path=reverse(
                viewname="v2:cluster-group-config-detail",
                kwargs={"cluster_pk": self.cluster_1.pk, "pk": self.cluster_1_group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_list_hosts_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:cluster-group-config-hosts-list",
                kwargs={"cluster_pk": self.cluster_1.pk, "group_config_pk": self.cluster_1_group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_add_hosts_success(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:cluster-group-config-hosts-list",
                kwargs={"cluster_pk": self.cluster_1.pk, "group_config_pk": self.cluster_1_group_config.pk},
            ),
            data=[self.new_host.pk],
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.new_host.name)

    def test_host_candidates(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:cluster-group-config-host-candidates",
                kwargs={"cluster_pk": self.cluster_1.pk, "pk": self.cluster_1_group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.new_host.name)

    def test_delete_host_success(self):
        response = self.client.delete(
            path=reverse(
                "v2:cluster-group-config-hosts-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "group_config_pk": self.cluster_1_group_config.pk,
                    "pk": self.host.pk,
                },
            ),
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(self.host, Host.objects.get(id=self.host.pk))
        self.assertNotIn(self.host, self.cluster_1_group_config.hosts.all())


class TestServiceGroupConfig(BaseServiceGroupConfigTestCase):  # pylint: disable=too-many-ancestors
    def test_list_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:service-group-config-list",
                kwargs={"cluster_pk": self.cluster_1.pk, "service_pk": self.service_1.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.service_1_group_config.pk)

    def test_retrieve_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:service-group-config-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "pk": self.service_1_group_config.pk,
                },
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.service_1_group_config.pk)

    def test_create_success(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:service-group-config-list",
                kwargs={"cluster_pk": self.cluster_1.pk, "service_pk": self.service_1.pk},
            ),
            data={"name": "service-group-config-new", "description": "service-group-config-new"},
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], "service-group-config-new")

    def test_delete_success(self):
        response = self.client.delete(
            path=reverse(
                viewname="v2:service-group-config-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "pk": self.service_1_group_config.pk,
                },
            )
        )
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

        response = self.client.get(
            path=reverse(
                viewname="v2:service-group-config-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "pk": self.service_1_group_config.pk,
                },
            )
        )
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_list_hosts_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:service-group-config-hosts-list",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "group_config_pk": self.service_1_group_config.pk,
                },
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.host.name)

    def test_add_hosts_success(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:service-group-config-hosts-list",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "group_config_pk": self.service_1_group_config.pk,
                },
            ),
            data=[self.host_for_service.pk],
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.host_for_service.name)

    def test_delete_host_success(self):
        response = self.client.delete(
            path=reverse(
                "v2:service-group-config-hosts-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "group_config_pk": self.service_1_group_config.pk,
                    "pk": self.host.pk,
                },
            ),
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(self.host, Host.objects.get(id=self.host.pk))
        self.assertIn(self.host, self.cluster_1_group_config.hosts.all())
        self.assertNotIn(self.host, self.service_1_group_config.hosts.all())

    def test_host_candidates_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:service-group-config-host-candidates",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "pk": self.service_1_group_config.pk,
                },
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.host_for_service.name)


class TestComponentGroupConfig(BaseServiceGroupConfigTestCase):  # pylint: disable=too-many-ancestors
    def setUp(self) -> None:
        super().setUp()

        self.component_1_group_config = GroupConfig.objects.create(
            name="component_1_group_config",
            object_type=ContentType.objects.get_for_model(self.component_1),
            object_id=self.component_1.pk,
        )
        self.component_1_group_config.hosts.add(self.host)

        self.host_for_component = self.add_host(
            bundle=self.provider_bundle, provider=self.provider, fqdn="host_for_component"
        )
        self.add_host_to_cluster(cluster=self.cluster_1, host=self.host_for_component)
        self.add_hostcomponent_map(
            cluster=self.cluster_1,
            hc_map=[
                {
                    "host_id": self.host_for_component.pk,
                    "service_id": self.service_1.pk,
                    "component_id": self.component_1.pk,
                }
            ],
        )

    def test_list_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:component-group-config-list",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                },
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.component_1_group_config.pk)

    def test_retrieve_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:component-group-config-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "pk": self.component_1_group_config.pk,
                },
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.component_1_group_config.pk)

    def test_create_success(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:component-group-config-list",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                },
            ),
            data={"name": "component-group-config-new", "description": "component-group-config-new"},
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], "component-group-config-new")

    def test_delete_success(self):
        response = self.client.delete(
            path=reverse(
                viewname="v2:component-group-config-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "pk": self.component_1_group_config.pk,
                },
            )
        )
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

        response = self.client.get(
            path=reverse(
                viewname="v2:component-group-config-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "pk": self.component_1_group_config.pk,
                },
            )
        )
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_list_hosts(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:component-group-config-hosts-list",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "group_config_pk": self.component_1_group_config.pk,
                },
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.host.name)

    def test_add_hosts_group_config_not_found_fail(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:component-group-config-hosts-list",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "group_config_pk": self.component_1_group_config.pk + 1000,
                },
            ),
            data=[self.host_for_component.pk],
        )

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_add_hosts_success(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:component-group-config-hosts-list",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "group_config_pk": self.component_1_group_config.pk,
                },
            ),
            data=[self.host_for_component.pk],
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.host_for_component.name)

    def test_list_host_candidates_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:component-group-config-host-candidates",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "pk": self.component_1_group_config.pk,
                },
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], self.host_for_component.name)

    def test_delete_host_success(self):
        response = self.client.delete(
            path=reverse(
                "v2:component-group-config-hosts-detail",
                kwargs={
                    "cluster_pk": self.cluster_1.pk,
                    "service_pk": self.service_1.pk,
                    "component_pk": self.component_1.pk,
                    "group_config_pk": self.component_1_group_config.pk,
                    "pk": self.host.pk,
                },
            ),
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(self.host, Host.objects.get(id=self.host.pk))
        self.assertIn(self.host, self.cluster_1_group_config.hosts.all())
        self.assertIn(self.host, self.service_1_group_config.hosts.all())
        self.assertNotIn(self.host, self.component_1_group_config.hosts.all())


class TestHostProviderGroupConfig(BaseAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.host = self.add_host(bundle=self.provider_bundle, provider=self.provider, fqdn="host")
        self.new_host = self.add_host(bundle=self.provider_bundle, provider=self.provider, fqdn="new-host")
        self.group_config = GroupConfig.objects.create(
            name="group_config",
            object_type=ContentType.objects.get_for_model(self.provider),
            object_id=self.provider.pk,
        )
        self.group_config.hosts.add(self.host)

    def test_list_success(self):
        response = self.client.get(
            path=reverse(viewname="v2:hostprovider-group-config-list", kwargs={"hostprovider_pk": self.provider.pk})
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"],
            [{"description": "", "hosts": [{"id": 1, "name": "host"}], "id": 1, "name": "group_config"}],
        )

    def test_retrieve_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:hostprovider-group-config-detail",
                kwargs={"hostprovider_pk": self.provider.pk, "pk": self.group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertDictEqual(
            response.json(), {"description": "", "hosts": [{"id": 1, "name": "host"}], "id": 1, "name": "group_config"}
        )

    def test_create_success(self):
        response = self.client.post(
            path=reverse(viewname="v2:hostprovider-group-config-list", kwargs={"hostprovider_pk": self.provider.pk}),
            data={"name": "group-config-new", "description": "group config new"},
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertDictEqual(
            response.json(), {"description": "group config new", "hosts": [], "id": 2, "name": "group-config-new"}
        )

    def test_delete_success(self):
        response = self.client.delete(
            path=reverse(
                viewname="v2:hostprovider-group-config-detail",
                kwargs={"hostprovider_pk": self.provider.pk, "pk": self.group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_list_hosts_success(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:hostprovider-group-config-hosts-list",
                kwargs={"hostprovider_pk": self.provider.pk, "group_config_pk": self.group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertListEqual(response.json(), [{"id": 1, "name": "host"}])

    def test_add_hosts_success(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:hostprovider-group-config-hosts-list",
                kwargs={"hostprovider_pk": self.provider.pk, "group_config_pk": self.group_config.pk},
            ),
            data=[self.new_host.pk],
        )

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertListEqual(response.json(), [{"id": 2, "name": "new-host"}])

    def test_add_hosts_fail(self):
        response = self.client.post(
            path=reverse(
                viewname="v2:hostprovider-group-config-hosts-list",
                kwargs={"hostprovider_pk": self.provider.pk, "group_config_pk": self.group_config.pk},
            ),
            data=[self.host.pk],
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {
                "code": "GROUP_CONFIG_HOST_EXISTS",
                "desc": "the host is already a member of this group ",
                "level": "error",
            },
        )

    def test_host_candidates(self):
        response = self.client.get(
            path=reverse(
                viewname="v2:hostprovider-group-config-host-candidates",
                kwargs={"hostprovider_pk": self.provider.pk, "pk": self.group_config.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertListEqual(response.json(), [{"id": 2, "name": "new-host"}])

    def test_delete_host_success(self):
        response = self.client.delete(
            path=reverse(
                viewname="v2:hostprovider-group-config-hosts-detail",
                kwargs={"hostprovider_pk": self.provider, "group_config_pk": self.group_config.pk, "pk": self.host.pk},
            )
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertNotIn(self.host, self.group_config.hosts.all())
