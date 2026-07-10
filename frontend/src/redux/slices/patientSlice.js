import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import * as patientApi from '../../api/patientApi'

const err = (e) => e.response?.data?.error?.message || 'Something went wrong.'

// ── Patients ──────────────────────────────────────────────────────────────────
export const fetchPatients = createAsyncThunk('patient/fetchPatients', async (_, { rejectWithValue }) => {
  try { return (await patientApi.getPatients()).data.data }
  catch (e) { return rejectWithValue(err(e)) }
})

export const fetchPatient = createAsyncThunk('patient/fetchPatient', async (id, { rejectWithValue }) => {
  try { return (await patientApi.getPatient(id)).data.data }
  catch (e) { return rejectWithValue(err(e)) }
})

export const createPatient = createAsyncThunk('patient/createPatient', async (data, { rejectWithValue }) => {
  try { return (await patientApi.createPatient(data)).data.data }
  catch (e) { return rejectWithValue(err(e)) }
})

export const updatePatient = createAsyncThunk('patient/updatePatient', async ({ id, data }, { rejectWithValue }) => {
  try { return (await patientApi.updatePatient(id, data)).data.data }
  catch (e) { return rejectWithValue(err(e)) }
})

export const deletePatient = createAsyncThunk('patient/deletePatient', async (id, { rejectWithValue }) => {
  try { await patientApi.deletePatient(id); return id }
  catch (e) { return rejectWithValue(err(e)) }
})

export const setPrimary = createAsyncThunk('patient/setPrimary', async (id, { rejectWithValue }) => {
  try { await patientApi.setPrimaryPatient(id); return id }
  catch (e) { return rejectWithValue(err(e)) }
})

// ── Vitals ────────────────────────────────────────────────────────────────────
export const fetchVitals = createAsyncThunk('patient/fetchVitals', async (patientId, { rejectWithValue }) => {
  try { return { patientId, vitals: (await patientApi.getVitals(patientId)).data.data } }
  catch (e) { return rejectWithValue(err(e)) }
})

export const recordVital = createAsyncThunk('patient/recordVital', async ({ patientId, data }, { rejectWithValue }) => {
  try { return { patientId, vital: (await patientApi.recordVital(patientId, data)).data.data } }
  catch (e) { return rejectWithValue(err(e)) }
})

export const deleteVital = createAsyncThunk('patient/deleteVital', async ({ patientId, vitalId }, { rejectWithValue }) => {
  try { await patientApi.deleteVital(patientId, vitalId); return { patientId, vitalId } }
  catch (e) { return rejectWithValue(err(e)) }
})

// ── Insurance ─────────────────────────────────────────────────────────────────
export const fetchInsurance = createAsyncThunk('patient/fetchInsurance', async (patientId, { rejectWithValue }) => {
  try { return { patientId, records: (await patientApi.getInsurance(patientId)).data.data } }
  catch (e) { return rejectWithValue(err(e)) }
})

export const addInsurance = createAsyncThunk('patient/addInsurance', async ({ patientId, data }, { rejectWithValue }) => {
  try { return { patientId, record: (await patientApi.addInsurance(patientId, data)).data.data } }
  catch (e) { return rejectWithValue(err(e)) }
})

export const updateInsurance = createAsyncThunk('patient/updateInsurance', async ({ patientId, insuranceId, data }, { rejectWithValue }) => {
  try { return { patientId, record: (await patientApi.updateInsurance(patientId, insuranceId, data)).data.data } }
  catch (e) { return rejectWithValue(err(e)) }
})

export const deleteInsurance = createAsyncThunk('patient/deleteInsurance', async ({ patientId, insuranceId }, { rejectWithValue }) => {
  try { await patientApi.deleteInsurance(patientId, insuranceId); return { patientId, insuranceId } }
  catch (e) { return rejectWithValue(err(e)) }
})

