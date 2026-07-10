import api from './axiosInstance'

const BASE = '/care-journey'

export const getJourneys         = ()                    => api.get(`${BASE}/`)
export const startJourney        = (data)                => api.post(`${BASE}/`, data)
export const getJourney          = (id)                  => api.get(`${BASE}/${id}/`)
export const getJourneyByBooking = (bookingId)           => api.get(`${BASE}/booking/${bookingId}/`)
export const advanceStep         = (id, data)            => api.patch(`${BASE}/${id}/advance-step/`, data)
export const updateNotes         = (id, data)            => api.patch(`${BASE}/${id}/notes/`, data)
export const cancelJourney       = (id)                  => api.post(`${BASE}/${id}/cancel/`)
