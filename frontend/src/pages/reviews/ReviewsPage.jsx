import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Star, AlertCircle, Plus } from 'lucide-react'
import { fetchMyReviews, fetchComplaints, fileComplaint, submitReview, replyToReview } from '../../redux/slices/reviewsSlice'
import { fetchBookings } from '../../redux/slices/bookingsSlice'

const STAR_COLORS = { 5: 'text-yellow-400', 4: 'text-yellow-400', 3: 'text-yellow-500', 2: 'text-orange-400', 1: 'text-red-400' }
const STATUS_COLORS = {
  open: 'bg-red-100 text-red-700', in_progress: 'bg-yellow-100 text-yellow-700',
  resolved: 'bg-green-100 text-green-700', closed: 'bg-gray-100 text-gray-500',
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
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Reviews & Complaints</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        {['reviews', 'complaints'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`pb-2 px-3 text-sm font-medium capitalize border-b-2 transition-colors ${tab === t ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            {t} {t === 'reviews' ? `(${reviews.length})` : `(${complaints.length})`}
          </button>
        ))}
      </div>

      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>}

      {/* Reviews tab */}
      {tab === 'reviews' && (
        <div className="space-y-3">
          {role === 'family' && eligibleBookings.length > 0 && (
            <button
              onClick={() => setShowReviewForm(!showReviewForm)}
              className="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center justify-center gap-2"
            >
              <Plus size={16} /> {showReviewForm ? 'Cancel' : 'Write a Review'}
            </button>
          )}

          {showReviewForm && (
            <form onSubmit={handleReviewSubmit} className="bg-white border border-gray-200 rounded-lg p-4 space-y-3 shadow-sm">
              <h3 className="font-medium text-gray-900">Write a Review</h3>
              <select
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
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
              
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Rating:</span>
                <select
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  value={reviewForm.rating}
                  onChange={(e) => setReviewForm({ ...reviewForm, rating: e.target.value })}
                  required
                >
                  <option value="5">5 - Excellent</option>
                  <option value="4">4 - Good</option>
                  <option value="3">3 - Average</option>
                  <option value="2">2 - Poor</option>
                  <option value="1">1 - Terrible</option>
                </select>
              </div>

              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="Review Title (Optional)"
                value={reviewForm.title}
                onChange={(e) => setReviewForm({ ...reviewForm, title: e.target.value })}
              />
              <textarea
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="Share your experience with the companion..."
                rows={3}
                value={reviewForm.comment}
                onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                required
              />
              <button
                type="submit"
                disabled={submitting || !reviewForm.booking_id}
                className="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Submitting…' : 'Submit Review'}
              </button>
            </form>
          )}

          {loading && !reviews.length ? (
            <p className="text-center text-gray-400 py-10">Loading…</p>
          ) : reviews.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <Star size={40} className="mx-auto mb-3 opacity-40" />
              <p>No reviews given yet.</p>
            </div>
          ) : reviews.map((r) => (
            <div key={r.id} className="bg-white border border-gray-200 rounded-lg p-4 space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  {[1,2,3,4,5].map((s) => (
                    <Star key={s} size={14} className={s <= r.rating ? STAR_COLORS[r.rating] : 'text-gray-200'} fill={s <= r.rating ? 'currentColor' : 'none'} />
                  ))}
                  <span className="text-xs text-gray-500 ml-1">{r.rating}/5</span>
                </div>
                <span className="text-xs text-gray-400">{fmt(r.created_at)}</span>
              </div>
              {r.title && <p className="text-sm font-medium text-gray-800">{r.title}</p>}
              {r.comment && <p className="text-sm text-gray-600">{r.comment}</p>}
              {r.reply ? (
                <div className="mt-2 bg-gray-50 rounded p-2 text-xs text-gray-600 border-l-2 border-blue-300">
                  <span className="font-medium">Reply: </span>{r.reply.comment}
                </div>
              ) : role === 'companion' && (
                <div className="mt-2">
                  {replyingTo === r.id ? (
                    <form onSubmit={(e) => handleReplySubmit(e, r.id)} className="space-y-2">
                      <textarea
                        className="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm"
                        placeholder="Write your reply..."
                        rows={2}
                        value={replyComment}
                        onChange={(e) => setReplyComment(e.target.value)}
                        required
                      />
                      <div className="flex gap-2">
                        <button type="submit" disabled={submitting} className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">Submit</button>
                        <button type="button" onClick={() => { setReplyingTo(null); setReplyComment('') }} className="px-3 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300">Cancel</button>
                      </div>
                    </form>
                  ) : (
                    <button onClick={() => setReplyingTo(r.id)} className="text-sm text-blue-600 hover:underline">
                      + Reply to review
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Complaints tab */}
      {tab === 'complaints' && (
        <div className="space-y-3">
          {eligibleBookingsForComplaint.length > 0 && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="w-full py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700"
            >
              {showForm ? 'Cancel' : '+ File a Complaint'}
            </button>
          )}

          {showForm && (
            <form onSubmit={handleComplaint} className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
              <select
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
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
              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="Subject"
                value={form.subject}
                onChange={(e) => setForm({ ...form, subject: e.target.value })}
                required
              />
              <textarea
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="Description"
                rows={3}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                required
              />
              <select
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
              >
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
              </select>
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50"
              >
                {submitting ? 'Submitting…' : 'Submit Complaint'}
              </button>
            </form>
          )}

          {complaints.length === 0 && !loading ? (
            <div className="text-center py-16 text-gray-400">
              <AlertCircle size={40} className="mx-auto mb-3 opacity-40" />
              <p>No complaints filed.</p>
            </div>
          ) : complaints.map((c) => {
            const booking = bookings.find(b => b.id === c.booking)
            let againstText = null
            if (booking) {
              if (role === 'family' && booking.companion_name) {
                againstText = `Against Companion: ${booking.companion_name}`
              } else if (role === 'companion' && booking.patient_name) {
                againstText = `Against Patient: ${booking.patient_name}`
              }
            }
            return (
              <div key={c.id} className="bg-white border border-gray-200 rounded-lg p-4 space-y-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-900">{c.subject}</p>
                  {againstText && (
                    <span className="text-xs font-semibold px-2 py-1 bg-red-50 text-red-700 rounded border border-red-100 whitespace-nowrap ml-2">
                      {againstText}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500">{c.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span className="capitalize">Priority: {c.priority}</span>
                  <span>{fmt(c.created_at)}</span>
                </div>
                {c.resolution_notes && (
                  <div className="mt-1 bg-green-50 rounded p-2 text-xs text-green-700 border-l-2 border-green-400">
                    <span className="font-medium">Resolution: </span>{c.resolution_notes}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
