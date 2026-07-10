import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import * as familyApi from '../../api/familyApi'

// ── Profile ───────────────────────────────────────────────────────────────────

export const fetchProfile = createAsyncThunk('family/fetchProfile', async (_, { rejectWithValue }) => {
  try {
    const res = await familyApi.getProfile()
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to load profile.')
  }
})

export const updateProfile = createAsyncThunk('family/updateProfile', async (data, { rejectWithValue }) => {
  try {
    const res = await familyApi.updateProfile(data)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to update profile.')
  }
})

// ── Members ───────────────────────────────────────────────────────────────────

export const fetchMembers = createAsyncThunk('family/fetchMembers', async (_, { rejectWithValue }) => {
  try {
    const res = await familyApi.getMembers()
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to load members.')
  }
})

export const addMember = createAsyncThunk('family/addMember', async (data, { rejectWithValue }) => {
  try {
    const res = await familyApi.createMember(data)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to add member.')
  }
})

export const editMember = createAsyncThunk('family/editMember', async ({ id, data }, { rejectWithValue }) => {
  try {
    const res = await familyApi.updateMember(id, data)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to update member.')
  }
})

export const removeMember = createAsyncThunk('family/removeMember', async (id, { rejectWithValue }) => {
  try {
    await familyApi.deleteMember(id)
    return id
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to delete member.')
  }
})

// ── Emergency Contacts ────────────────────────────────────────────────────────

export const fetchContacts = createAsyncThunk('family/fetchContacts', async (_, { rejectWithValue }) => {
  try {
    const res = await familyApi.getContacts()
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to load contacts.')
  }
})

export const addContact = createAsyncThunk('family/addContact', async (data, { rejectWithValue }) => {
  try {
    const res = await familyApi.createContact(data)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to add contact.')
  }
})

export const editContact = createAsyncThunk('family/editContact', async ({ id, data }, { rejectWithValue }) => {
  try {
    const res = await familyApi.updateContact(id, data)
    return res.data.data
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to update contact.')
  }
})

export const removeContact = createAsyncThunk('family/removeContact', async (id, { rejectWithValue }) => {
  try {
    await familyApi.deleteContact(id)
    return id
  } catch (err) {
    return rejectWithValue(err.response?.data?.error?.message || 'Failed to delete contact.')
  }
})

// ── Slice ─────────────────────────────────────────────────────────────────────

const familySlice = createSlice({
  name: 'family',
  initialState: {
    profile: null,
    members: [],
    contacts: [],
    loading: false,
    error: null,
  },
  reducers: {
    clearFamilyError: (state) => { state.error = null },
  },
  extraReducers: (builder) => {
    const pending = (state) => { state.loading = true; state.error = null }
    const rejected = (state, action) => { state.loading = false; state.error = action.payload }

    builder
      .addCase(fetchProfile.pending, pending)
      .addCase(fetchProfile.fulfilled, (state, { payload }) => { state.loading = false; state.profile = payload })
      .addCase(fetchProfile.rejected, rejected)

      .addCase(updateProfile.pending, pending)
      .addCase(updateProfile.fulfilled, (state, { payload }) => { state.loading = false; state.profile = payload })
      .addCase(updateProfile.rejected, rejected)

      .addCase(fetchMembers.pending, pending)
      .addCase(fetchMembers.fulfilled, (state, { payload }) => { state.loading = false; state.members = payload })
      .addCase(fetchMembers.rejected, rejected)

      .addCase(addMember.pending, pending)
      .addCase(addMember.fulfilled, (state, { payload }) => { state.loading = false; state.members.push(payload) })
      .addCase(addMember.rejected, rejected)

      .addCase(editMember.pending, pending)
      .addCase(editMember.fulfilled, (state, { payload }) => {
        state.loading = false
        const idx = state.members.findIndex((m) => m.id === payload.id)
        if (idx !== -1) state.members[idx] = payload
      })
      .addCase(editMember.rejected, rejected)

      .addCase(removeMember.pending, pending)
      .addCase(removeMember.fulfilled, (state, { payload }) => {
        state.loading = false
        state.members = state.members.filter((m) => m.id !== payload)
      })
      .addCase(removeMember.rejected, rejected)

      .addCase(fetchContacts.pending, pending)
      .addCase(fetchContacts.fulfilled, (state, { payload }) => { state.loading = false; state.contacts = payload })
      .addCase(fetchContacts.rejected, rejected)

      .addCase(addContact.pending, pending)
      .addCase(addContact.fulfilled, (state, { payload }) => { state.loading = false; state.contacts.push(payload) })
      .addCase(addContact.rejected, rejected)

      .addCase(editContact.pending, pending)
      .addCase(editContact.fulfilled, (state, { payload }) => {
        state.loading = false
        const idx = state.contacts.findIndex((c) => c.id === payload.id)
        if (idx !== -1) state.contacts[idx] = payload
      })
      .addCase(editContact.rejected, rejected)

      .addCase(removeContact.pending, pending)
      .addCase(removeContact.fulfilled, (state, { payload }) => {
        state.loading = false
        state.contacts = state.contacts.filter((c) => c.id !== payload)
      })
      .addCase(removeContact.rejected, rejected)
  },
})

export const { clearFamilyError } = familySlice.actions
export default familySlice.reducer
