import api from './axiosInstance'

const BASE = '/auth'

export const register = (data) => api.post(`${BASE}/register/`, data)
export const login = (data) => api.post(`${BASE}/login/`, data)
export const logout = (data) => api.post(`${BASE}/logout/`, data)
export const refresh = (data) => api.post(`${BASE}/refresh/`, data)
export const sendVerificationOtp = (data) => api.post(`${BASE}/send-verification-otp/`, data)
export const verifyOtp = (data) => api.post(`${BASE}/verify-otp/`, data)
export const resendVerificationOtp = (data) => api.post(`${BASE}/resend-verification-otp/`, data)
export const passwordResetRequest = (data) => api.post(`${BASE}/password-reset/request/`, data)
export const passwordResetVerify = (data) => api.post(`${BASE}/password-reset/verify/`, data)
export const passwordResetConfirm = (data) => api.post(`${BASE}/password-reset/confirm/`, data)
export const changePassword = (data) => api.post(`${BASE}/change-password/`, data)
export const getSessions = () => api.get(`${BASE}/sessions/`)
export const revokeSession = (data) => api.post(`${BASE}/sessions/revoke/`, data)
export const securityOverview = () => api.get(`${BASE}/security/overview/`)
export const loginHistory = (params) => api.get(`${BASE}/security/login-history/`, { params })
export const verificationStatus = () => api.get(`${BASE}/security/verification-status/`)
export const securityScore = () => api.get(`${BASE}/security/score/`)
