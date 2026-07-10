import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import {
  getCareServices, getCareService, getScheduledServices,
  getInstantServices, getEmergencyServices, getCategories,
  getServiceTypes, getPackages, getAllPackages, getPackage, calculatePrice,
} from '../../api/servicesApi'

// ── CareService thunks (primary) ──────────────────────────────────────────────
export const fetchCareServices = createAsyncThunk('services/fetchCareServices',
  async (_, { rejectWithValue }) => {
    try { return (await getCareServices()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch services') }
  }
)

export const fetchCareService = createAsyncThunk('services/fetchCareService',
  async (id, { rejectWithValue }) => {
    try { return (await getCareService(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch service') }
  }
)

export const fetchScheduledServices = createAsyncThunk('services/fetchScheduled',
  async (_, { rejectWithValue }) => {
    try { return (await getScheduledServices()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed') }
  }
)

export const fetchInstantServices = createAsyncThunk('services/fetchInstant',
  async (_, { rejectWithValue }) => {
    try { return (await getInstantServices()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed') }
  }
)

export const fetchEmergencyServices = createAsyncThunk('services/fetchEmergency',
  async (_, { rejectWithValue }) => {
    try { return (await getEmergencyServices()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed') }
  }
)

export const fetchCategories = createAsyncThunk('services/fetchCategories',
  async (_, { rejectWithValue }) => {
    try { return (await getCategories()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed') }
  }
)

// ── Legacy thunks (kept for price calculator) ─────────────────────────────────
export const fetchServiceTypes = createAsyncThunk('services/fetchTypes',
  async (params, { rejectWithValue }) => {
    try { return (await getServiceTypes(params)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch service types') }
  }
)

export const fetchPackages = createAsyncThunk('services/fetchPackages',
  async (params, { rejectWithValue }) => {
    try { return (await getPackages(params)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch packages') }
  }
)

export const fetchAllPackages = createAsyncThunk('services/fetchAllPackages',
  async (_, { rejectWithValue }) => {
    try { return (await getAllPackages()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch packages') }
  }
)

export const fetchPackage = createAsyncThunk('services/fetchPackage',
  async (id, { rejectWithValue }) => {
    try { return (await getPackage(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch package') }
  }
)

export const calcPrice = createAsyncThunk('services/calcPrice',
  async (data, { rejectWithValue }) => {
    try { return (await calculatePrice(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to calculate price') }
  }
)

const initialState = {
  // CareService (primary)
  careServices: [],
  currentCareService: null,
  categories: [],
  // Legacy packages
  serviceTypes: [],
  packages: [],
  currentPackage: null,
  priceEstimate: null,
  loading: false,
  error: null,
}

const servicesSlice = createSlice({
  name: 'services',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null },
    clearCurrentPackage: (state) => { state.currentPackage = null },
    clearPriceEstimate: (state) => { state.priceEstimate = null },
    clearCurrentCareService: (state) => { state.currentCareService = null },
  },
  extraReducers: (builder) => {
    const pending  = (state) => { state.loading = true;  state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      // CareService
      .addCase(fetchCareServices.pending, pending)
      .addCase(fetchCareServices.fulfilled, (state, { payload }) => { state.loading = false; state.careServices = payload || [] })
      .addCase(fetchCareServices.rejected, rejected)

      .addCase(fetchCareService.pending, pending)
      .addCase(fetchCareService.fulfilled, (state, { payload }) => { state.loading = false; state.currentCareService = payload })
      .addCase(fetchCareService.rejected, rejected)

      .addCase(fetchScheduledServices.fulfilled, (state, { payload }) => { state.careServices = payload || [] })
      .addCase(fetchInstantServices.fulfilled, (state, { payload }) => { state.careServices = payload || [] })
      .addCase(fetchEmergencyServices.fulfilled, (state, { payload }) => { state.careServices = payload || [] })
      .addCase(fetchCategories.fulfilled, (state, { payload }) => { state.categories = payload || [] })

      // Legacy
      .addCase(fetchServiceTypes.pending, pending)
      .addCase(fetchServiceTypes.fulfilled, (state, { payload }) => { state.loading = false; state.serviceTypes = payload || [] })
      .addCase(fetchServiceTypes.rejected, rejected)

      .addCase(fetchPackages.pending, pending)
      .addCase(fetchPackages.fulfilled, (state, { payload }) => { state.loading = false; state.packages = payload || [] })
      .addCase(fetchPackages.rejected, rejected)

      .addCase(fetchAllPackages.pending, pending)
      .addCase(fetchAllPackages.fulfilled, (state, { payload }) => { state.loading = false; state.packages = payload || [] })
      .addCase(fetchAllPackages.rejected, rejected)

      .addCase(fetchPackage.pending, pending)
      .addCase(fetchPackage.fulfilled, (state, { payload }) => { state.loading = false; state.currentPackage = payload })
      .addCase(fetchPackage.rejected, rejected)

      .addCase(calcPrice.pending, pending)
      .addCase(calcPrice.fulfilled, (state, { payload }) => { state.loading = false; state.priceEstimate = payload })
      .addCase(calcPrice.rejected, rejected)
  },
})

export const { clearError, clearCurrentPackage, clearPriceEstimate, clearCurrentCareService } = servicesSlice.actions
export default servicesSlice.reducer
