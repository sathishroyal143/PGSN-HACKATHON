import api from './axiosInstance'

const BASE = '/patients'

// ── Patients ──────────────────────────────────────────────────────────────────
export const getPatients = () => api.get(`${BASE}/`)
export const getPatient = (id) => api.get(`${BASE}/${id}/`)
export const createPatient = (data) => api.post(`${BASE}/`, data)
export const updatePatient = (id, data) => api.patch(`${BASE}/${id}/`, data)
export const deletePatient = (id) => api.delete(`${BASE}/${id}/`)
export const getPatientsSummary = () => api.get(`${BASE}/summary/`)
export const setPrimaryPatient = (id) => api.post(`${BASE}/${id}/set-primary/`)

// ── Vitals ────────────────────────────────────────────────────────────────────
export const getVitals = (patientId) => api.get(`${BASE}/${patientId}/vitals/`)
export const recordVital = (patientId, data) => api.post(`${BASE}/${patientId}/vitals/`, data)
export const deleteVital = (patientId, vitalId) => api.delete(`${BASE}/${patientId}/vitals/${vitalId}/`)

// ── Insurance ─────────────────────────────────────────────────────────────────
export const getInsurance = (patientId) => api.get(`${BASE}/${patientId}/insurance/`)
export const addInsurance = (patientId, data) => api.post(`${BASE}/${patientId}/insurance/`, data)
export const updateInsurance = (patientId, insuranceId, data) =>
  api.patch(`${BASE}/${patientId}/insurance/${insuranceId}/`, data)
export const deleteInsurance = (patientId, insuranceId) =>
  api.delete(`${BASE}/${patientId}/insurance/${insuranceId}/`)
