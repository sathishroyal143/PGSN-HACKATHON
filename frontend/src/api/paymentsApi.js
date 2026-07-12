import axiosInstance from './axiosInstance'

const BASE = '/payments'

const paymentsApi = {
  getPayments: () => axiosInstance.get(`${BASE}/`),
  initiatePayment: (data) => axiosInstance.post(`${BASE}/`, data),
  verifyPayment: (paymentId, data) => axiosInstance.post(`${BASE}/${paymentId}/verify/`, data),
  getRefunds: (paymentId) => axiosInstance.get(`${BASE}/${paymentId}/refunds/`),
  requestRefund: (paymentId, data) => axiosInstance.post(`${BASE}/${paymentId}/refunds/`, data),
  getInvoices: () => axiosInstance.get(`${BASE}/invoices/`),
  getInvoiceByBooking: (bookingId) => axiosInstance.get(`${BASE}/invoices/booking/${bookingId}/`),
  getWallet: () => axiosInstance.get(`${BASE}/wallet/`),
  getWalletTransactions: () => axiosInstance.get(`${BASE}/wallet/transactions/`),
  rechargeWallet: (data) => axiosInstance.post(`${BASE}/wallet/recharge/`, data),
  withdrawFromWallet: (data) => axiosInstance.post(`${BASE}/wallet/withdraw/`, data),
}

export default paymentsApi
