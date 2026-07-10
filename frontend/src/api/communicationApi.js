import axiosInstance from './axiosInstance'

const BASE = '/communication/conversations'

const communicationApi = {
  // Conversations
  getConversations: () =>
    axiosInstance.get(`${BASE}/`),

  createDirectConversation: (recipient_id) =>
    axiosInstance.post(`${BASE}/direct/`, { recipient_id }),

  getConversation: (conversationId) =>
    axiosInstance.get(`${BASE}/${conversationId}/`),

  closeConversation: (conversationId) =>
    axiosInstance.delete(`${BASE}/${conversationId}/`),

  // Messages
  getMessages: (conversationId, params = {}) =>
    axiosInstance.get(`${BASE}/${conversationId}/messages/`, { params }),

  sendMessage: (conversationId, data) =>
    axiosInstance.post(`${BASE}/${conversationId}/messages/`, data),

  deleteMessage: (conversationId, messageId) =>
    axiosInstance.delete(`${BASE}/${conversationId}/messages/${messageId}/`),

  markRead: (conversationId) =>
    axiosInstance.post(`${BASE}/${conversationId}/read/`),

  sendTyping: (conversationId, is_typing) =>
    axiosInstance.post(`${BASE}/${conversationId}/typing/`, { is_typing }),

  // Calls
  getCalls: (conversationId) =>
    axiosInstance.get(`${BASE}/${conversationId}/calls/`),

  initiateCall: (conversationId, data) =>
    axiosInstance.post(`${BASE}/${conversationId}/calls/`, data),

  answerCall: (conversationId, callId) =>
    axiosInstance.post(`${BASE}/${conversationId}/calls/${callId}/answer/`),

  declineCall: (conversationId, callId) =>
    axiosInstance.post(`${BASE}/${conversationId}/calls/${callId}/decline/`),

  endCall: (conversationId, callId) =>
    axiosInstance.post(`${BASE}/${conversationId}/calls/${callId}/end/`),
}

export default communicationApi
