"""Checks and utilities for action roles"""
from operator import itemgetter
from typing import Iterable, Tuple, Set, List, Iterator

import allure
from adcm_client.base import ObjectNotFound
from adcm_client.objects import ADCMClient, Cluster, Prototype, Service, Role, Bundle
from adcm_pytest_plugin.utils import catch_failed

from tests.functional.rbac.conftest import RbacRoles, extract_role_short_info, RoleShortInfo, RoleType
from tests.library.assertions import is_in_collection, is_not_in_collection, is_superset_of, does_not_intersect


# !===== Utils =====!


def get_prototype_prefix_for_action_role(prototype: Prototype) -> str:
    """Get prototype based prefix for role name"""
    return f'{prototype.type}_{prototype.display_name}_'


def get_bundle_prefix_for_role_name(bundle: Bundle) -> str:
    """Get Bundle based prefix for role name"""
    return f'{bundle.name}_{bundle.version}_{bundle.edition}_'


# !===== Checks =====!


@allure.step('Check that roles are created for each action in cluster')
def check_cluster_actions_roles_are_created_correctly(
    client: ADCMClient,
    cluster: Cluster,
    hidden_role_names: set,
    hidden_role_prefix: str,
):
    """
    Check that all cluster action roles have corresponding hidden roles,
    that roles are bonded to correct business role,
    and the business role is assigned to correct default RBAC roles.
    """
    cluster_proto = cluster.prototype()
    actions = cluster_proto.actions
    full_hidden_prefix = f'{hidden_role_prefix}{get_prototype_prefix_for_action_role(cluster_proto)}'
    with allure.step('Check that "hidden" roles are created for each action in cluster'):
        cluster_actions_role_names = get_actions_role_names(full_hidden_prefix, actions)
        is_superset_of(hidden_role_names, cluster_actions_role_names, 'Not all expected "hidden" roles were found')
    _, business = check_business_roles_children(client, cluster_proto, actions, cluster_actions_role_names)

    with allure.step('Check that business roles are applied correctly to RBAC default roles'):
        business_roles_ids = get_roles_ids_from_info(business)
        check_roles_are_added_to_rbac_roles(
            client,
            rbac_roles=(RbacRoles.ClusterAdministrator,),
            children_roles_ids=business_roles_ids,
        )

    check_all_roles_have_category(cluster_proto.display_name, business)


def check_service_and_components_roles_are_created_correctly(
    client: ADCMClient,
    service: Service,
    hidden_role_names: set,
    hidden_role_prefix: str,
):
    """
    Check that all service and component action roles have corresponding hidden roles,
    that roles are bonded to correct business role,
    and the business role is assigned to correct default RBAC roles.
    """
    expected_parent_roles = (
        RbacRoles.ClusterAdministrator,
        RbacRoles.ServiceAdministrator,
    )

    with allure.step(
        f'Check that all required roles are created for service "{service.display_name}" and its components'
    ):
        service_proto = service.prototype()
        service_actions = service_proto.actions
        service_full_hidden_prefix = f'{hidden_role_prefix}{get_prototype_prefix_for_action_role(service_proto)}'

        with allure.step('Check that "hidden" roles are created for each action in service'):
            service_actions_role_names = get_actions_role_names(service_full_hidden_prefix, service_actions)
            is_superset_of(
                hidden_role_names, service_actions_role_names, "Some of required roles weren't created for service"
            )

        _, business = check_business_roles_children(client, service_proto, service_actions, service_actions_role_names)

        check_roles_are_added_to_rbac_roles(client, expected_parent_roles, get_roles_ids_from_info(business))

        check_all_roles_have_category(service.cluster().prototype().display_name, business)

        _check_components_roles_are_created_correctly(
            client,
            service,
            hidden_role_names,
            prefix_for_component=f'{hidden_role_prefix}{service_proto.type}_{service_proto.name}_',
        )


@allure.step(
    'Check that "hidden" roles are created for each action in each component in service '
    'and that they are correctly connected to corresponding business roles'
)
def _check_components_roles_are_created_correctly(client, service, hidden_role_names, prefix_for_component: str):
    """Check that component action roles are created correctly"""
    expected_parent_roles = (
        RbacRoles.ClusterAdministrator,
        RbacRoles.ServiceAdministrator,
    )
    component_business_roles = set()

    for component in service.component_list():
        component_proto = component.prototype()
        component_actions = component_proto.actions
        component_actions_role_names = get_actions_role_names(
            f'{prefix_for_component}{get_prototype_prefix_for_action_role(component_proto)}', component_actions
        )
        is_superset_of(hidden_role_names, component_actions_role_names, 'Not all roles were created')

        _, business = check_business_roles_children(
            client, component_proto, component_actions, component_actions_role_names
        )
        component_business_roles.update(business)

    check_roles_are_added_to_rbac_roles(
        client, expected_parent_roles, get_roles_ids_from_info(component_business_roles)
    )

    check_all_roles_have_category(service.cluster().prototype().display_name, component_business_roles)


