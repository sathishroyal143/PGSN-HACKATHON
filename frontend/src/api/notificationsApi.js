import axiosInstance from './axiosInstance'

const BASE = '/notifications'

const notificationsApi = {
  getNotifications: (params = {}) =>
    axiosInstance.get(`${BASE}/`, { params }),

  markRead: (notificationId) =>
    axiosInstance.post(`${BASE}/${notificationId}/read/`),

  markAllRead: () =>
    axiosInstance.post(`${BASE}/read-all/`),

  deleteNotification: (notificationId) =>
    axiosInstance.delete(`${BASE}/${notificationId}/`),

  getPreferences: () =>
    axiosInstance.get(`${BASE}/preferences/`),

  updatePreferences: (data) =>
    axiosInstance.patch(`${BASE}/preferences/`, data),
}

export default notificationsApi
