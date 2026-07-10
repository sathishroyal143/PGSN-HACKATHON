import api from './axiosInstance'

const BASE = '/analytics'

export const getAnalyticsDashboard = (params) =>
  api.get(`${BASE}/dashboard/`, { params })

export const getAnalyticsEvents = (params) =>
  api.get(`${BASE}/events/`, { params })

export const getReports = () =>
  api.get(`${BASE}/reports/`)

export const createReport = (data) =>
  api.post(`${BASE}/reports/`, data)

export const getReport = (id) =>
  api.get(`${BASE}/reports/${id}/`)

export const getInsights = () =>
  api.get(`${BASE}/insights/`)

export const generateInsights = (data) =>
  api.post(`${BASE}/insights/generate/`, data)
