import { configureStore, combineReducers } from '@reduxjs/toolkit';
import authSlice from '@store/authSlice';
import notificationsSlice from '@store/notificationsSlice';
import clustersSlice from '@store/adcm/clusters/clustersSlice';
import clustersDynamicActionsSlice from '@store/adcm/clusters/clustersDynamicActionsSlice';
import clusterUpgradesSlice from '@store/adcm/clusters/clusterUpgradesSlice';
import clusterHostsSlice from '@store/adcm/cluster/hosts/hostsSlice';
import clusterHostsTableSlice from '@store/adcm/cluster/hosts/hostsTableSlice';
import clusterHostsActionsSlice from '@store/adcm/cluster/hosts/hostsActionsSlice';
import clusterHostsDynamicActionsSlice from '@store/adcm/cluster/hosts/hostsDynamicActionsSlice';
import hostComponentsDynamicActionsSlice from '@store/adcm/cluster/hosts/host/hostComponentsDynamicActionsSlice';
import clustersTableSlice from '@store/adcm/clusters/clustersTableSlice';
import clusterConfigGroupsSlice from '@store/adcm/cluster/configGroups/clusterConfigGroupsSlice';
import clusterConfigGroupsTableSlice from '@store/adcm/cluster/configGroups/clusterConfigGroupsTableSlice';
import clusterConfigGroupActionsSlice from '@store/adcm/cluster/configGroups/clusterConfigGroupActionsSlice';
import clusterConfigGroupSlice from '@store/adcm/cluster/configGroupSingle/clusterConfigGroup';
import hostProviderConfigGroupsSlice from '@store/adcm/hostProvider/configurationGroups/hostProviderConfigGroupsSlice';
import hostProviderConfigGroupsTableSlice from '@store/adcm/hostProvider/configurationGroups/hostProviderConfigGroupsTableSlice';
import bundlesSlice from '@store/adcm/bundles/bundlesSlice';
import bundleSlice from '@store/adcm/bundle/bundleSlice';
import bundlesTableSlice from '@store/adcm/bundles/bundlesTableSlice';
import clusterMappingSlice from '@store/adcm/cluster/mapping/mappingSlice';
import breadcrumbsSlice from '@store/adcm/breadcrumbs/breadcrumbsSlice';
import hostProvidersSlice from '@store/adcm/hostProviders/hostProvidersSlice';
import hostProvidersTableSlice from '@store/adcm/hostProviders/hostProvidersTableSlice';
import createHostProviderDialogSlice from '@store/adcm/hostProviders/dialogs/createHostProviderDialogSlice';
import hostsTableSlice from '@store/adcm/hosts/hostsTableSlice';
import hostsSlice from '@store/adcm/hosts/hostsSlice';
import hostsActionsSlice from '@store/adcm/hosts/hostsActionsSlice';
import serviceSlice from '@store/adcm/services/serviceSlice';
import auditOperationsSlice from '@store/adcm/audit/auditOperations/auditOperationsSlice';
import auditOperationsTableSlice from '@store/adcm/audit/auditOperations/auditOperationsTableSlice';
import auditLoginsSlice from '@store/adcm/audit/auditLogins/auditLoginsSlice';
import auditLoginsTableSlice from '@store/adcm/audit/auditLogins/auditLoginsTableSlice';
import clusterImportsSlice from '@store/adcm/cluster/imports/cluster/clusterImportsSlice';
import clusterImportsFilterSlice from '@store/adcm/cluster/imports/cluster/clusterImportsFilterSlice';
import clusterImportsServiceSlice from '@store/adcm/cluster/imports/service/clusterImportsServiceSlice';
import clusterImportsServiceFilterSlice from '@store/adcm/cluster/imports/service/clusterImportsServiceFilterSlice';
import clusterOverviewServicesSlice from '@store/adcm/cluster/overview/overviewServicesSlice';
import clusterOverviewHostsSlice from '@store/adcm/cluster/overview/overviewHostsSlice';
import clusterOverviewServicesTableSlice from '@store/adcm/cluster/overview/overviewServicesTableSlice';
import clusterOverviewHostsTableSlice from '@store/adcm/cluster/overview/overviewHostsTableSlice';

