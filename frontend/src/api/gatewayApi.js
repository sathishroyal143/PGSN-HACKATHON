import api from './axiosInstance'

const BASE = '/gateway'

export const getAPIKeys = () => api.get(`${BASE}/keys/`)
export const createAPIKey = (data) => api.post(`${BASE}/keys/`, data)
export const revokeAPIKey = (id) => api.post(`${BASE}/keys/${id}/revoke/`)

export const getRateLimits = () => api.get(`${BASE}/rate-limits/`)
export const createRateLimit = (data) => api.post(`${BASE}/rate-limits/`, data)
export const updateRateLimit = (id, data) => api.patch(`${BASE}/rate-limits/${id}/`, data)

export const getAuditLogs = (params) => api.get(`${BASE}/audit-logs/`, { params })
export const getGatewayStatistics = () => api.get(`${BASE}/statistics/`)
