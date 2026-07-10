import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import paymentsApi from '../../api/paymentsApi'

export const fetchPayments = createAsyncThunk('payments/fetchAll', async (_, { rejectWithValue }) => {
  try { return (await paymentsApi.getPayments()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const initiatePayment = createAsyncThunk('payments/initiate', async (data, { rejectWithValue }) => {
  try { return (await paymentsApi.initiatePayment(data)).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fetchInvoices = createAsyncThunk('payments/fetchInvoices', async (_, { rejectWithValue }) => {
  try { return (await paymentsApi.getInvoices()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fetchWallet = createAsyncThunk('payments/fetchWallet', async (_, { rejectWithValue }) => {
  try { return (await paymentsApi.getWallet()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fetchWalletTransactions = createAsyncThunk('payments/fetchWalletTxns', async (_, { rejectWithValue }) => {
  try { return (await paymentsApi.getWalletTransactions()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

const paymentsSlice = createSlice({
  name: 'payments',
  initialState: {
    payments: [],
    invoices: [],
    wallet: null,
    walletTransactions: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchPayments.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchPayments.fulfilled, (state, action) => { state.loading = false; state.payments = action.payload || [] })
      .addCase(fetchPayments.rejected, (state, action) => { state.loading = false; state.error = action.payload })
      .addCase(initiatePayment.fulfilled, (state, action) => { state.payments.unshift(action.payload) })
      .addCase(fetchInvoices.fulfilled, (state, action) => { state.invoices = action.payload || [] })
      .addCase(fetchWallet.fulfilled, (state, action) => { state.wallet = action.payload })
      .addCase(fetchWalletTransactions.fulfilled, (state, action) => { state.walletTransactions = action.payload || [] })
  },
})

export default paymentsSlice.reducer
