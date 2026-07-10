import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import {
  getJourneys, startJourney, getJourney,
  getJourneyByBooking, advanceStep, updateNotes, cancelJourney,
} from '../../api/careJourneyApi'

export const fetchJourneys = createAsyncThunk('careJourney/fetchAll',
  async (_, { rejectWithValue }) => {
    try { return (await getJourneys()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch journeys') }
  }
)

export const createJourney = createAsyncThunk('careJourney/create',
  async (data, { rejectWithValue }) => {
    try { return (await startJourney(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to start journey') }
  }
)

export const fetchJourney = createAsyncThunk('careJourney/fetchOne',
  async (id, { rejectWithValue }) => {
    try { return (await getJourney(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch journey') }
  }
)

export const fetchJourneyByBooking = createAsyncThunk('careJourney/fetchByBooking',
  async (bookingId, { rejectWithValue }) => {
    try { return (await getJourneyByBooking(bookingId)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch journey') }
  }
)

export const updateStep = createAsyncThunk('careJourney/advanceStep',
  async ({ id, data }, { rejectWithValue }) => {
    try { return (await advanceStep(id, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to update step') }
  }
)

export const saveNotes = createAsyncThunk('careJourney/updateNotes',
  async ({ id, data }, { rejectWithValue }) => {
    try { return (await updateNotes(id, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to update notes') }
  }
)

export const cancelActiveJourney = createAsyncThunk('careJourney/cancel',
  async (id, { rejectWithValue }) => {
    try { return (await cancelJourney(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to cancel journey') }
  }
)

const initialState = {
  journeys: [],
  currentJourney: null,
  loading: false,
  error: null,
}

const careJourneySlice = createSlice({
  name: 'careJourney',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null },
    clearCurrentJourney: (state) => { state.currentJourney = null },
  },
  extraReducers: (builder) => {
    const pending  = (state) => { state.loading = true;  state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }
    const setCurrent = (state, { payload }) => { state.loading = false; state.currentJourney = payload }

    builder
      .addCase(fetchJourneys.pending, pending)
      .addCase(fetchJourneys.fulfilled, (state, { payload }) => { state.loading = false; state.journeys = payload })
      .addCase(fetchJourneys.rejected, rejected)

      .addCase(createJourney.pending, pending)
      .addCase(createJourney.fulfilled, (state, { payload }) => {
        state.loading = false
        state.currentJourney = payload
        state.journeys.unshift(payload)
      })
      .addCase(createJourney.rejected, rejected)

      .addCase(fetchJourney.pending, pending)
      .addCase(fetchJourney.fulfilled, setCurrent)
      .addCase(fetchJourney.rejected, rejected)

      .addCase(fetchJourneyByBooking.pending, pending)
      .addCase(fetchJourneyByBooking.fulfilled, setCurrent)
      .addCase(fetchJourneyByBooking.rejected, rejected)

      .addCase(updateStep.pending, pending)
      .addCase(updateStep.fulfilled, setCurrent)
      .addCase(updateStep.rejected, rejected)

      .addCase(saveNotes.pending, pending)
      .addCase(saveNotes.fulfilled, setCurrent)
      .addCase(saveNotes.rejected, rejected)

      .addCase(cancelActiveJourney.pending, pending)
      .addCase(cancelActiveJourney.fulfilled, setCurrent)
      .addCase(cancelActiveJourney.rejected, rejected)
  },
})

export const { clearError, clearCurrentJourney } = careJourneySlice.actions
export default careJourneySlice.reducer
