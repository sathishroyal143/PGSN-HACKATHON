import api from './axiosInstance'

const BASE = '/ai'

export const matchCompanions   = (data)  => api.post(`${BASE}/match/`, data)
export const computeTrustScore = (data)  => api.post(`${BASE}/trust-score/`, data)
export const assessPriority    = (data)  => api.post(`${BASE}/priority/`, data)
export const generateSummary   = (data)  => api.post(`${BASE}/medical-summary/`, data)
export const getAIHistory      = ()      => api.get(`${BASE}/history/`)
export const getAIRequest      = (id)    => api.get(`${BASE}/history/${id}/`)
