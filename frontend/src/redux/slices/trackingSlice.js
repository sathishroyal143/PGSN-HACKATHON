import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import trackingApi from '../../api/trackingApi'

// ---------------------------------------------------------------------------
// Thunks
// ---------------------------------------------------------------------------

export const fetchTrackingSummary = createAsyncThunk(
  'tracking/fetchSummary',
  async (bookingId, { rejectWithValue }) => {
    try {
      const res = await trackingApi.getSummary(bookingId)
      return res.data.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load tracking summary.')
    }
  }
)

export const fetchLocationHistory = createAsyncThunk(
  'tracking/fetchHistory',
  async ({ bookingId, limit }, { rejectWithValue }) => {
    try {
      const res = await trackingApi.getLocationHistory(bookingId, limit)
      return res.data.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load location history.')
    }
  }
)

export const fetchRoutes = createAsyncThunk(
  'tracking/fetchRoutes',
  async (bookingId, { rejectWithValue }) => {
    try {
      const res = await trackingApi.getRoutes(bookingId)
      return res.data.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load routes.')
    }
  }
)

export const fetchGeofenceEvents = createAsyncThunk(
  'tracking/fetchGeofenceEvents',
  async (bookingId, { rejectWithValue }) => {
    try {
      const res = await trackingApi.getGeofenceEvents(bookingId)
      return res.data.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load geofence events.')
    }
  }
)

// ---------------------------------------------------------------------------
// Slice
// ---------------------------------------------------------------------------

const initialState = {
  // Keyed by bookingId for multi-booking support
  summaries: {},       // { [bookingId]: { live_location, active_route, geofences } }
  histories: {},       // { [bookingId]: [...points] }
  routes: {},          // { [bookingId]: [...routes] }
  geofenceEvents: {},  // { [bookingId]: [...events] }
  wsStatus: {},        // { [bookingId]: 'connecting' | 'connected' | 'disconnected' | 'error' }
  loading: false,
  error: null,
}

const trackingSlice = createSlice({
  name: 'tracking',
  initialState,
  reducers: {
    setWsStatus(state, action) {
      const { bookingId, status } = action.payload
      state.wsStatus[bookingId] = status
    },
    updateLiveLocation(state, action) {
      const { bookingId, location } = action.payload
      if (state.summaries[bookingId]) {
        state.summaries[bookingId].live_location = location
      } else {
        state.summaries[bookingId] = { live_location: location, active_route: null, geofences: [] }
      }
      // Append to history trail
      if (!state.histories[bookingId]) state.histories[bookingId] = []
      state.histories[bookingId].push({
        latitude: location.latitude,
        longitude: location.longitude,
        recorded_at: location.recorded_at,
      })
    },
    updateActiveRoute(state, action) {
      const { bookingId, route } = action.payload
      if (state.summaries[bookingId]) {
        state.summaries[bookingId].active_route = route
      }
    },
    appendGeofenceEvent(state, action) {
      const { bookingId, event } = action.payload
      if (!state.geofenceEvents[bookingId]) state.geofenceEvents[bookingId] = []
      state.geofenceEvents[bookingId].unshift(event)
    },
    clearTracking(state, action) {
      const bookingId = action.payload
      delete state.summaries[bookingId]
      delete state.histories[bookingId]
      delete state.routes[bookingId]
      delete state.geofenceEvents[bookingId]
      delete state.wsStatus[bookingId]
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTrackingSummary.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchTrackingSummary.fulfilled, (state, action) => {
        state.loading = false
        const bookingId = action.meta.arg
        state.summaries[bookingId] = action.payload
      })
      .addCase(fetchTrackingSummary.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })

      .addCase(fetchLocationHistory.fulfilled, (state, action) => {
        const bookingId = action.meta.arg.bookingId
        state.histories[bookingId] = action.payload
      })

      .addCase(fetchRoutes.fulfilled, (state, action) => {
        const bookingId = action.meta.arg
        state.routes[bookingId] = action.payload
      })

      .addCase(fetchGeofenceEvents.fulfilled, (state, action) => {
        const bookingId = action.meta.arg
        state.geofenceEvents[bookingId] = action.payload
      })
  },
})

export const {
  setWsStatus,
  updateLiveLocation,
  updateActiveRoute,
  appendGeofenceEvent,
  clearTracking,
} = trackingSlice.actions

export default trackingSlice.reducer
