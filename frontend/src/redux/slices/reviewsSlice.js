import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import reviewsApi from '../../api/reviewsApi'

export const fetchMyReviews = createAsyncThunk('reviews/fetchMine', async (_, { rejectWithValue }) => {
  try { return (await reviewsApi.getMyReviews()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const submitReview = createAsyncThunk('reviews/submit', async (data, { rejectWithValue }) => {
  try { return (await reviewsApi.submitReview(data)).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fetchComplaints = createAsyncThunk('reviews/fetchComplaints', async (_, { rejectWithValue }) => {
  try { return (await reviewsApi.getComplaints()).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const fileComplaint = createAsyncThunk('reviews/fileComplaint', async (data, { rejectWithValue }) => {
  try { return (await reviewsApi.fileComplaint(data)).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

export const replyToReview = createAsyncThunk('reviews/replyToReview', async ({ reviewId, data }, { rejectWithValue }) => {
  try { return (await reviewsApi.replyToReview(reviewId, data)).data.data }
  catch (err) { return rejectWithValue(err.response?.data?.error?.message || 'Failed.') }
})

const reviewsSlice = createSlice({
  name: 'reviews',
  initialState: { reviews: [], complaints: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchMyReviews.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchMyReviews.fulfilled, (state, action) => { state.loading = false; state.reviews = action.payload || [] })
      .addCase(fetchMyReviews.rejected, (state, action) => { state.loading = false; state.error = action.payload })
      .addCase(submitReview.fulfilled, (state, action) => { state.reviews.unshift(action.payload) })
      .addCase(replyToReview.fulfilled, (state, action) => {
        const reply = action.payload
        const review = state.reviews.find(r => r.id === reply.review)
        if (review) review.reply = reply
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => { state.complaints = action.payload || [] })
      .addCase(fileComplaint.fulfilled, (state, action) => { state.complaints.unshift(action.payload) })
  },
})

export default reviewsSlice.reducer
