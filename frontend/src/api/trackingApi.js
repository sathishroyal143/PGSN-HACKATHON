import axiosInstance from './axiosInstance'

const BASE = (bookingId) => `/tracking/${bookingId}`

const trackingApi = {
  // Summary
  getSummary: (bookingId) =>
    axiosInstance.get(`${BASE(bookingId)}/summary/`),

  // Location
  postLocation: (bookingId, data) =>
    axiosInstance.post(`${BASE(bookingId)}/location/`, data),

  getLiveLocation: (bookingId) =>
    axiosInstance.get(`${BASE(bookingId)}/location/`),

  getLocationHistory: (bookingId, limit = 500) =>
    axiosInstance.get(`${BASE(bookingId)}/location/history/`, { params: { limit } }),

  // Routes
  getRoutes: (bookingId) =>
    axiosInstance.get(`${BASE(bookingId)}/routes/`),

  createRoute: (bookingId, data) =>
    axiosInstance.post(`${BASE(bookingId)}/routes/`, data),

  activateRoute: (bookingId, routeId) =>
    axiosInstance.post(`${BASE(bookingId)}/routes/${routeId}/activate/`),

  completeRoute: (bookingId, routeId) =>
    axiosInstance.post(`${BASE(bookingId)}/routes/${routeId}/complete/`),

  updateETA: (bookingId, routeId, estimated_arrival) =>
    axiosInstance.patch(`${BASE(bookingId)}/routes/${routeId}/eta/`, { estimated_arrival }),

  // Geofences
  getGeofences: (bookingId) =>
    axiosInstance.get(`${BASE(bookingId)}/geofences/`),

  createGeofence: (bookingId, data) =>
    axiosInstance.post(`${BASE(bookingId)}/geofences/`, data),

  getGeofenceEvents: (bookingId) =>
    axiosInstance.get(`${BASE(bookingId)}/geofences/events/`),
}

export default trackingApi
