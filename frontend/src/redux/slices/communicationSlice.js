import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import communicationApi from '../../api/communicationApi'

// ---------------------------------------------------------------------------
// Thunks
// ---------------------------------------------------------------------------

export const fetchConversations = createAsyncThunk(
  'communication/fetchConversations',
  async (_, { rejectWithValue }) => {
    try {
      const res = await communicationApi.getConversations()
      return res.data.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load conversations.')
    }
  }
)

export const fetchMessages = createAsyncThunk(
  'communication/fetchMessages',
  async ({ conversationId, before }, { rejectWithValue }) => {
    try {
      const res = await communicationApi.getMessages(conversationId, before ? { before } : {})
      return { conversationId, messages: res.data.data, prepend: !!before }
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load messages.')
    }
  }
)

export const sendMessage = createAsyncThunk(
  'communication/sendMessage',
  async ({ conversationId, data }, { rejectWithValue }) => {
    try {
      const res = await communicationApi.sendMessage(conversationId, data)
      return { conversationId, message: res.data.data }
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to send message.')
    }
  }
)

export const fetchCallHistory = createAsyncThunk(
  'communication/fetchCallHistory',
  async (conversationId, { rejectWithValue }) => {
    try {
      const res = await communicationApi.getCalls(conversationId)
      return { conversationId, calls: res.data.data }
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load calls.')
    }
  }
)

// ---------------------------------------------------------------------------
// Slice
// ---------------------------------------------------------------------------

const initialState = {
  conversations: [],
  messages: {},        // { [conversationId]: [...messages] }
  calls: {},           // { [conversationId]: [...calls] }
  activeConversationId: null,
  wsStatus: {},        // { [conversationId]: 'connecting'|'connected'|'disconnected'|'error' }
  typingUsers: {},     // { [conversationId]: { [userId]: userName } }
  loading: false,
  sending: false,
  error: null,
  incomingCall: null,  // { call_id, caller_name, call_type, conversation_id }
  activeCall: null,    // { call_id, caller_name, call_type, conversation_id }
}

const communicationSlice = createSlice({
  name: 'communication',
  initialState,
  reducers: {
    setActiveConversation(state, action) {
      state.activeConversationId = action.payload
    },
    setWsStatus(state, action) {
      const { conversationId, status } = action.payload
      state.wsStatus[conversationId] = status
    },
    appendIncomingMessage(state, action) {
      const { conversationId, message } = action.payload
      if (!state.messages[conversationId]) state.messages[conversationId] = []
      const exists = state.messages[conversationId].some((m) => m.id === message.id)
      if (!exists) state.messages[conversationId].push(message)
      // Update last_message_at on conversation
      const conv = state.conversations.find((c) => c.id === conversationId)
      if (conv) conv.last_message_at = message.created_at
    },
    setTyping(state, action) {
      const { conversationId, userId, userName, isTyping } = action.payload
      if (!state.typingUsers[conversationId]) state.typingUsers[conversationId] = {}
      if (isTyping) {
        state.typingUsers[conversationId][userId] = userName
      } else {
        delete state.typingUsers[conversationId][userId]
      }
    },
    markConversationRead(state, action) {
      const conversationId = action.payload
      const conv = state.conversations.find((c) => c.id === conversationId)
      if (conv) {
        const participant = conv.participants?.find((p) => p.unread_count > 0)
        if (participant) participant.unread_count = 0
      }
    },
    clearCommunication(state) {
      Object.assign(state, initialState)
    },
    setIncomingCall(state, action) {
      state.incomingCall = action.payload
    },
    setActiveCall(state, action) {
      state.activeCall = action.payload
      state.incomingCall = null
    },
    clearCallState(state) {
      state.incomingCall = null
      state.activeCall = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConversations.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchConversations.fulfilled, (state, action) => {
        state.loading = false
        state.conversations = action.payload || []
      })
      .addCase(fetchConversations.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })

      .addCase(fetchMessages.fulfilled, (state, action) => {
        const { conversationId, messages, prepend } = action.payload
        if (prepend) {
          state.messages[conversationId] = [...messages, ...(state.messages[conversationId] || [])]
        } else {
          state.messages[conversationId] = messages
        }
      })

      .addCase(sendMessage.pending, (state) => { state.sending = true })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.sending = false
        const { conversationId, message } = action.payload
        if (!state.messages[conversationId]) state.messages[conversationId] = []
        const exists = state.messages[conversationId].some((m) => m.id === message.id)
        if (!exists) state.messages[conversationId].push(message)
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.sending = false
        state.error = action.payload
      })

      .addCase(fetchCallHistory.fulfilled, (state, action) => {
        const { conversationId, calls } = action.payload
        state.calls[conversationId] = calls
      })
  },
})

export const {
  setActiveConversation,
  setWsStatus,
  appendIncomingMessage,
  setTyping,
  markConversationRead,
  clearCommunication,
  setIncomingCall,
  setActiveCall,
  clearCallState,
} = communicationSlice.actions

export default communicationSlice.reducer
