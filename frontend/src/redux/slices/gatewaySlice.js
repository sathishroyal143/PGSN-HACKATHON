import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import * as gatewayApi from '../../api/gatewayApi'

const message = (error, fallback) =>
  error.response?.data?.error?.message || error.response?.data?.detail || fallback

const request = (type, apiCall, fallback) => createAsyncThunk(
  type,
  async (payload, { rejectWithValue }) => {
    try { return (await apiCall(payload)).data.data }
    catch (error) { return rejectWithValue(message(error, fallback)) }
  },
)

export const fetchAPIKeys = request(
  'gateway/keys', gatewayApi.getAPIKeys, 'Failed to load API keys.',
)
export const addAPIKey = request(
  'gateway/addKey', gatewayApi.createAPIKey, 'Failed to create API key.',
)
export const revokeKey = request(
  'gateway/revokeKey', gatewayApi.revokeAPIKey, 'Failed to revoke API key.',
)
export const fetchRateLimits = request(
  'gateway/rateLimits', gatewayApi.getRateLimits, 'Failed to load rate limits.',
)
export const addRateLimit = request(
  'gateway/addRateLimit', gatewayApi.createRateLimit, 'Failed to create rate limit.',
)
export const toggleRateLimit = createAsyncThunk(
  'gateway/toggleRateLimit',
  async ({ id, is_active }, { rejectWithValue }) => {
    try { return (await gatewayApi.updateRateLimit(id, { is_active })).data.data }
    catch (error) {
      return rejectWithValue(message(error, 'Failed to update rate limit.'))
    }
  },
)
export const fetchAuditLogs = request(
  'gateway/auditLogs', gatewayApi.getAuditLogs, 'Failed to load audit logs.',
)
export const fetchGatewayStatistics = request(
  'gateway/statistics', gatewayApi.getGatewayStatistics, 'Failed to load statistics.',
)

const gatewaySlice = createSlice({
  name: 'gateway',
  initialState: {
    keys: [],
    rateLimits: [],
    auditLogs: [],
    statistics: null,
    createdSecret: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearCreatedSecret: (state) => { state.createdSecret = null },
    clearGatewayError: (state) => { state.error = null },
  },
  extraReducers: (builder) => {
    const pending = (state) => { state.loading = true; state.error = null }
    const rejected = (state, action) => {
      state.loading = false
      state.error = action.payload
    }
    builder
      .addCase(fetchAPIKeys.pending, pending)
      .addCase(fetchAPIKeys.fulfilled, (state, { payload }) => {
        state.loading = false; state.keys = payload
      })
      .addCase(fetchAPIKeys.rejected, rejected)
      .addCase(addAPIKey.pending, pending)
      .addCase(addAPIKey.fulfilled, (state, { payload }) => {
        state.loading = false
        state.createdSecret = payload.key
        state.keys.unshift(payload)
      })
      .addCase(addAPIKey.rejected, rejected)
      .addCase(revokeKey.fulfilled, (state, { payload }) => {
        const index = state.keys.findIndex((item) => item.id === payload.id)
        if (index >= 0) state.keys[index] = payload
      })
      .addCase(revokeKey.rejected, rejected)
      .addCase(fetchRateLimits.pending, pending)
      .addCase(fetchRateLimits.fulfilled, (state, { payload }) => {
        state.loading = false; state.rateLimits = payload
      })
      .addCase(fetchRateLimits.rejected, rejected)
      .addCase(addRateLimit.pending, pending)
      .addCase(addRateLimit.fulfilled, (state, { payload }) => {
        state.loading = false; state.rateLimits.push(payload)
      })
      .addCase(addRateLimit.rejected, rejected)
      .addCase(toggleRateLimit.fulfilled, (state, { payload }) => {
        const index = state.rateLimits.findIndex((item) => item.id === payload.id)
        if (index >= 0) state.rateLimits[index] = payload
      })
      .addCase(toggleRateLimit.rejected, rejected)
      .addCase(fetchAuditLogs.pending, pending)
      .addCase(fetchAuditLogs.fulfilled, (state, { payload }) => {
        state.loading = false; state.auditLogs = payload
      })
      .addCase(fetchAuditLogs.rejected, rejected)
      .addCase(fetchGatewayStatistics.fulfilled, (state, { payload }) => {
        state.statistics = payload
      })
      .addCase(fetchGatewayStatistics.rejected, rejected)
  },
})

export const { clearCreatedSecret, clearGatewayError } = gatewaySlice.actions
export default gatewaySlice.reducer
