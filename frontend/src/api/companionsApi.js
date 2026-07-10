import api from './axiosInstance'

const BASE = '/companions'

export const getCompanions        = (params)       => api.get(`${BASE}/`, { params })
export const createCompanionProfile = (data)       => api.post(`${BASE}/profile/`, data)
export const getMyProfile         = ()             => api.get(`${BASE}/me/`)
export const updateAvailability   = (data)         => api.patch(`${BASE}/me/availability/`, data)
export const updateLocation       = (data)         => api.post(`${BASE}/me/location/`, data)
export const getCompanion         = (id)           => api.get(`${BASE}/${id}/`)
export const updateCompanionProfile = (id, data)   => api.patch(`${BASE}/${id}/`, data)
