import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import * as analyticsApi from '../../api/analyticsApi'

const errorMessage = (error, fallback) =>
  error.response?.data?.error?.message ||
  error.response?.data?.detail ||
  fallback

export const fetchAnalyticsDashboard = createAsyncThunk(
  'analytics/dashboard',
  async (params, { rejectWithValue }) => {
    try {
      return (await analyticsApi.getAnalyticsDashboard(params)).data.data
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Failed to load analytics.'))
    }
  },
)

export const fetchReports = createAsyncThunk(
  'analytics/reports',
  async (_, { rejectWithValue }) => {
    try {
      return (await analyticsApi.getReports()).data.data
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Failed to load reports.'))
    }
  },
)

export const generateReport = createAsyncThunk(
  'analytics/generateReport',
  async (data, { rejectWithValue }) => {
    try {
      return (await analyticsApi.createReport(data)).data.data
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Report generation failed.'))
    }
  },
)

export const fetchInsights = createAsyncThunk(
  'analytics/insights',
  async (_, { rejectWithValue }) => {
    try {
      return (await analyticsApi.getInsights()).data.data
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Failed to load insights.'))
    }
  },
)

export const regenerateInsights = createAsyncThunk(
  'analytics/regenerateInsights',
  async (data, { rejectWithValue }) => {
    try {
      return (await analyticsApi.generateInsights(data)).data.data
    } catch (error) {
      return rejectWithValue(errorMessage(error, 'Insight generation failed.'))
    }
  },
)

const initialState = {
  dashboard: null,
  reports: [],
  insights: [],
  loading: false,
  reportLoading: false,
  insightLoading: false,
  error: null,
}

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    clearAnalyticsError: (state) => { state.error = null },
  },
  extraReducers: (builder) => {
    const rejected = (state, action) => {
      state.loading = false
      state.reportLoading = false
      state.insightLoading = false
      state.error = action.payload
    }

    builder
      .addCase(fetchAnalyticsDashboard.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchAnalyticsDashboard.fulfilled, (state, { payload }) => {
        state.loading = false
        state.dashboard = payload
      })
      .addCase(fetchAnalyticsDashboard.rejected, rejected)
      .addCase(fetchReports.pending, (state) => {
        state.reportLoading = true
        state.error = null
      })
      .addCase(fetchReports.fulfilled, (state, { payload }) => {
        state.reportLoading = false
        state.reports = payload
      })
      .addCase(fetchReports.rejected, rejected)
      .addCase(generateReport.pending, (state) => {
        state.reportLoading = true
        state.error = null
      })
      .addCase(generateReport.fulfilled, (state, { payload }) => {
        state.reportLoading = false
        state.reports.unshift(payload)
      })
      .addCase(generateReport.rejected, rejected)
      .addCase(fetchInsights.pending, (state) => {
        state.insightLoading = true
        state.error = null
      })
      .addCase(fetchInsights.fulfilled, (state, { payload }) => {
        state.insightLoading = false
        state.insights = payload
      })
      .addCase(fetchInsights.rejected, rejected)
      .addCase(regenerateInsights.pending, (state) => {
        state.insightLoading = true
        state.error = null
      })
      .addCase(regenerateInsights.fulfilled, (state, { payload }) => {
        state.insightLoading = false
        state.insights = payload
      })
      .addCase(regenerateInsights.rejected, rejected)
  },
})

export const { clearAnalyticsError } = analyticsSlice.actions
export default analyticsSlice.reducer