// eslint-disable-next-line import/no-cycle
import { apiMiddleware } from './middlewares/apiMiddleware';
// eslint-disable-next-line import/no-cycle
import { wsMiddleware } from './middlewares/wsMiddeware';
import clusterSlice from './adcm/clusters/clusterSlice';
import usersSlice from './adcm/users/usersSlice';
import usersTableSlice from './adcm/users/usersTableSlice';
import servicesSlice from './adcm/cluster/services/servicesSlice';
import servicesTableSlice from './adcm/cluster/services/servicesTableSlice';
import servicesActionsSlice from './adcm/cluster/services/servicesActionsSlice';
import servicesDynamicActionsSlice from './adcm/cluster/services/servicesDynamicActionsSlice';
import serviceComponentsSlice from './adcm/cluster/services/serviceComponents/serviceComponentsSlice';
import serviceComponentsTableSlice from './adcm/cluster/services/serviceComponents/serviceComponentsTableSlice';
import usersActionsSlice from './adcm/users/usersActionsSlice';
import jobsSlice from './adcm/jobs/jobsSlice';
import jobsTableSlice from './adcm/jobs/jobsTableSlice';
import jobsActionsSlice from './adcm/jobs/jobsActionsSlice';
import groupsSlice from './adcm/groups/groupsSlice';
import groupsTableSlice from './adcm/groups/groupsTableSlice';
import groupsActionsSlice from './adcm/groups/groupActionsSlice';
import policiesTableSlice from './adcm/policies/policiesTableSlice';
import policiesSlice from './adcm/policies/policiesSlice';
import policiesActionsSlice from './adcm/policies/policiesActionsSlice';
import rolesSlice from './adcm/roles/rolesSlice';
import rolesTableSlice from './adcm/roles/rolesTableSlice';
import rolesActionsSlice from './adcm/roles/rolesActionsSlice';
import serviceComponentsActionsSlice from './adcm/cluster/services/serviceComponents/serviceComponentsActionsSlice';
import serviceComponentSlice from './adcm/cluster/services/serviceComponents/serviceComponent/serviceComponentSlice';
import serviceComponentConfigGroupsSlice from './adcm/cluster/services/serviceComponents/serviceComponent/configGroups/serviceComponentConfigGroupsSlice';
import serviceComponentConfigGroupsTableSlice from './adcm/cluster/services/serviceComponents/serviceComponent/configGroups/serviceComponentConfigGroupsTableSlice';
import serviceComponentConfigGroupsActionsSlice from './adcm/cluster/services/serviceComponents/serviceComponent/configGroups/serviceComponentConfigGroupsActionsSlice';
import serviceComponentConfigGroupSingleSlice from './adcm/cluster/services/serviceComponents/serviceComponent/configGroupSingle/serviceComponentConfigGroupSingleSlice';

import clustersActionsSlice from './adcm/clusters/clustersActionsSlice';
import clusterHostSlice from './adcm/cluster/hosts/host/clusterHostSlice';
import hostComponentsTableSlice from './adcm/hostComponents/hostComponentsTableSlice';
import hostComponentsSlice from './adcm/hostComponents/hostComponentsSlice';
import profileSlice from './adcm/profile/profileSlice';
import hostsDynamicActionsSlice from './adcm/hosts/hostsDynamicActionsSlice';
import hostProviderSlice from './adcm/hostProviders/hostProviderSlice';
import hostProvidersActionsSlice from './adcm/hostProviders/hostProvidersActionsSlice';
import hostProvidersDynamicActionsSlice from './adcm/hostProviders/hostProvidersDynamicActionsSlice';
import hostProviderUpgradesSlice from './adcm/hostProviders/hostProviderUpgradesSlice';
import serviceComponentsDynamicActionsSlice from './adcm/cluster/services/serviceComponents/serviceComponentsDynamicActionsSlice';
import hostSlice from './adcm/host/hostSlice';
import serviceConfigGroupsSlice from './adcm/cluster/services/configGroups/serviceConfigGroupsSlice.ts';
import serviceConfigGroupsTableSlice from './adcm/cluster/services/configGroups/serviceConfigGroupsTableSlice.ts';
import serviceConfigGroupsActionsSlice from './adcm/cluster/services/configGroups/serviceConfigGroupsActionsSlice.ts';
import serviceConfigGroupSlice from './adcm/cluster/services/configGroupSingle/configGroupSingle.ts';
import hostProviderConfigGroupActionsSlice from '@store/adcm/hostProvider/configurationGroups/hostProviderConfigGroupActionsSlice';
import hostProviderConfigGroupSlice from '@store/adcm/hostProvider/configurationGroupSingle/hostProviderConfigGroupSlice';
import bellSlice from '@store/adcm/bell/bellSlice';
import adcmSettingsSlice from '@store/adcm/settings/settingsSlice';
import adcmSettingsDynamicActionsSlice from '@store/adcm/settings/settingsDynamicActionsSlice';
import bundlesActionsSlice from './adcm/bundles/bundlesActionsSlice.ts';

import adcmEntityConfigurationSlice from '@store/adcm/entityConfiguration/configurationSlice.ts';
import adcmEntityConfigurationCompareSlice from '@store/adcm/entityConfiguration/compareSlice.ts';

