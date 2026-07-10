import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import dashboardApi from '../../api/dashboardApi'

export const fetchDashboard = createAsyncThunk('dashboard/fetch', async (_, { rejectWithValue }) => {
  try { return (await dashboardApi.getDashboard()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: { stats: null, recentBookings: [], role: null, loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboard.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchDashboard.fulfilled, (state, action) => {
        state.loading = false
        state.stats = action.payload?.stats || null
        state.recentBookings = action.payload?.recent_bookings || []
        state.role = action.payload?.role || null
      })
      .addCase(fetchDashboard.rejected, (state, action) => { state.loading = false; state.error = action.payload })
  },
})

export default dashboardSlice.reducer
