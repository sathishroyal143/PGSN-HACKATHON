import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import * as authApi from '../../api/authApi'
import { getMe } from '../../api/userApi'

export const registerUser = createAsyncThunk('auth/register', async (data, { rejectWithValue }) => {
  try {
    const res = await authApi.register(data)
    return res.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Registration failed.')
  }
})

export const loginUser = createAsyncThunk('auth/login', async (data, { rejectWithValue }) => {
  try {
    const res = await authApi.login(data)
    const { access, refresh, user } = res.data.data
    localStorage.setItem('access', access)
    localStorage.setItem('refresh', refresh)
    return { access, refresh, user }
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Login failed.')
  }
})

export const logoutUser = createAsyncThunk('auth/logout', async (_, { rejectWithValue }) => {
  try {
    const refresh = localStorage.getItem('refresh')
    if (refresh) await authApi.logout({ refresh })
  } catch (_) {}
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
})

export const fetchCurrentUser = createAsyncThunk('auth/fetchCurrentUser', async (_, { rejectWithValue }) => {
  try {
    const res = await getMe()
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to fetch user profile.')
  }
})

export const sendVerificationOtp = createAsyncThunk('auth/sendOtp', async (data, { rejectWithValue }) => {
  try {
    const res = await authApi.sendVerificationOtp(data)
    return res.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to send OTP.')
  }
})

export const verifyOtp = createAsyncThunk('auth/verifyOtp', async (data, { rejectWithValue }) => {
  try {
    const res = await authApi.verifyOtp(data)
    return res.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'OTP verification failed.')
  }
})

export const requestPasswordReset = createAsyncThunk('auth/passwordResetRequest', async (data, { rejectWithValue }) => {
  try {
    const res = await authApi.passwordResetRequest(data)
    return res.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to send reset email.')
  }
})

export const confirmPasswordReset = createAsyncThunk('auth/passwordResetConfirm', async (data, { rejectWithValue }) => {
  try {
    const res = await authApi.passwordResetConfirm(data)
    return res.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Password reset failed.')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    isAuthenticated: !!localStorage.getItem('access'),
    loading: false,
    error: null,
    otpSent: false,
    otpVerified: false,
    resetEmailSent: false,
    passwordReset: false,
  },
  reducers: {
    clearError: (state) => { state.error = null },
    clearOtpState: (state) => { state.otpSent = false; state.otpVerified = false },
    clearResetState: (state) => { state.resetEmailSent = false; state.passwordReset = false },
    setUser: (state, action) => { state.user = action.payload },
  },
  extraReducers: (builder) => {
    const pending = (state) => { state.loading = true; state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      .addCase(registerUser.pending, pending)
      .addCase(registerUser.fulfilled, (state) => { state.loading = false })
      .addCase(registerUser.rejected, rejected)

      .addCase(loginUser.pending, pending)
      .addCase(loginUser.fulfilled, (state, { payload }) => {
        state.loading = false
        state.isAuthenticated = true
        state.access = payload.access
        state.refresh = payload.refresh
        state.user = payload.user
      })
      .addCase(loginUser.rejected, rejected)

      .addCase(logoutUser.fulfilled, (state) => {
        state.isAuthenticated = false
        state.user = null
        state.access = null
        state.refresh = null
      })

      .addCase(fetchCurrentUser.fulfilled, (state, { payload }) => {
        state.user = payload
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.isAuthenticated = false
        state.user = null
        state.access = null
        state.refresh = null
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
      })

      .addCase(sendVerificationOtp.pending, pending)
      .addCase(sendVerificationOtp.fulfilled, (state) => { state.loading = false; state.otpSent = true })
      .addCase(sendVerificationOtp.rejected, rejected)

      .addCase(verifyOtp.pending, pending)
      .addCase(verifyOtp.fulfilled, (state) => { state.loading = false; state.otpVerified = true })
      .addCase(verifyOtp.rejected, rejected)

      .addCase(requestPasswordReset.pending, pending)
      .addCase(requestPasswordReset.fulfilled, (state) => { state.loading = false; state.resetEmailSent = true })
      .addCase(requestPasswordReset.rejected, rejected)

      .addCase(confirmPasswordReset.pending, pending)
      .addCase(confirmPasswordReset.fulfilled, (state) => { state.loading = false; state.passwordReset = true })
      .addCase(confirmPasswordReset.rejected, rejected)
  },
})

export const { clearError, clearOtpState, clearResetState, setUser } = authSlice.actions
export default authSlice.reducer
