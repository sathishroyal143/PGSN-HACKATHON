import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import {
  getBookings, createBooking, getBooking,
  updateBookingStatus, cancelBooking, assignCompanion,
  acceptBooking, rejectBooking, getPendingRequests,
} from '../../api/bookingsApi'

export const fetchBookings = createAsyncThunk('bookings/fetchAll',
  async (params, { rejectWithValue }) => {
    try { return (await getBookings(params)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch bookings') }
  }
)

export const addBooking = createAsyncThunk('bookings/create',
  async (data, { rejectWithValue }) => {
    try { return (await createBooking(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to create booking') }
  }
)

export const fetchBooking = createAsyncThunk('bookings/fetchOne',
  async (id, { rejectWithValue }) => {
    try { return (await getBooking(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch booking') }
  }
)

export const changeBookingStatus = createAsyncThunk('bookings/changeStatus',
  async ({ id, data }, { rejectWithValue }) => {
    try { return (await updateBookingStatus(id, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to update status') }
  }
)

export const cancelBookingThunk = createAsyncThunk('bookings/cancel',
  async ({ id, reason }, { rejectWithValue }) => {
    try { return (await cancelBooking(id, { reason })).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to cancel booking') }
  }
)

export const assignCompanionThunk = createAsyncThunk('bookings/assignCompanion',
  async ({ id, companion_id }, { rejectWithValue }) => {
    try { return (await assignCompanion(id, { companion_id })).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to assign companion') }
  }
)

export const fetchPendingRequests = createAsyncThunk('bookings/fetchPendingRequests',
  async (_, { rejectWithValue }) => {
    try { return (await getPendingRequests()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch pending requests') }
  }
)

export const acceptBookingThunk = createAsyncThunk('bookings/accept',
  async (id, { rejectWithValue }) => {
    try { return (await acceptBooking(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to accept booking') }
  }
)

export const rejectBookingThunk = createAsyncThunk('bookings/reject',
  async ({ id, reason }, { rejectWithValue }) => {
    try { return (await rejectBooking(id, { reason })).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to reject booking') }
  }
)

const initialState = {
  bookings: [],
  pendingRequests: [],
  currentBooking: null,
  loading: false,
  error: null,
}

const bookingsSlice = createSlice({
  name: 'bookings',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null },
    clearCurrentBooking: (state) => { state.currentBooking = null },
  },
  extraReducers: (builder) => {
    const pending  = (state) => { state.loading = true;  state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      .addCase(fetchBookings.pending, pending)
      .addCase(fetchBookings.fulfilled, (state, { payload }) => { state.loading = false; state.bookings = payload })
      .addCase(fetchBookings.rejected, rejected)

      .addCase(addBooking.pending, pending)
      .addCase(addBooking.fulfilled, (state, { payload }) => {
        state.loading = false
        state.bookings.unshift(payload)
        state.currentBooking = payload
      })
      .addCase(addBooking.rejected, rejected)

      .addCase(fetchBooking.pending, pending)
      .addCase(fetchBooking.fulfilled, (state, { payload }) => { state.loading = false; state.currentBooking = payload })
      .addCase(fetchBooking.rejected, rejected)

      .addCase(changeBookingStatus.pending, pending)
      .addCase(changeBookingStatus.fulfilled, (state, { payload }) => {
        state.loading = false
        state.currentBooking = payload
        const idx = state.bookings.findIndex((b) => b.id === payload.id)
        if (idx !== -1) state.bookings[idx] = { ...state.bookings[idx], status: payload.status }
      })
      .addCase(changeBookingStatus.rejected, rejected)

      .addCase(cancelBookingThunk.pending, pending)
      .addCase(cancelBookingThunk.fulfilled, (state, { payload }) => {
        state.loading = false
        state.currentBooking = payload
        const idx = state.bookings.findIndex((b) => b.id === payload.id)
        if (idx !== -1) state.bookings[idx] = { ...state.bookings[idx], status: payload.status }
      })
      .addCase(cancelBookingThunk.rejected, rejected)

      .addCase(assignCompanionThunk.pending, pending)
      .addCase(assignCompanionThunk.fulfilled, (state, { payload }) => { state.loading = false; state.currentBooking = payload })
      .addCase(assignCompanionThunk.rejected, rejected)

      .addCase(fetchPendingRequests.pending, pending)
      .addCase(fetchPendingRequests.fulfilled, (state, { payload }) => { state.loading = false; state.pendingRequests = payload })
      .addCase(fetchPendingRequests.rejected, rejected)

      .addCase(acceptBookingThunk.pending, pending)
      .addCase(acceptBookingThunk.fulfilled, (state, { payload }) => {
        state.loading = false
        state.pendingRequests = state.pendingRequests.filter((r) => r.id !== payload.id)
        state.currentBooking = payload
      })
      .addCase(acceptBookingThunk.rejected, rejected)

      .addCase(rejectBookingThunk.pending, pending)
      .addCase(rejectBookingThunk.fulfilled, (state, { payload }) => {
        state.loading = false
        state.pendingRequests = state.pendingRequests.filter((r) => r.id !== payload.id)
      })
      .addCase(rejectBookingThunk.rejected, rejected)
  },
})

export const { clearError, clearCurrentBooking } = bookingsSlice.actions
export default bookingsSlice.reducer
