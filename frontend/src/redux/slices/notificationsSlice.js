import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import notificationsApi from '../../api/notificationsApi'

export const fetchNotifications = createAsyncThunk(
  'notifications/fetch',
  async (params = {}, { rejectWithValue }) => {
    try {
      const res = await notificationsApi.getNotifications(params)
      return res.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed to load notifications.')
    }
  }
)

export const markRead = createAsyncThunk(
  'notifications/markRead',
  async (notificationId, { rejectWithValue }) => {
    try {
      await notificationsApi.markRead(notificationId)
      return notificationId
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed.')
    }
  }
)

export const markAllRead = createAsyncThunk(
  'notifications/markAllRead',
  async (_, { rejectWithValue }) => {
    try {
      await notificationsApi.markAllRead()
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed.')
    }
  }
)

export const deleteNotification = createAsyncThunk(
  'notifications/delete',
  async (notificationId, { rejectWithValue }) => {
    try {
      await notificationsApi.deleteNotification(notificationId)
      return notificationId
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed.')
    }
  }
)

export const fetchPreferences = createAsyncThunk(
  'notifications/fetchPreferences',
  async (_, { rejectWithValue }) => {
    try {
      const res = await notificationsApi.getPreferences()
      return res.data.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed.')
    }
  }
)

export const updatePreferences = createAsyncThunk(
  'notifications/updatePreferences',
  async (data, { rejectWithValue }) => {
    try {
      const res = await notificationsApi.updatePreferences(data)
      return res.data.data
    } catch (err) {
      return rejectWithValue(err.response?.data?.error?.message || 'Failed.')
    }
  }
)

const notificationsSlice = createSlice({
  name: 'notifications',
  initialState: {
    items: [],
    unreadCount: 0,
    preferences: null,
    loading: false,
    error: null,
  },
  reducers: {
    appendNotification(state, action) {
      state.items.unshift(action.payload)
      state.unreadCount += 1
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNotifications.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.data || []
        state.unreadCount = action.payload.unread_count ?? 0
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.loading = false; state.error = action.payload
      })

      .addCase(markRead.fulfilled, (state, action) => {
        const n = state.items.find((i) => i.id === action.payload)
        if (n && !n.is_read) { n.is_read = true; state.unreadCount = Math.max(0, state.unreadCount - 1) }
      })

      .addCase(markAllRead.fulfilled, (state) => {
        state.items.forEach((n) => { n.is_read = true })
        state.unreadCount = 0
      })

      .addCase(deleteNotification.fulfilled, (state, action) => {
        const idx = state.items.findIndex((i) => i.id === action.payload)
        if (idx !== -1) {
          if (!state.items[idx].is_read) state.unreadCount = Math.max(0, state.unreadCount - 1)
          state.items.splice(idx, 1)
        }
      })

      .addCase(fetchPreferences.fulfilled, (state, action) => { state.preferences = action.payload })
      .addCase(updatePreferences.fulfilled, (state, action) => { state.preferences = action.payload })
  },
})

export const { appendNotification } = notificationsSlice.actions
export default notificationsSlice.reducer
