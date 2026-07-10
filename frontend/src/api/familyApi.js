import api from './axiosInstance'

const PROFILE = '/family/profile'
const MEMBERS = '/family/members'
const CONTACTS = '/family/emergency-contacts'

export const getProfile = () => api.get(`${PROFILE}/get/`)
export const updateProfile = (data) => api.patch(`${PROFILE}/update/`, data)
export const getProfileSummary = () => api.get(`${PROFILE}/summary/`)

export const getMembers = () => api.get(`${MEMBERS}/`)
export const createMember = (data) => api.post(`${MEMBERS}/`, data)
export const getMember = (id) => api.get(`${MEMBERS}/${id}/`)
export const updateMember = (id, data) => api.patch(`${MEMBERS}/${id}/`, data)
export const deleteMember = (id) => api.delete(`${MEMBERS}/${id}/`)

export const getContacts = () => api.get(`${CONTACTS}/`)
export const createContact = (data) => api.post(`${CONTACTS}/`, data)
export const getContact = (id) => api.get(`${CONTACTS}/${id}/`)
export const updateContact = (id, data) => api.patch(`${CONTACTS}/${id}/`, data)
export const deleteContact = (id) => api.delete(`${CONTACTS}/${id}/`)