def check_provider_based_object_action_roles_are_created_correctly(
    prototype: Prototype, client: ADCMClient, hidden_role_names, hidden_role_prefix: str
):
    """
    Check that all provider/host action roles have corresponding hidden roles,
    that roles are bonded to correct business role,
    and the business role is not assigned to any default RBAC role.
    """
    actions = prototype.actions
    full_hidden_prefix = f'{hidden_role_prefix}{get_prototype_prefix_for_action_role(prototype)}'

    with allure.step(f'Check that "hidden" roles are created for each action in {prototype.type}'):
        actions_role_names = get_actions_role_names(full_hidden_prefix, actions)
        is_superset_of(hidden_role_names, actions_role_names, 'Not all expected "hidden" roles were found')

    _, business = check_business_roles_children(client, prototype, actions, actions_role_names)

    check_roles_are_not_added_to_rbac_roles(
        client, (RbacRoles.ClusterAdministrator, RbacRoles.ServiceAdministrator, RbacRoles.ADCMUser), business
    )


@allure.step('Check that "business" roles was created with all required children')
def check_business_roles_children(
    client: ADCMClient, prototype: Prototype, actions: List[dict], actions_role_names: List[str]
) -> Tuple[Set[RoleShortInfo], Set[RoleShortInfo]]:
    """
    Checks that "action" business roles have all newly created roles as its children.
    :returns: hidden and business roles as ShortRoleInfo set
    """
    hidden_roles = set()
    business_roles = set()
    for action_display_name, hidden_role_name in zip(key_values_from('display_name', actions), actions_role_names):
        business_role_name = f'{prototype.type.capitalize()} Action: {action_display_name}'
        with allure.step(f'Check role "{hidden_role_name}" is a child of "{business_role_name}"'):
            with catch_failed(ObjectNotFound, f'There should be a hidden role with name "{hidden_role_name}"'):
                hidden_role = client.role(name=hidden_role_name, type=RoleType.HIDDEN.value)
            with catch_failed(ObjectNotFound, f'There should be a business role with name "{business_role_name}"'):
                business_role = client.role(name=business_role_name, type=RoleType.BUSINESS.value)
            is_in_collection(
                hidden_role.id,
                (child.id for child in business_role.child_list()),
                f"Role wasn't found in children of '{hidden_role.name}'",
            )
        hidden_roles.add(extract_role_short_info(hidden_role))
        business_roles.add(extract_role_short_info(business_role))
    return hidden_roles, business_roles


@allure.step('Check that business roles are applied correctly to RBAC default roles')
def check_roles_are_added_to_rbac_roles(
    client: ADCMClient, rbac_roles: Iterable[RbacRoles], children_roles_ids: Set[int]
):
    """Check that all given RBAC default roles have all given roles as its children"""
    for rbac_role in rbac_roles:
        with allure.step(f'Check roles were added to role "{rbac_role.value}"'):
            role: Role = client.role(name=rbac_role.value)
            is_superset_of(
                set(r.id for r in role.child_list()),
                children_roles_ids,
                'One or more roles not found (by id) in the child list',
            )


@allure.step("Check that business roles aren't applied to RBAC default roles")
def check_roles_are_not_added_to_rbac_roles(
    client: ADCMClient, rbac_roles: Iterable[RbacRoles], children_roles_ids: Set[int]
):
    """Check that all given RBAC default roles doesn't have all given roles as its children"""
    for rbac_role in rbac_roles:
        with allure.step(f"Check roles weren't added to role '{rbac_role.value}'"):
            role: Role = client.role(name=rbac_role.value)
            does_not_intersect(
                set(r.id for r in role.child_list()),
                children_roles_ids,
                'One or more roles was found (by id) in the child list',
            )


@allure.step('Check roles have category "{category}"')
def check_all_roles_have_category(category: str, roles: Iterable[RoleShortInfo]):
    """Check that category is presented in each role"""
    for role in roles:
        with allure.step(f'Check if role "{role.name}" have category "{category}"'):
            is_in_collection(category, role.categories)


@allure.step("Check roles doesn't have category '{category}'")
def check_roles_does_not_have_category(category: str, roles: Iterable[RoleShortInfo]):
    """Check that category is not presented in each role"""
    for role in roles:
        with allure.step(f'Check if role "{role.name}" does not have category "{category}"'):
            is_not_in_collection(category, role.categories)


# !===== Helpers =====!


def key_values_from(key, collection: Iterable[dict]) -> Iterator:
    """Create generator with value of given key from each collection item"""
    return map(itemgetter(key), collection)


def get_roles_of_type(role_type: RoleType, client: ADCMClient):
    """Get first 200 roles with given type"""
    return client.role_list(type=role_type.value, paging={'limit': 200})


def get_actions_role_names(full_role_prefix: str, action_names: List[dict]) -> List[str]:
    """full_role_prefix is prefix with "prototype" prefix and others (only without action name in it)"""
    return [f'{full_role_prefix}{name}' for name in key_values_from('name', action_names)]


def get_roles_ids_from_info(roles_short_info: Iterable[RoleShortInfo]) -> Set[int]:
    """Extract values of "id" field from RoleShortInfo's to set of integers"""
    return {role.id for role in roles_short_info}
