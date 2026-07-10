import api from './axiosInstance'

const BASE = (patientId) => `/medical-records/patients/${patientId}/records`
const REC  = (recordId)  => `/medical-records/records/${recordId}`

// Medical Records
export const getMedicalRecords  = (patientId, params) => api.get(`${BASE(patientId)}/`, { params })
export const getMedicalRecord   = (patientId, id)     => api.get(`${BASE(patientId)}/${id}/`)
export const createMedicalRecord= (patientId, data)   => api.post(`${BASE(patientId)}/`, data)
export const updateMedicalRecord= (patientId, id, data) => api.patch(`${BASE(patientId)}/${id}/`, data)
export const deleteMedicalRecord= (patientId, id)     => api.delete(`${BASE(patientId)}/${id}/`)
export const getRecordSummary   = (patientId)         => api.get(`${BASE(patientId)}/summary/`)
export const getRecordTimeline  = (patientId)         => api.get(`${BASE(patientId)}/timeline/`)

// Prescriptions
export const getPrescriptions   = (recordId)          => api.get(`${REC(recordId)}/prescriptions/`)
export const createPrescription = (recordId, data)    => api.post(`${REC(recordId)}/prescriptions/`, data)
export const updatePrescription = (recordId, id, data)=> api.patch(`${REC(recordId)}/prescriptions/${id}/`, data)
export const deletePrescription = (recordId, id)      => api.delete(`${REC(recordId)}/prescriptions/${id}/`)

// Lab Reports
export const getLabReports      = (recordId)          => api.get(`${REC(recordId)}/lab-reports/`)
export const createLabReport    = (recordId, data)    => api.post(`${REC(recordId)}/lab-reports/`, data)
export const updateLabReport    = (recordId, id, data)=> api.patch(`${REC(recordId)}/lab-reports/${id}/`, data)
export const deleteLabReport    = (recordId, id)      => api.delete(`${REC(recordId)}/lab-reports/${id}/`)

// Documents
export const getDocuments       = (recordId)          => api.get(`${REC(recordId)}/documents/`)
export const uploadDocument     = (recordId, formData)=> api.post(`${REC(recordId)}/documents/`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const deleteDocument     = (recordId, id)      => api.delete(`${REC(recordId)}/documents/${id}/`)
