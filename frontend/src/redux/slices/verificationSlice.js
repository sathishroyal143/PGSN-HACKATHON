import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import verificationApi from '../../api/verificationApi'

export const fetchDocuments = createAsyncThunk('verification/fetchDocs', async (_, { rejectWithValue }) => {
  try { return (await verificationApi.getDocuments()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const uploadDocument = createAsyncThunk('verification/upload', async (formData, { rejectWithValue }) => {
  try { return (await verificationApi.uploadDocument(formData)).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fetchKYC = createAsyncThunk('verification/fetchKYC', async (_, { rejectWithValue }) => {
  try { return (await verificationApi.getKYC()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

const verificationSlice = createSlice({
  name: 'verification',
  initialState: { documents: [], kyc: null, loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDocuments.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchDocuments.fulfilled, (state, action) => { state.loading = false; state.documents = action.payload || [] })
      .addCase(fetchDocuments.rejected, (state, action) => { state.loading = false; state.error = action.payload })
      .addCase(uploadDocument.fulfilled, (state, action) => { state.documents.unshift(action.payload) })
      .addCase(fetchKYC.fulfilled, (state, action) => { state.kyc = action.payload })
  },
})

export default verificationSlice.reducer
