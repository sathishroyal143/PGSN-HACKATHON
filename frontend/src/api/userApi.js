import api from './axiosInstance'

const BASE = '/users'

export const getMe = () => api.get(`${BASE}/me/`)
export const getUser = (id) => api.get(`${BASE}/${id}/`)
export const updateUser = (id, data) => api.patch(`${BASE}/${id}/`, data)
export const deleteUser = (id) => api.delete(`${BASE}/${id}/`)
export const getUserStatistics = (id) => api.get(`${BASE}/${id}/statistics/`)
export const updateNotificationPreferences = (id, data) => api.patch(`${BASE}/${id}/notification_preferences/`, data)
export const searchUsers = (params) => api.get(`${BASE}/search/`, { params })
export const updateProfilePicture = (id, formData) => api.post(`${BASE}/${id}/update_profile_picture/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
