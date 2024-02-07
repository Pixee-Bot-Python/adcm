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


from cm.inventory import HcAclAction
from cm.models import Action, ClusterObject, ServiceComponent
from cm.tests.test_inventory.base import BaseInventoryTestCase


class TestInventoryHcAclActions(BaseInventoryTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.provider_bundle = self.add_bundle(source_dir=self.bundles_dir / "provider")
        cluster_bundle = self.add_bundle(source_dir=self.bundles_dir / "cluster_1")

        self.cluster_1 = self.add_cluster(bundle=cluster_bundle, name="cluster_1")
        self.provider = self.add_provider(bundle=self.provider_bundle, name="provider")
        self.host_1 = self.add_host(
            bundle=self.provider_bundle, provider=self.provider, fqdn="host_1", cluster=self.cluster_1
        )
        self.host_2 = self.add_host(
            bundle=self.provider_bundle, provider=self.provider, fqdn="host_2", cluster=self.cluster_1
        )
        self.service: ClusterObject = self.add_services_to_cluster(
            service_names=["service_two_components"], cluster=self.cluster_1
        ).get()
        self.component_1 = ServiceComponent.objects.get(prototype__name="component_1", service=self.service)
        self.component_2 = ServiceComponent.objects.get(prototype__name="component_2", service=self.service)

        self.hc_acl_action_cluster = Action.objects.get(
            name="hc_acl_action_on_cluster", prototype=self.cluster_1.prototype
        )
        self.hc_acl_action_service = Action.objects.get(
            name="hc_acl_action_on_service", prototype=self.service.prototype
        )

        self.hc_acl_action_component_1 = Action.objects.get(
            name="hc_acl_action_on_component_1", prototype=self.component_1.prototype
        )

        self.initial_hc = [
            {
                "service_id": self.service.pk,
                "component_id": self.component_1.pk,
                "host_id": self.host_1.pk,
            }
        ]
        self.add_hostcomponent_map(cluster=self.cluster_1, hc_map=self.initial_hc)

    def test_expand(self):
        expected_topology = {
            "CLUSTER": [self.host_1.fqdn, self.host_2.fqdn],
            self.service.name: [self.host_1.fqdn, self.host_2.fqdn],
            f"{self.service.name}.{self.component_1.name}": [self.host_1.fqdn],
            f"{self.service.name}.{self.component_2.name}": [self.host_2.fqdn],
            f"{self.service.name}.{self.component_2.name}.{HcAclAction.ADD}": [self.host_2.fqdn],
        }

        expected_data = {
            ("CLUSTER", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            ("CLUSTER", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (self.service.name, "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (self.service.name, "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (f"{self.service.name}.{self.component_1.name}", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (f"{self.service.name}.{self.component_2.name}", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (f"{self.service.name}.{self.component_2.name}.{HcAclAction.ADD}", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            ("vars", "cluster"): (
                self.templates_dir / "cluster.json.j2",
                {
                    "id": self.cluster_1.pk,
                },
            ),
            ("vars", "services"): (
                self.templates_dir / "service_two_components.json.j2",
                {
                    "service_id": self.service.pk,
                    "component_1_id": self.component_1.pk,
                    "component_2_id": self.component_2.pk,
                },
            ),
        }

        hc_map_add = [
            *self.initial_hc,
            {"host_id": self.host_2.pk, "component_id": self.component_2.pk, "service_id": self.service.pk},
        ]

        for obj, action in [
            (self.cluster_1, self.hc_acl_action_cluster),
            (self.service, self.hc_acl_action_service),
            (self.component_1, self.hc_acl_action_component_1),
        ]:
            with self.subTest(
                msg=f"Object: {obj.prototype.type} #{obj.pk} {obj.name}, "
                f"action: {action.name}, action_hc_map: {hc_map_add}"
            ):
                delta = self.get_mapping_delta_for_hc_acl(cluster=self.cluster_1, new_mapping=hc_map_add)
                self.add_hostcomponent_map(cluster=self.cluster_1, hc_map=hc_map_add)

                self.assert_inventory(
                    obj=obj,
                    action=action,
                    expected_topology=expected_topology,
                    expected_data=expected_data,
                    delta=delta,
                )

    def test_shrink(self):
        initial_hc = [
            *self.initial_hc,
            {"service_id": self.service.pk, "component_id": self.component_2.pk, "host_id": self.host_2.pk},
        ]
        self.add_hostcomponent_map(cluster=self.cluster_1, hc_map=initial_hc)

        expected_topology = {
            "CLUSTER": [self.host_1.fqdn, self.host_2.fqdn],
            f"{self.service.name}.{self.component_1.name}": [self.host_1.fqdn],
            self.service.name: [self.host_1.fqdn],
            f"{self.service.name}.{self.component_2.name}.{HcAclAction.REMOVE}": [self.host_2.fqdn],
        }

        expected_data = {
            ("CLUSTER", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            ("CLUSTER", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (self.service.name, "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (f"{self.service.name}.{self.component_1.name}", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (f"{self.service.name}.{self.component_2.name}.{HcAclAction.REMOVE}", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            ("vars", "cluster"): (
                self.templates_dir / "cluster.json.j2",
                {
                    "id": self.cluster_1.pk,
                },
            ),
            ("vars", "services"): (
                self.templates_dir / "service_two_components.json.j2",
                {
                    "service_id": self.service.pk,
                    "component_1_id": self.component_1.pk,
                    "component_2_id": self.component_2.pk,
                },
            ),
        }

        for obj, action in (
            (self.cluster_1, self.hc_acl_action_cluster),
            (self.service, self.hc_acl_action_service),
            (self.component_1, self.hc_acl_action_component_1),
        ):
            with self.subTest(
                msg=f"Object: {obj.prototype.type} #{obj.pk} {obj.name}, "
                f"action: {action.name}, action_hc_map: {self.initial_hc}"
            ):
                delta = self.get_mapping_delta_for_hc_acl(cluster=self.cluster_1, new_mapping=self.initial_hc)
                self.add_hostcomponent_map(cluster=self.cluster_1, hc_map=self.initial_hc)

                self.assert_inventory(
                    obj=obj,
                    action=action,
                    expected_topology=expected_topology,
                    expected_data=expected_data,
                    delta=delta,
                )

    def test_move(self):
        initial_hc = [
            *self.initial_hc,
            {
                "service_id": self.service.pk,
                "component_id": self.component_2.pk,
                "host_id": self.host_2.pk,
            },
        ]
        self.add_hostcomponent_map(cluster=self.cluster_1, hc_map=initial_hc)

        expected_topology = {
            "CLUSTER": [self.host_1.fqdn, self.host_2.fqdn],
            self.service.name: [self.host_1.fqdn, self.host_2.fqdn],
            f"{self.service.name}.{self.component_1.name}": [self.host_2.fqdn],
            f"{self.service.name}.{self.component_2.name}": [self.host_1.fqdn],
            f"{self.service.name}.{self.component_1.name}.{HcAclAction.ADD}": [self.host_2.fqdn],
            f"{self.service.name}.{self.component_2.name}.{HcAclAction.ADD}": [self.host_1.fqdn],
            f"{self.service.name}.{self.component_1.name}.{HcAclAction.REMOVE}": [self.host_1.fqdn],
            f"{self.service.name}.{self.component_2.name}.{HcAclAction.REMOVE}": [self.host_2.fqdn],
        }

        expected_data = {
            ("CLUSTER", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            ("CLUSTER", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (self.service.name, "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (self.service.name, "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (f"{self.service.name}.{self.component_1.name}", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (f"{self.service.name}.{self.component_2.name}", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (f"{self.service.name}.{self.component_1.name}.{HcAclAction.ADD}", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            (f"{self.service.name}.{self.component_2.name}.{HcAclAction.ADD}", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (f"{self.service.name}.{self.component_1.name}.{HcAclAction.REMOVE}", "hosts", self.host_1.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_1.pk,
                },
            ),
            (f"{self.service.name}.{self.component_2.name}.{HcAclAction.REMOVE}", "hosts", self.host_2.fqdn): (
                self.templates_dir / "host.json.j2",
                {
                    "adcm_hostid": self.host_2.pk,
                },
            ),
            ("vars", "cluster"): (
                self.templates_dir / "cluster.json.j2",
                {
                    "id": self.cluster_1.pk,
                },
            ),
            ("vars", "services"): (
                self.templates_dir / "service_two_components.json.j2",
                {
                    "service_id": self.service.pk,
                    "component_1_id": self.component_1.pk,
                    "component_2_id": self.component_2.pk,
                },
            ),
        }

        hc_map_move = [
            {
                "service_id": self.service.pk,
                "component_id": self.component_1.pk,
                "host_id": self.host_2.pk,
            },
            {
                "service_id": self.service.pk,
                "component_id": self.component_2.pk,
                "host_id": self.host_1.pk,
            },
        ]

        for obj, action in [
            (self.cluster_1, self.hc_acl_action_cluster),
            (self.service, self.hc_acl_action_service),
            (self.component_1, self.hc_acl_action_component_1),
        ]:
            with self.subTest(
                msg=f"Object: {obj.prototype.type} #{obj.pk} {obj.name}, "
                f"action: {action.name}, action_hc_map: {hc_map_move}"
            ):
                delta = self.get_mapping_delta_for_hc_acl(cluster=self.cluster_1, new_mapping=hc_map_move)
                self.add_hostcomponent_map(cluster=self.cluster_1, hc_map=hc_map_move)

                self.assert_inventory(
                    obj=obj,
                    action=action,
                    expected_topology=expected_topology,
                    expected_data=expected_data,
                    delta=delta,
                )
