import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Star, AlertCircle, Plus, MessageSquare, ShieldAlert, CheckCircle2, User } from 'lucide-react'
import { fetchMyReviews, fetchComplaints, fileComplaint, submitReview, replyToReview } from '../../redux/slices/reviewsSlice'
import { fetchBookings } from '../../redux/slices/bookingsSlice'

const STAR_COLORS = { 5: 'text-amber-400', 4: 'text-amber-400', 3: 'text-amber-500', 2: 'text-orange-400', 1: 'text-rose-400' }
const STATUS_COLORS = {
  open: 'bg-rose-50 text-rose-700 border-rose-200', 
  in_progress: 'bg-amber-50 text-amber-700 border-amber-200',
  resolved: 'bg-emerald-50 text-emerald-700 border-emerald-200', 
  closed: 'bg-gray-50 text-gray-600 border-gray-200',
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}

export default function ReviewsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { reviews, complaints, loading, error } = useSelector((s) => s.reviews)
  const { bookings } = useSelector((s) => s.bookings)
  const { user } = useSelector((s) => s.auth)
  const role = user?.role?.toLowerCase() || 'family'
  
  const [tab, setTab] = useState('reviews')
  const [showForm, setShowForm] = useState(false) // For complaints
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [form, setForm] = useState({ booking_id: '', against_id: '', subject: '', description: '', priority: 'medium' })
  const [reviewForm, setReviewForm] = useState({ booking_id: '', rating: 5, title: '', comment: '' })
  const [submitting, setSubmitting] = useState(false)
  const [replyingTo, setReplyingTo] = useState(null)
  const [replyComment, setReplyComment] = useState('')

  useEffect(() => {
    dispatch(fetchMyReviews())
    dispatch(fetchComplaints())
    if (role === 'family' || role === 'companion') {
      dispatch(fetchBookings())
    }
  }, [dispatch, role])

  const eligibleBookings = bookings.filter(b => b.status === 'COMPLETED' && b.companion_id && !reviews.some(r => r.booking === b.id))
  const eligibleBookingsForComplaint = bookings.filter(b => b.status === 'COMPLETED' && !complaints.some(c => c.booking === b.id))

  async function handleComplaint(e) {
    e.preventDefault()
    setSubmitting(true)
    const payload = { ...form }
    const booking = eligibleBookingsForComplaint.find(b => b.id === payload.booking_id)
    if (booking) {
      if (role === 'family' && booking.companion_id) {
        payload.against_id = booking.companion_id
      } else if (role === 'companion' && booking.family_user_id) {
        payload.against_id = booking.family_user_id
      } else {
        delete payload.against_id
      }
    }
    await dispatch(fileComplaint(payload))
    setSubmitting(false)
    setShowForm(false)
    setForm({ booking_id: '', against_id: '', subject: '', description: '', priority: 'medium' })
  }

  async function handleReviewSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    const booking = eligibleBookings.find(b => b.id === reviewForm.booking_id)
    if (booking) {
       await dispatch(submitReview({
         booking_id: booking.id,
         reviewee_id: booking.companion_id,
         rating: parseInt(reviewForm.rating, 10),
         title: reviewForm.title,
         comment: reviewForm.comment
       }))
    }
    setSubmitting(false)
    setShowReviewForm(false)
    setReviewForm({ booking_id: '', rating: 5, title: '', comment: '' })
  }

  async function handleReplySubmit(e, reviewId) {
    e.preventDefault()
    setSubmitting(true)
    await dispatch(replyToReview({ reviewId, data: { comment: replyComment } }))
    setSubmitting(false)
    setReplyingTo(null)
    setReplyComment('')
  }

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Feedback & Support</h1>
          <p className="text-gray-500 mt-1 font-medium">Manage your reviews and track support complaints.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setTab('reviews')}
          className={`pb-4 px-2 text-sm font-bold transition-all relative ${tab === 'reviews' ? 'text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
        >
          <div className="flex items-center gap-2">
            <Star size={18} />
            Reviews
            <span className="bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">{reviews.length}</span>
          </div>
          {tab === 'reviews' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-primary-600 rounded-t-full" />}
        </button>

        <button
          onClick={() => setTab('complaints')}
          className={`pb-4 px-2 text-sm font-bold transition-all relative ${tab === 'complaints' ? 'text-rose-600' : 'text-gray-500 hover:text-gray-700'}`}
        >
          <div className="flex items-center gap-2">
            <AlertCircle size={18} />
            Complaints
            <span className="bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">{complaints.length}</span>
          </div>
          {tab === 'complaints' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-rose-600 rounded-t-full" />}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-center font-semibold">
          {error}
        </div>
      )}

      {/* Reviews tab */}
      {tab === 'reviews' && (
        <div className="space-y-6">
          {role === 'family' && eligibleBookings.length > 0 && (
            <div className="bg-gradient-to-r from-primary-50 to-indigo-50 border border-primary-100 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="font-bold text-gray-900 text-lg">Leave a Review</h3>
                <p className="text-gray-600 text-sm font-medium mt-1">You have {eligibleBookings.length} completed booking(s) waiting for feedback.</p>
              </div>
              <button
                onClick={() => setShowReviewForm(!showReviewForm)}
                className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-colors shadow-sm flex items-center gap-2 whitespace-nowrap"
              >
                {showReviewForm ? 'Cancel' : <><Plus size={18} /> Write Review</>}
              </button>
            </div>
          )}

          {showReviewForm && (
            <form onSubmit={handleReviewSubmit} className="bg-white border border-gray-200 rounded-2xl p-6 space-y-5 shadow-sm animate-in fade-in slide-in-from-top-4 duration-300">
              <h3 className="font-bold text-xl text-gray-900">New Review</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1.5">Select Assignment</label>
                  <select
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                    value={reviewForm.booking_id}
                    onChange={(e) => setReviewForm({ ...reviewForm, booking_id: e.target.value })}
                    required
                  >
                    <option value="">Select a completed booking...</option>
                    {eligibleBookings.map(b => (
                      <option key={b.id} value={b.id}>
                        {fmt(b.created_at)} - Companion: {b.companion_name} ({b.service_name}) [Patient: {b.patient_name}]
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1.5">Rating</label>
                  <div className="flex gap-2">
                    {[1,2,3,4,5].map((star) => (
                      <button
                        type="button"
                        key={star}
                        onClick={() => setReviewForm({ ...reviewForm, rating: star })}
                        className={`p-2 rounded-xl border transition-all ${
                          reviewForm.rating >= star 
                            ? 'bg-amber-50 border-amber-200 text-amber-500' 
                            : 'bg-white border-gray-200 text-gray-300 hover:border-amber-200 hover:text-amber-200'
                        }`}
                      >
                        <Star size={24} fill="currentColor" />
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1.5">Review Title (Optional)</label>
                  <input
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                    placeholder="E.g., Great care provided!"
                    value={reviewForm.title}
                    onChange={(e) => setReviewForm({ ...reviewForm, title: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1.5">Feedback</label>
                  <textarea
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                    placeholder="Share details about your experience..."
                    rows={4}
                    value={reviewForm.comment}
                    onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={submitting || !reviewForm.booking_id}
                  className="px-8 py-3 bg-gradient-to-r from-primary-600 to-indigo-600 text-white rounded-xl font-bold transition-all hover:shadow-lg disabled:opacity-50"
                >
                  {submitting ? 'Submitting…' : 'Publish Review'}
                </button>
              </div>
            </form>
          )}

          {loading && !reviews.length ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
            </div>
          ) : reviews.length === 0 ? (
            <div className="text-center py-24 bg-white border border-dashed border-gray-200 rounded-3xl">
              <div className="bg-gray-50 p-6 rounded-full inline-block mb-4">
                <Star size={48} className="text-gray-300" />
              </div>
              <h3 className="font-bold text-gray-900 text-xl">No Reviews Yet</h3>
              <p className="text-gray-500 mt-2">Reviews left by you or about you will appear here.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {reviews.map((r) => (
                <div key={r.id} className="bg-white border border-gray-100 hover:border-primary-200 rounded-3xl p-6 shadow-sm hover:shadow-xl transition-all group flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-1 bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-100">
                      <span className="font-bold text-amber-600 text-sm mr-1">{r.rating}.0</span>
                      {[1,2,3,4,5].map((s) => (
                        <Star key={s} size={14} className={s <= r.rating ? STAR_COLORS[r.rating] : 'text-gray-300'} fill={s <= r.rating ? 'currentColor' : 'none'} />
                      ))}
                    </div>
                    <span className="text-xs font-semibold text-gray-400">{fmt(r.created_at)}</span>
                  </div>
                  
                  {r.title && <h4 className="font-bold text-gray-900 text-lg mb-2">{r.title}</h4>}
                  <p className="text-gray-600 text-sm leading-relaxed flex-1">{r.comment}</p>
                  
                  <div className="w-full h-px bg-gray-100 my-4" />

                  {r.reply ? (
                    <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
                      <div className="flex items-center gap-2 mb-2">
                        <MessageSquare size={14} className="text-primary-500" />
                        <span className="font-bold text-xs text-gray-700 uppercase tracking-wider">Reply</span>
                      </div>
                      <p className="text-sm text-gray-600 italic">"{r.reply.comment}"</p>
                    </div>
                  ) : role === 'companion' && (
                    <div>
                      {replyingTo === r.id ? (
                        <form onSubmit={(e) => handleReplySubmit(e, r.id)} className="space-y-3 animate-in fade-in duration-200">
                          <textarea
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                            placeholder="Write your reply..."
                            rows={3}
                            value={replyComment}
                            onChange={(e) => setReplyComment(e.target.value)}
                            required
                          />
                          <div className="flex gap-2 justify-end">
                            <button type="button" onClick={() => { setReplyingTo(null); setReplyComment('') }} className="px-4 py-2 bg-white border border-gray-200 text-gray-700 text-sm font-bold rounded-xl hover:bg-gray-50 transition-colors">Cancel</button>
                            <button type="submit" disabled={submitting} className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-bold rounded-xl transition-colors">Post Reply</button>
                          </div>
                        </form>
                      ) : (
                        <button onClick={() => setReplyingTo(r.id)} className="text-sm font-bold text-primary-600 hover:text-primary-700 flex items-center gap-1">
                          <MessageSquare size={16} /> Reply to Review
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Complaints tab */}
      {tab === 'complaints' && (
        <div className="space-y-6">
          {eligibleBookingsForComplaint.length > 0 && (
            <div className="bg-gradient-to-r from-rose-50 to-red-50 border border-rose-100 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="font-bold text-gray-900 text-lg">Need Support?</h3>
                <p className="text-gray-600 text-sm font-medium mt-1">File a complaint or report an issue regarding a completed assignment.</p>
              </div>
              <button
                onClick={() => setShowForm(!showForm)}
                className="bg-rose-600 hover:bg-rose-700 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-colors shadow-sm flex items-center gap-2 whitespace-nowrap"
              >
                {showForm ? 'Cancel' : <><AlertCircle size={18} /> File Complaint</>}
              </button>
            </div>
          )}

          {showForm && (
            <form onSubmit={handleComplaint} className="bg-white border border-gray-200 rounded-2xl p-6 space-y-5 shadow-sm animate-in fade-in slide-in-from-top-4 duration-300">
              <h3 className="font-bold text-xl text-gray-900">File a Complaint</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1.5">Select Assignment</label>
                  <select
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 outline-none transition-all"
                    value={form.booking_id}
                    onChange={(e) => setForm({ ...form, booking_id: e.target.value })}
                    required
                  >
                    <option value="" disabled>Select a Booking</option>
                    {eligibleBookingsForComplaint.map(b => (
                      <option key={b.id} value={b.id}>
                        {fmt(b.created_at)} - {b.service_name || 'Care Booking'} [Patient: {b.patient_name}]
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1.5">Subject</label>
                    <input
                      className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 outline-none transition-all"
                      placeholder="Brief description of the issue"
                      value={form.subject}
                      onChange={(e) => setForm({ ...form, subject: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1.5">Priority Level</label>
                    <select
                      className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 outline-none transition-all"
                      value={form.priority}
                      onChange={(e) => setForm({ ...form, priority: e.target.value })}
                    >
                      <option value="low">Low Priority</option>
                      <option value="medium">Medium Priority</option>
                      <option value="high">High Priority</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-1.5">Detailed Description</label>
                  <textarea
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium text-gray-900 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 outline-none transition-all"
                    placeholder="Please provide as much detail as possible..."
                    rows={5}
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-8 py-3 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold transition-all hover:shadow-lg disabled:opacity-50"
                >
                  {submitting ? 'Submitting…' : 'Submit Complaint'}
                </button>
              </div>
            </form>
          )}

          {complaints.length === 0 && !loading ? (
            <div className="text-center py-24 bg-white border border-dashed border-gray-200 rounded-3xl">
              <div className="bg-gray-50 p-6 rounded-full inline-block mb-4">
                <ShieldAlert size={48} className="text-gray-300" />
              </div>
              <h3 className="font-bold text-gray-900 text-xl">No Complaints</h3>
              <p className="text-gray-500 mt-2">Any support tickets or complaints you file will appear here.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {complaints.map((c) => {
                const booking = bookings.find(b => b.id === c.booking)
                let againstText = null
                if (booking) {
                  if (role === 'family' && booking.companion_name) {
                    againstText = `Companion: ${booking.companion_name}`
                  } else if (role === 'companion' && booking.patient_name) {
                    againstText = `Patient: ${booking.patient_name}`
                  }
                }
                return (
                  <div key={c.id} className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm hover:shadow-md transition-all flex flex-col">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h4 className="font-bold text-gray-900 text-lg leading-tight">{c.subject}</h4>
                        <p className="text-xs font-semibold text-gray-400 mt-1">Filed on {fmt(c.created_at)}</p>
                      </div>
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border capitalize whitespace-nowrap ${STATUS_COLORS[c.status] || 'bg-gray-50 text-gray-600'}`}>
                        {c.status.replace('_', ' ')}
                      </span>
                    </div>
                    
                    <p className="text-gray-600 text-sm leading-relaxed bg-gray-50 rounded-xl p-4 mb-4">{c.description}</p>
                    
                    <div className="flex items-center justify-between text-xs font-bold mt-auto pt-4 border-t border-gray-100">
                      <div className="flex items-center gap-4">
                        <span className={`px-2 py-1 rounded-md ${
                          c.priority === 'high' ? 'bg-rose-50 text-rose-600' : 
                          c.priority === 'medium' ? 'bg-amber-50 text-amber-600' : 'bg-gray-100 text-gray-600'
                        } uppercase tracking-wider`}>
                          {c.priority} priority
                        </span>
                        {againstText && (
                          <span className="flex items-center gap-1 text-gray-500">
                            <User size={14} /> {againstText}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    {c.resolution_notes && (
                      <div className="mt-4 bg-emerald-50 rounded-2xl p-4 border border-emerald-100">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle2 size={16} className="text-emerald-600" />
                          <span className="font-bold text-xs text-emerald-800 uppercase tracking-wider">Resolution Notes</span>
                        </div>
                        <p className="text-sm text-emerald-700 font-medium">{c.resolution_notes}</p>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
