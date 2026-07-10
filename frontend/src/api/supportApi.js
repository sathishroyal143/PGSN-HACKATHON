import axiosInstance from './axiosInstance'

const BASE = '/support'

const supportApi = {
  getTickets: () => axiosInstance.get(`${BASE}/tickets/`),
  createTicket: (data) => axiosInstance.post(`${BASE}/tickets/`, data),
  getTicket: (ticketId) => axiosInstance.get(`${BASE}/tickets/${ticketId}/`),
  replyTicket: (ticketId, data) => axiosInstance.post(`${BASE}/tickets/${ticketId}/`, data),
  getFAQs: (category) => axiosInstance.get(`${BASE}/faqs/`, { params: category ? { category } : {} }),
  chatbot: (data) => axiosInstance.post(`${BASE}/chatbot/`, data),
}

export default supportApi
