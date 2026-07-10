import api from './axiosInstance'

const BASE = '/bookings'

export const getBookings        = (params)       => api.get(`${BASE}/`, { params })
export const createBooking      = (data)         => api.post(`${BASE}/`, data)
export const getBooking         = (id)           => api.get(`${BASE}/${id}/`)
export const updateBookingStatus = (id, data)    => api.patch(`${BASE}/${id}/status/`, data)
export const cancelBooking      = (id, data)     => api.post(`${BASE}/${id}/cancel/`, data)
export const assignCompanion    = (id, data)     => api.post(`${BASE}/${id}/assign-companion/`, data)
export const acceptBooking       = (id)           => api.post(`${BASE}/${id}/accept/`)
export const rejectBooking       = (id, data)     => api.post(`${BASE}/${id}/reject/`, data)
export const getPendingRequests  = ()             => api.get(`${BASE}/pending-requests/`)

