import api from './axiosInstance'

const BASE = '/services'

// ── CareService endpoints (primary) ──
export const getCareServices     = ()    => api.get(`${BASE}/`)
export const getCareService      = (id)  => api.get(`${BASE}/${id}/`)
export const getScheduledServices = ()   => api.get(`${BASE}/scheduled/`)
export const getInstantServices   = ()   => api.get(`${BASE}/instant/`)
export const getEmergencyServices = ()   => api.get(`${BASE}/emergency/`)
export const getCategories        = ()   => api.get(`${BASE}/categories/`)
export const searchServices       = (q)  => api.get(`${BASE}/search/`, { params: { q } })

// ── Legacy package endpoints (kept for price calculator) ──
export const getServiceTypes    = (params)       => api.get(`${BASE}/types/`, { params })
export const getServiceType     = (id)           => api.get(`${BASE}/types/${id}/`)
export const getPackages        = (params)       => api.get(`${BASE}/packages/`, { params })
export const getAllPackages      = ()             => api.get(`${BASE}/packages/all/`)
export const getPackage         = (id)           => api.get(`${BASE}/packages/${id}/`)
export const calculatePrice     = (data)         => api.post(`${BASE}/calculate-price/`, data)
