import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import {
  getCompanions, createCompanionProfile, getMyProfile,
  updateAvailability, updateLocation, getCompanion, updateCompanionProfile,
} from '../../api/companionsApi'

export const fetchCompanions = createAsyncThunk('companions/fetchAll',
  async (params, { rejectWithValue }) => {
    try { return (await getCompanions(params)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch companions') }
  }
)

export const createProfile = createAsyncThunk('companions/createProfile',
  async (data, { rejectWithValue }) => {
    try { return (await createCompanionProfile(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to create profile') }
  }
)

export const fetchMyProfile = createAsyncThunk('companions/fetchMyProfile',
  async (_, { rejectWithValue }) => {
    try { return (await getMyProfile()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch profile') }
  }
)

export const setAvailability = createAsyncThunk('companions/setAvailability',
  async (data, { rejectWithValue }) => {
    try { return (await updateAvailability(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to update availability') }
  }
)

export const setLocation = createAsyncThunk('companions/setLocation',
  async (data, { rejectWithValue }) => {
    try { return (await updateLocation(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to update location') }
  }
)

export const fetchCompanion = createAsyncThunk('companions/fetchOne',
  async (id, { rejectWithValue }) => {
    try { return (await getCompanion(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch companion') }
  }
)

export const editProfile = createAsyncThunk('companions/editProfile',
  async ({ id, data }, { rejectWithValue }) => {
    try { return (await updateCompanionProfile(id, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to update profile') }
  }
)

const initialState = {
  companions: [],
  currentCompanion: null,
  myProfile: null,
  loading: false,
  error: null,
}

const companionsSlice = createSlice({
  name: 'companions',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null },
    clearCurrentCompanion: (state) => { state.currentCompanion = null },
  },
  extraReducers: (builder) => {
    const pending  = (state) => { state.loading = true;  state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      .addCase(fetchCompanions.pending, pending)
      .addCase(fetchCompanions.fulfilled, (state, { payload }) => { state.loading = false; state.companions = payload })
      .addCase(fetchCompanions.rejected, rejected)

      .addCase(createProfile.pending, pending)
      .addCase(createProfile.fulfilled, (state, { payload }) => { state.loading = false; state.myProfile = payload })
      .addCase(createProfile.rejected, rejected)

      .addCase(fetchMyProfile.pending, pending)
      .addCase(fetchMyProfile.fulfilled, (state, { payload }) => { state.loading = false; state.myProfile = payload })
      .addCase(fetchMyProfile.rejected, rejected)

      .addCase(setAvailability.pending, pending)
      .addCase(setAvailability.fulfilled, (state, { payload }) => { state.loading = false; state.myProfile = payload })
      .addCase(setAvailability.rejected, rejected)

      .addCase(setLocation.fulfilled, (state) => { state.loading = false })

      .addCase(fetchCompanion.pending, pending)
      .addCase(fetchCompanion.fulfilled, (state, { payload }) => { state.loading = false; state.currentCompanion = payload })
      .addCase(fetchCompanion.rejected, rejected)

      .addCase(editProfile.pending, pending)
      .addCase(editProfile.fulfilled, (state, { payload }) => {
        state.loading = false
        state.currentCompanion = payload
        const idx = state.companions.findIndex((c) => c.id === payload.id)
        if (idx !== -1) state.companions[idx] = payload
      })
      .addCase(editProfile.rejected, rejected)
  },
})

export const { clearError, clearCurrentCompanion } = companionsSlice.actions
export default companionsSlice.reducer
