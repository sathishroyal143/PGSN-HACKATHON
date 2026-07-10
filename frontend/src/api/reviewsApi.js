import axiosInstance from './axiosInstance'

const BASE = '/reviews'

const reviewsApi = {
  getMyReviews: () => axiosInstance.get(`${BASE}/`),
  submitReview: (data) => axiosInstance.post(`${BASE}/`, data),
  getReviewsForUser: (userId) => axiosInstance.get(`${BASE}/user/${userId}/`),
  replyToReview: (reviewId, data) => axiosInstance.post(`${BASE}/${reviewId}/reply/`, data),
  getComplaints: () => axiosInstance.get(`${BASE}/complaints/`),
  fileComplaint: (data) => axiosInstance.post(`${BASE}/complaints/`, data),
  getComplaint: (complaintId) => axiosInstance.get(`${BASE}/complaints/${complaintId}/`),
}

export default reviewsApi
