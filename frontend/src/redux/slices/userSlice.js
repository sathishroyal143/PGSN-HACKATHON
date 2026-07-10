import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import * as userApi from '../../api/userApi'

export const fetchMe = createAsyncThunk('user/fetchMe', async (_, { rejectWithValue }) => {
  try {
    const res = await userApi.getMe()
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to load profile.')
  }
})

export const updateMe = createAsyncThunk('user/updateMe', async ({ id, data }, { rejectWithValue }) => {
  try {
    const res = await userApi.updateUser(id, data)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to update profile.')
  }
})

export const updateNotificationPrefs = createAsyncThunk('user/updateNotificationPrefs', async ({ id, data }, { rejectWithValue }) => {
  try {
    const res = await userApi.updateNotificationPreferences(id, data)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to update preferences.')
  }
})

export const updateUserProfilePicture = createAsyncThunk('user/updateUserProfilePicture', async ({ id, formData }, { rejectWithValue }) => {
  try {
    const res = await userApi.updateProfilePicture(id, formData)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to update profile picture.')
  }
})


const userSlice = createSlice({
  name: 'user',
  initialState: {
    profile: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearUserError: (state) => { state.error = null },
  },
  extraReducers: (builder) => {
    const pending = (state) => { state.loading = true; state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      .addCase(fetchMe.pending, pending)
      .addCase(fetchMe.fulfilled, (state, { payload }) => { state.loading = false; state.profile = payload })
      .addCase(fetchMe.rejected, rejected)

      .addCase(updateMe.pending, pending)
      .addCase(updateMe.fulfilled, (state, { payload }) => { state.loading = false; state.profile = payload })
      .addCase(updateMe.rejected, rejected)

      .addCase(updateNotificationPrefs.pending, pending)
      .addCase(updateNotificationPrefs.fulfilled, (state, { payload }) => {
        state.loading = false
        if (state.profile) Object.assign(state.profile, payload)
      })
      .addCase(updateNotificationPrefs.rejected, rejected)

      .addCase(updateUserProfilePicture.pending, pending)
      .addCase(updateUserProfilePicture.fulfilled, (state, { payload }) => {
        state.loading = false
        if (state.profile) {
          state.profile.profile_picture = payload.profile_picture
        }
      })
      .addCase(updateUserProfilePicture.rejected, rejected)
  },

})

export const { clearUserError } = userSlice.actions
export default userSlice.reducer
