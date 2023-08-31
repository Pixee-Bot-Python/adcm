import { httpClient } from '@api/httpClient';
import { AdcmMaintenanceMode, AdcmServiceComponent, Batch } from '@models/adcm';
import { SortParams } from '@models/table';
import { prepareSorting } from '@utils/apiUtils';
import qs from 'qs';

export class AdcmClusterServiceComponentsApi {
  public static async getServiceComponents(clusterId: number, serviceId: number, sortParams: SortParams) {
    const queryParams = prepareSorting(sortParams);

    const query = qs.stringify(queryParams);
    const response = await httpClient.get<Batch<AdcmServiceComponent>>(
      `/api/v2/clusters/${clusterId}/services/${serviceId}/components/?${query}/`,
    );

    return response.data;
  }

  public static async getServiceComponent(clusterId: number, serviceId: number, componentId: number) {
    const response = await httpClient.get<AdcmServiceComponent>(
      `/api/v2/clusters/${clusterId}/services/${serviceId}/components/${componentId}/`,
    );

    return response.data;
  }

  public static async toggleMaintenanceMode(
    clusterId: number,
    serviceId: number,
    componentId: number,
    maintenanceMode: AdcmMaintenanceMode,
  ) {
    const response = await httpClient.post(
      `/api/v2/clusters/${clusterId}/services/${serviceId}/components/${componentId}/maintenance-mode/`,
      { maintenanceMode },
    );

    return response.data;
  }
}