const rootReducer = combineReducers({
  auth: authSlice,
  notifications: notificationsSlice,
  adcm: combineReducers({
    cluster: clusterSlice,
    clusters: clustersSlice,
    clustersActions: clustersActionsSlice,
    clustersDynamicActions: clustersDynamicActionsSlice,
    clusterUpgrades: clusterUpgradesSlice,
    clustersTable: clustersTableSlice,
    clusterHosts: clusterHostsSlice,
    clusterHost: clusterHostSlice,
    clusterHostsActions: clusterHostsActionsSlice,
    clusterHostsDynamicActions: clusterHostsDynamicActionsSlice,
    hostComponentsDynamicActions: hostComponentsDynamicActionsSlice,
    clusterHostsTable: clusterHostsTableSlice,
    clusterMapping: clusterMappingSlice,
    clusterConfigGroups: clusterConfigGroupsSlice,
    clusterConfigGroupsTable: clusterConfigGroupsTableSlice,
    clusterConfigGroupActions: clusterConfigGroupActionsSlice,
    clusterConfigGroup: clusterConfigGroupSlice,
    bundle: bundleSlice,
    bundles: bundlesSlice,
    bundlesActions: bundlesActionsSlice,
    bundlesTable: bundlesTableSlice,
    breadcrumbs: breadcrumbsSlice,
    hostComponents: hostComponentsSlice,
    hostComponentsTable: hostComponentsTableSlice,
    hostProvider: hostProviderSlice,
    hostProviderConfigGroupActions: hostProviderConfigGroupActionsSlice,
    hostProviderConfigGroups: hostProviderConfigGroupsSlice,
    hostProviderConfigGroupsTable: hostProviderConfigGroupsTableSlice,
    hostProviderConfigGroup: hostProviderConfigGroupSlice,
    hostProviders: hostProvidersSlice,
    hostProvidersActions: hostProvidersActionsSlice,
    hostProvidersTable: hostProvidersTableSlice,
    hostProvidersDynamicActions: hostProvidersDynamicActionsSlice,
    hostProviderUpgrades: hostProviderUpgradesSlice,
    hostsDynamicActions: hostsDynamicActionsSlice,
    createHostProviderDialog: createHostProviderDialogSlice,
    hosts: hostsSlice,
    host: hostSlice,
    hostsTable: hostsTableSlice,
    hostsActions: hostsActionsSlice,
    service: serviceSlice,
    services: servicesSlice,
    servicesTable: servicesTableSlice,
    servicesActions: servicesActionsSlice,
    servicesDynamicActions: servicesDynamicActionsSlice,
    serviceConfigGroups: serviceConfigGroupsSlice,
    serviceConfigGroupsTable: serviceConfigGroupsTableSlice,
    serviceConfigGroupsActions: serviceConfigGroupsActionsSlice,
    serviceConfigGroup: serviceConfigGroupSlice,
    serviceComponents: serviceComponentsSlice,
    serviceComponentConfigGroups: serviceComponentConfigGroupsSlice,
    serviceComponentConfigGroupsTable: serviceComponentConfigGroupsTableSlice,
    serviceComponentConfigGroupsActions: serviceComponentConfigGroupsActionsSlice,
    serviceComponentConfigGroupSingle: serviceComponentConfigGroupSingleSlice,
    serviceComponentsTable: serviceComponentsTableSlice,
    serviceComponentsActions: serviceComponentsActionsSlice,
    serviceComponentsDynamicActions: serviceComponentsDynamicActionsSlice,
    serviceComponent: serviceComponentSlice,
    auditOperations: auditOperationsSlice,
    auditOperationsTable: auditOperationsTableSlice,
    auditLogins: auditLoginsSlice,
    auditLoginsTable: auditLoginsTableSlice,
    clusterImports: clusterImportsSlice,
    clusterImportsFilter: clusterImportsFilterSlice,
    clusterImportsService: clusterImportsServiceSlice,
    clusterImportsServiceFilter: clusterImportsServiceFilterSlice,
    clusterOverviewServices: clusterOverviewServicesSlice,
    clusterOverviewHosts: clusterOverviewHostsSlice,
    clusterOverviewServicesTable: clusterOverviewServicesTableSlice,
    clusterOverviewHostsTable: clusterOverviewHostsTableSlice,
    // createHostDialog: createHostDialogSlice,
    users: usersSlice,
    usersTable: usersTableSlice,
    usersActions: usersActionsSlice,
    jobs: jobsSlice,
    bell: bellSlice,
    jobsTable: jobsTableSlice,
    jobsActions: jobsActionsSlice,
    groups: groupsSlice,
    groupsTable: groupsTableSlice,
    groupsActions: groupsActionsSlice,
    policies: policiesSlice,
    policiesActions: policiesActionsSlice,
    policiesTable: policiesTableSlice,
    profile: profileSlice,
    roles: rolesSlice,
    rolesTable: rolesTableSlice,
    rolesActions: rolesActionsSlice,
    adcmSettings: adcmSettingsSlice,
    adcmSettingsDynamicActions: adcmSettingsDynamicActionsSlice,
    entityConfigurationCompare: adcmEntityConfigurationCompareSlice,
    entityConfiguration: adcmEntityConfigurationSlice,
  }),
});

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(apiMiddleware, wsMiddleware),
});

export type StoreState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;
