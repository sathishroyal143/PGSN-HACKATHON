import axiosInstance from './axiosInstance'

const BASE = '/verification'

const verificationApi = {
  getDocuments: () => axiosInstance.get(`${BASE}/documents/`),
  uploadDocument: (formData) => axiosInstance.post(`${BASE}/documents/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getDocument: (docId) => axiosInstance.get(`${BASE}/documents/${docId}/`),
  reviewDocument: (docId, data) => axiosInstance.post(`${BASE}/documents/${docId}/review/`, data),
  getKYC: () => axiosInstance.get(`${BASE}/kyc/`),
}

export default verificationApi
