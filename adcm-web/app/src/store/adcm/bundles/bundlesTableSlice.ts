import { createAsyncThunk, createListSlice } from '@store/redux';
import { ListState } from '@models/table';
import { AdcmBundlesFilter } from '@models/adcm/bundle';
import { AdcmPrototypesApi } from '@api';
import { AdcmProduct, AdcmPrototypeType } from '@models/adcm';

type AdcmBundlesTableState = ListState<AdcmBundlesFilter> & {
  relatedData: {
    products: AdcmProduct[];
  };
};

const createInitialState = (): AdcmBundlesTableState => ({
  filter: {
    displayName: undefined,
    product: undefined,
  },
  paginationParams: {
    perPage: 10,
    pageNumber: 0,
  },
  requestFrequency: 0,
  sortParams: {
    sortBy: 'name',
    sortDirection: 'asc',
  },
  relatedData: {
    products: [],
  },
});

const loadPrototypeVersions = createAsyncThunk('adcm/bundlesTable/loadPrototype', async (arg, thunkAPI) => {
  try {
    const prototypesWithVersions = await AdcmPrototypesApi.getPrototypeVersions({ type: AdcmPrototypeType.Cluster });
    return prototypesWithVersions;
  } catch (error) {
    return thunkAPI.rejectWithValue(error);
  }
});

const loadRelatedData = createAsyncThunk('adcm/bundlesTable/loadRelatedData', async (arg, thunkAPI) => {
  thunkAPI.dispatch(loadPrototypeVersions());
});

const bundlesTableSlice = createListSlice({
  name: 'adcm/bundlesTable',
  createInitialState,
  reducers: {
    cleanupRelatedData(state) {
      state.relatedData = createInitialState().relatedData;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(loadPrototypeVersions.fulfilled, (state, action) => {
      state.relatedData.products = action.payload.map(({ name, displayName }) => ({ name, displayName }));
    });
  },
});

export const {
  setPaginationParams,
  setRequestFrequency,
  cleanupList,
  cleanupRelatedData,
  setFilter,
  resetFilter,
  setSortParams,
  resetSortParams,
} = bundlesTableSlice.actions;
export { loadRelatedData };
export default bundlesTableSlice.reducer;
