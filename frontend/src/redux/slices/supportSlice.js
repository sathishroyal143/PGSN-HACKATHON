import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import supportApi from '../../api/supportApi'

export const fetchTickets = createAsyncThunk('support/fetchTickets', async (_, { rejectWithValue }) => {
  try { return (await supportApi.getTickets()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const createTicket = createAsyncThunk('support/createTicket', async (data, { rejectWithValue }) => {
  try { return (await supportApi.createTicket(data)).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fetchTicketDetail = createAsyncThunk('support/fetchDetail', async (ticketId, { rejectWithValue }) => {
  try { return (await supportApi.getTicket(ticketId)).data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fetchFAQs = createAsyncThunk('support/fetchFAQs', async (category, { rejectWithValue }) => {
  try { return (await supportApi.getFAQs(category)).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const sendChatbot = createAsyncThunk('support/chatbot', async (message, { rejectWithValue }) => {
  try { return (await supportApi.chatbot({ message })).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

const supportSlice = createSlice({
  name: 'support',
  initialState: {
    tickets: [], activeTicket: null, activeMessages: [],
    faqs: [], loading: false, error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTickets.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchTickets.fulfilled, (state, action) => { state.loading = false; state.tickets = action.payload || [] })
      .addCase(fetchTickets.rejected, (state, action) => { state.loading = false; state.error = action.payload })
      .addCase(createTicket.fulfilled, (state, action) => { state.tickets.unshift(action.payload) })
      .addCase(fetchTicketDetail.fulfilled, (state, action) => {
        state.activeTicket = action.payload?.data || null
        state.activeMessages = action.payload?.messages || []
      })
      .addCase(fetchFAQs.fulfilled, (state, action) => { state.faqs = action.payload || [] })
  },
})

export default supportSlice.reducer
