import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import {
  getMedicalRecords, getMedicalRecord, createMedicalRecord,
  updateMedicalRecord, deleteMedicalRecord, getRecordSummary,
  getPrescriptions, createPrescription, deletePrescription,
  getLabReports, createLabReport, deleteLabReport,
  getDocuments, uploadDocument, deleteDocument,
} from '../../api/medicalRecordsApi'

// ── Thunks ──────────────────────────────────────────────────────────────────

export const fetchRecords = createAsyncThunk('medicalRecords/fetchAll',
  async ({ patientId, params }, { rejectWithValue }) => {
    try { return (await getMedicalRecords(patientId, params)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch records') }
  }
)

export const fetchRecord = createAsyncThunk('medicalRecords/fetchOne',
  async ({ patientId, id }, { rejectWithValue }) => {
    try { return (await getMedicalRecord(patientId, id)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch record') }
  }
)

export const addRecord = createAsyncThunk('medicalRecords/create',
  async ({ patientId, data }, { rejectWithValue }) => {
    try { return (await createMedicalRecord(patientId, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to create record') }
  }
)

export const editRecord = createAsyncThunk('medicalRecords/update',
  async ({ patientId, id, data }, { rejectWithValue }) => {
    try { return (await updateMedicalRecord(patientId, id, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to update record') }
  }
)

export const removeRecord = createAsyncThunk('medicalRecords/delete',
  async ({ patientId, id }, { rejectWithValue }) => {
    try { await deleteMedicalRecord(patientId, id); return id }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to delete record') }
  }
)

export const fetchSummary = createAsyncThunk('medicalRecords/summary',
  async (patientId, { rejectWithValue }) => {
    try { return (await getRecordSummary(patientId)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch summary') }
  }
)

export const fetchPrescriptions = createAsyncThunk('medicalRecords/fetchPrescriptions',
  async (recordId, { rejectWithValue }) => {
    try { return (await getPrescriptions(recordId)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch prescriptions') }
  }
)

export const addPrescription = createAsyncThunk('medicalRecords/addPrescription',
  async ({ recordId, data }, { rejectWithValue }) => {
    try { return (await createPrescription(recordId, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to add prescription') }
  }
)

export const removePrescription = createAsyncThunk('medicalRecords/removePrescription',
  async ({ recordId, id }, { rejectWithValue }) => {
    try { await deletePrescription(recordId, id); return id }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to delete prescription') }
  }
)

export const fetchLabReports = createAsyncThunk('medicalRecords/fetchLabReports',
  async (recordId, { rejectWithValue }) => {
    try { return (await getLabReports(recordId)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch lab reports') }
  }
)

export const addLabReport = createAsyncThunk('medicalRecords/addLabReport',
  async ({ recordId, data }, { rejectWithValue }) => {
    try { return (await createLabReport(recordId, data)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to add lab report') }
  }
)

export const removeLabReport = createAsyncThunk('medicalRecords/removeLabReport',
  async ({ recordId, id }, { rejectWithValue }) => {
    try { await deleteLabReport(recordId, id); return id }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to delete lab report') }
  }
)

export const fetchDocuments = createAsyncThunk('medicalRecords/fetchDocuments',
  async (recordId, { rejectWithValue }) => {
    try { return (await getDocuments(recordId)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to fetch documents') }
  }
)

export const addDocument = createAsyncThunk('medicalRecords/addDocument',
  async ({ recordId, formData }, { rejectWithValue }) => {
    try { return (await uploadDocument(recordId, formData)).data.data }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to upload document') }
  }
)

export const removeDocument = createAsyncThunk('medicalRecords/removeDocument',
  async ({ recordId, id }, { rejectWithValue }) => {
    try { await deleteDocument(recordId, id); return id }
    catch (e) { return rejectWithValue(e.response?.data?.error?.message || 'Failed to delete document') }
  }
)

// ── Slice ────────────────────────────────────────────────────────────────────

const initialState = {
  records: [],
  currentRecord: null,
  summary: null,
  prescriptions: [],
  labReports: [],
  documents: [],
  loading: false,
  error: null,
}

const medicalRecordsSlice = createSlice({
  name: 'medicalRecords',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null },
    clearCurrentRecord: (state) => { state.currentRecord = null },
  },
  extraReducers: (builder) => {
    const pending  = (state) => { state.loading = true;  state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      // Records
      .addCase(fetchRecords.pending, pending)
      .addCase(fetchRecords.fulfilled, (state, { payload }) => { state.loading = false; state.records = payload })
      .addCase(fetchRecords.rejected, rejected)

      .addCase(fetchRecord.pending, pending)
      .addCase(fetchRecord.fulfilled, (state, { payload }) => { state.loading = false; state.currentRecord = payload })
      .addCase(fetchRecord.rejected, rejected)

      .addCase(addRecord.pending, pending)
      .addCase(addRecord.fulfilled, (state, { payload }) => { state.loading = false; state.records.unshift(payload) })
      .addCase(addRecord.rejected, rejected)

      .addCase(editRecord.pending, pending)
      .addCase(editRecord.fulfilled, (state, { payload }) => {
        state.loading = false
        state.currentRecord = payload
        const idx = state.records.findIndex((r) => r.id === payload.id)
        if (idx !== -1) state.records[idx] = payload
      })
      .addCase(editRecord.rejected, rejected)

      .addCase(removeRecord.pending, pending)
      .addCase(removeRecord.fulfilled, (state, { payload }) => {
        state.loading = false
        state.records = state.records.filter((r) => r.id !== payload)
      })
      .addCase(removeRecord.rejected, rejected)

      .addCase(fetchSummary.fulfilled, (state, { payload }) => { state.summary = payload })

      // Prescriptions
      .addCase(fetchPrescriptions.fulfilled, (state, { payload }) => { state.prescriptions = payload })
      .addCase(addPrescription.fulfilled, (state, { payload }) => { state.prescriptions.unshift(payload) })
      .addCase(removePrescription.fulfilled, (state, { payload }) => {
        state.prescriptions = state.prescriptions.filter((p) => p.id !== payload)
      })

      // Lab Reports
      .addCase(fetchLabReports.fulfilled, (state, { payload }) => { state.labReports = payload })
      .addCase(addLabReport.fulfilled, (state, { payload }) => { state.labReports.unshift(payload) })
      .addCase(removeLabReport.fulfilled, (state, { payload }) => {
        state.labReports = state.labReports.filter((r) => r.id !== payload)
      })

      // Documents
      .addCase(fetchDocuments.fulfilled, (state, { payload }) => { state.documents = payload })
      .addCase(addDocument.fulfilled, (state, { payload }) => { state.documents.unshift(payload) })
      .addCase(removeDocument.fulfilled, (state, { payload }) => {
        state.documents = state.documents.filter((d) => d.id !== payload)
      })
  },
})

export const { clearError, clearCurrentRecord } = medicalRecordsSlice.actions
export default medicalRecordsSlice.reducer