// ── Slice ─────────────────────────────────────────────────────────────────────
const patientSlice = createSlice({
  name: 'patient',
  initialState: {
    list: [],
    current: null,
    vitals: {},      // keyed by patientId
    insurance: {},   // keyed by patientId
    loading: false,
    error: null,
  },
  reducers: {
    clearPatientError: (state) => { state.error = null },
    clearCurrent: (state) => { state.current = null },
  },
  extraReducers: (builder) => {
    const pending = (state) => { state.loading = true; state.error = null }
    const rejected = (state, { payload }) => { state.loading = false; state.error = payload }

    builder
      // patients
      .addCase(fetchPatients.pending, pending)
      .addCase(fetchPatients.fulfilled, (state, { payload }) => { state.loading = false; state.list = payload })
      .addCase(fetchPatients.rejected, rejected)

      .addCase(fetchPatient.pending, pending)
      .addCase(fetchPatient.fulfilled, (state, { payload }) => { state.loading = false; state.current = payload })
      .addCase(fetchPatient.rejected, rejected)

      .addCase(createPatient.pending, pending)
      .addCase(createPatient.fulfilled, (state, { payload }) => { state.loading = false; state.list.push(payload) })
      .addCase(createPatient.rejected, rejected)

      .addCase(updatePatient.pending, pending)
      .addCase(updatePatient.fulfilled, (state, { payload }) => {
        state.loading = false
        const idx = state.list.findIndex((p) => p.id === payload.id)
        if (idx !== -1) state.list[idx] = payload
        if (state.current?.id === payload.id) state.current = payload
      })
      .addCase(updatePatient.rejected, rejected)

      .addCase(deletePatient.pending, pending)
      .addCase(deletePatient.fulfilled, (state, { payload }) => {
        state.loading = false
        state.list = state.list.filter((p) => p.id !== payload)
        if (state.current?.id === payload) state.current = null
      })
      .addCase(deletePatient.rejected, rejected)

      .addCase(setPrimary.pending, pending)
      .addCase(setPrimary.fulfilled, (state, { payload }) => {
        state.loading = false
        state.list = state.list.map((p) => ({ ...p, is_primary: p.id === payload }))
        if (state.current) state.current.is_primary = state.current.id === payload
      })
      .addCase(setPrimary.rejected, rejected)

      // vitals
      .addCase(fetchVitals.pending, pending)
      .addCase(fetchVitals.fulfilled, (state, { payload }) => {
        state.loading = false
        state.vitals[payload.patientId] = payload.vitals
      })
      .addCase(fetchVitals.rejected, rejected)

      .addCase(recordVital.pending, pending)
      .addCase(recordVital.fulfilled, (state, { payload }) => {
        state.loading = false
        const existing = state.vitals[payload.patientId] || []
        state.vitals[payload.patientId] = [payload.vital, ...existing]
      })
      .addCase(recordVital.rejected, rejected)

      .addCase(deleteVital.pending, pending)
      .addCase(deleteVital.fulfilled, (state, { payload }) => {
        state.loading = false
        const existing = state.vitals[payload.patientId] || []
        state.vitals[payload.patientId] = existing.filter((v) => v.id !== payload.vitalId)
      })
      .addCase(deleteVital.rejected, rejected)

      // insurance
      .addCase(fetchInsurance.pending, pending)
      .addCase(fetchInsurance.fulfilled, (state, { payload }) => {
        state.loading = false
        state.insurance[payload.patientId] = payload.records
      })
      .addCase(fetchInsurance.rejected, rejected)

      .addCase(addInsurance.pending, pending)
      .addCase(addInsurance.fulfilled, (state, { payload }) => {
        state.loading = false
        const existing = state.insurance[payload.patientId] || []
        state.insurance[payload.patientId] = [payload.record, ...existing]
      })
      .addCase(addInsurance.rejected, rejected)

      .addCase(updateInsurance.pending, pending)
      .addCase(updateInsurance.fulfilled, (state, { payload }) => {
        state.loading = false
        const records = state.insurance[payload.patientId] || []
        const idx = records.findIndex((r) => r.id === payload.record.id)
        if (idx !== -1) records[idx] = payload.record
      })
      .addCase(updateInsurance.rejected, rejected)

      .addCase(deleteInsurance.pending, pending)
      .addCase(deleteInsurance.fulfilled, (state, { payload }) => {
        state.loading = false
        const records = state.insurance[payload.patientId] || []
        state.insurance[payload.patientId] = records.filter((r) => r.id !== payload.insuranceId)
      })
      .addCase(deleteInsurance.rejected, rejected)
  },
})

export const { clearPatientError, clearCurrent } = patientSlice.actions
export default patientSlice.reducer
