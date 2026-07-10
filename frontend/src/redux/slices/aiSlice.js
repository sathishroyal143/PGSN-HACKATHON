import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import {
  matchCompanions, computeTrustScore, assessPriority,
  generateSummary, getAIHistory, getAIRequest,
} from '../../api/aiApi'

export const fetchCompanionMatches = createAsyncThunk('ai/match',
  async (data, { rejectWithValue }) => {
    try { return (await matchCompanions(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Matching failed') }
  }
)

export const fetchTrustScore = createAsyncThunk('ai/trustScore',
  async (data, { rejectWithValue }) => {
    try { return (await computeTrustScore(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Trust score failed') }
  }
)

export const fetchPriority = createAsyncThunk('ai/priority',
  async (data, { rejectWithValue }) => {
    try { return (await assessPriority(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Priority assessment failed') }
  }
)

export const fetchMedicalSummary = createAsyncThunk('ai/medicalSummary',
  async (data, { rejectWithValue }) => {
    try { return (await generateSummary(data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Summary generation failed') }
  }
)

export const fetchAIHistory = createAsyncThunk('ai/history',
  async (_, { rejectWithValue }) => {
    try { return (await getAIHistory()).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch history') }
  }
)

export const fetchAIRequest = createAsyncThunk('ai/historyDetail',
  async (id, { rejectWithValue }) => {
    try { return (await getAIRequest(id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch request') }
  }
)

const initialState = {
  matches: [],
  trustScore: null,
  priority: null,
  medicalSummary: null,
  history: [],
  currentRequest: null,
  loading: false,
  error: null,
}

const aiSlice = createSlice({
  name: 'ai',
  initialState,
  reducers: {
    clearError:         (state) => { state.error = null },
    clearResults:       (state) => {
      state.matches = []
      state.trustScore = null
      state.priority = null
      state.medicalSummary = null
    },
  },
  extraReducers: (builder) => {
    const pending  = (state) => { state.loading = true;  state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      .addCase(fetchCompanionMatches.pending, pending)
      .addCase(fetchCompanionMatches.fulfilled, (state, { payload }) => {
        state.loading = false; state.matches = payload.matches || []
      })
      .addCase(fetchCompanionMatches.rejected, rejected)

      .addCase(fetchTrustScore.pending, pending)
      .addCase(fetchTrustScore.fulfilled, (state, { payload }) => {
        state.loading = false; state.trustScore = payload
      })
      .addCase(fetchTrustScore.rejected, rejected)

      .addCase(fetchPriority.pending, pending)
      .addCase(fetchPriority.fulfilled, (state, { payload }) => {
        state.loading = false; state.priority = payload
      })
      .addCase(fetchPriority.rejected, rejected)

      .addCase(fetchMedicalSummary.pending, pending)
      .addCase(fetchMedicalSummary.fulfilled, (state, { payload }) => {
        state.loading = false; state.medicalSummary = payload
      })
      .addCase(fetchMedicalSummary.rejected, rejected)

      .addCase(fetchAIHistory.pending, pending)
      .addCase(fetchAIHistory.fulfilled, (state, { payload }) => {
        state.loading = false; state.history = payload
      })
      .addCase(fetchAIHistory.rejected, rejected)

      .addCase(fetchAIRequest.pending, pending)
      .addCase(fetchAIRequest.fulfilled, (state, { payload }) => {
        state.loading = false; state.currentRequest = payload
      })
      .addCase(fetchAIRequest.rejected, rejected)
  },
})

export const { clearError, clearResults } = aiSlice.actions
export default aiSlice.reducer
