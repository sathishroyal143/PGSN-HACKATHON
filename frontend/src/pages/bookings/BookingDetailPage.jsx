import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom'
import { fetchBooking, cancelBookingThunk } from '../../redux/slices/bookingsSlice'

const STATUS_COLOR = {
  PENDING:     'bg-yellow-100 text-yellow-800',
  CONFIRMED:   'bg-blue-100 text-blue-800',
  IN_PROGRESS: 'bg-indigo-100 text-indigo-800',
  COMPLETED:   'bg-green-100 text-green-800',
  CANCELLED:   'bg-red-100 text-red-800',
  NO_SHOW:     'bg-gray-100 text-gray-600',
}

const CANCELLABLE = ['PENDING', 'CONFIRMED']

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

function Row({ label, value }) {
  if (!value && value !== 0) return null
  return (
    <div className="flex justify-between py-1.5 border-b border-gray-50 last:border-0">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-sm text-gray-800 font-medium text-right max-w-xs">{value}</span>
    </div>
  )
}

export default function BookingDetailPage() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { currentBooking: b, loading, error } = useSelector((s) => s.bookings)
  const [cancelReason, setCancelReason] = useState('')
  const [showCancel, setShowCancel] = useState(false)
  const location = useLocation()
  const prefix = '/' + location.pathname.split('/')[1]

  useEffect(() => {
    dispatch(fetchBooking(id))
  }, [dispatch, id])

  const handleCancel = async () => {
    if (!cancelReason.trim()) return
    await dispatch(cancelBookingThunk({ id, reason: cancelReason }))
    setShowCancel(false)
  }

  if (loading && !b) return <div className="p-6 text-center text-gray-500">Loading…</div>
  if (error) return <div className="p-6 text-center text-red-500">{error}</div>
  if (!b) return null

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-5">
      <button 
        onClick={() => navigate(prefix === '/companion' ? `${prefix}/requests/accepted` : `${prefix}/bookings`)} 
        className="text-sm text-blue-600 hover:underline"
      >
        ← Back
      </button>

      {/* Quick links */}
      <div className="flex gap-4 flex-wrap">

        {['CONFIRMED', 'IN_PROGRESS'].includes(b.status) && prefix !== '/companion' && (
          <Link to={`${prefix}/tracking/${b.id}`} className="text-sm text-green-600 hover:underline">
            📍 Live Tracking →
          </Link>
        )}
        {['IN_PROGRESS', 'COMPLETED'].includes(b.status) && (
          <Link to={prefix === '/companion' ? `/companion/journey/${b.id}` : `${prefix}/journeys/${b.id}`} className="text-sm text-blue-600 hover:underline">
            🏥 Care Journey →
          </Link>
        )}
        {b.companion_profile_id && prefix === '/family' && (
          <Link to={`/family/companions/${b.companion_profile_id}`} className="text-sm text-indigo-600 hover:underline">
            👤 View Companion →
          </Link>
        )}
      </div>

      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{b.service_name}</h1>
            <p className="text-sm text-gray-500 mt-0.5">Booking #{b.id?.slice(0, 8)}</p>
          </div>
          <span className={`shrink-0 px-3 py-1 rounded-full text-sm font-medium ${STATUS_COLOR[b.status] || 'bg-gray-100 text-gray-600'}`}>
            {b.status?.replace('_', ' ')}
          </span>
        </div>

        <div className="mt-4 space-y-0.5">
          <Row label="Patient"       value={b.patient_name} />
          <Row label="Companion"     value={b.companion_name} />
          <Row label="Booking Type"  value={b.booking_type} />
          <Row label="Scheduled Start" value={fmt(b.scheduled_start)} />
          <Row label="Scheduled End"   value={fmt(b.scheduled_end)} />
          {b.actual_start && <Row label="Actual Start" value={fmt(b.actual_start)} />}
          {b.actual_end   && <Row label="Actual End"   value={fmt(b.actual_end)} />}
          <Row label="Duration"      value={b.duration_hours ? `${b.duration_hours}h` : null} />
        </div>
      </div>

      {/* Location */}
      {(b.pickup_address || b.hospital_name) && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h2 className="font-semibold text-gray-800 mb-3">Location</h2>
          <div className="space-y-0.5">
            <Row label="Pickup Address" value={b.pickup_address} />
            {b.hospital_name    && <Row label="Hospital"         value={b.hospital_name} />}
            {b.hospital_address && <Row label="Hospital Address" value={b.hospital_address} />}
          </div>
        </div>
      )}

      {/* Pricing */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="font-semibold text-gray-800 mb-3">Pricing</h2>
        <div className="space-y-0.5">
          <Row label="Quoted Price" value={b.quoted_price ? `₹${b.quoted_price}` : null} />
          <Row label="Final Price"  value={b.final_price  ? `₹${b.final_price}`  : null} />
        </div>
        {b.price_breakdown && Object.keys(b.price_breakdown).length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-500 mb-1">Breakdown</p>
            {Object.entries(b.price_breakdown).map(([k, v]) => (
              <div key={k} className="flex justify-between text-xs text-gray-600 py-0.5">
                <span className="capitalize">{k.replace(/_/g, ' ')}</span>
                <span>₹{v}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Special Requirements */}
      {(b.special_instructions || b.requires_wheelchair || b.requires_oxygen) && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h2 className="font-semibold text-gray-800 mb-3">Special Requirements</h2>
          {b.requires_wheelchair && <p className="text-sm text-gray-700">♿ Wheelchair required</p>}
          {b.requires_oxygen     && <p className="text-sm text-gray-700">🫁 Oxygen required</p>}
          {b.special_instructions && <p className="text-sm text-gray-700 mt-1">{b.special_instructions}</p>}
        </div>
      )}

      {/* Status Log */}
      {b.status_logs?.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h2 className="font-semibold text-gray-800 mb-3">Status History</h2>
          <div className="space-y-2">
            {b.status_logs.map((log) => (
              <div key={log.id} className="flex items-start gap-3 text-sm">
                <span className="text-gray-400 text-xs mt-0.5 shrink-0">{fmt(log.created_at)}</span>
                <span className="text-gray-700">
                  <span className="font-medium">{log.from_status}</span>
                  {' → '}
                  <span className="font-medium">{log.to_status}</span>
                  {log.changed_by_name && <span className="text-gray-500"> by {log.changed_by_name}</span>}
                  {log.notes && <span className="text-gray-500"> — {log.notes}</span>}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cancellation info */}
      {b.status === 'CANCELLED' && b.cancellation_reason && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm font-medium text-red-700">Cancellation Reason</p>
          <p className="text-sm text-red-600 mt-1">{b.cancellation_reason}</p>
        </div>
      )}

      {/* Cancel Action */}
      {CANCELLABLE.includes(b.status) && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          {!showCancel ? (
            <button
              onClick={() => setShowCancel(true)}
              className="px-4 py-2 border border-red-300 text-red-600 text-sm rounded-md hover:bg-red-50"
            >
              Cancel Booking
            </button>
          ) : (
            <div className="space-y-3">
              <p className="text-sm font-medium text-gray-800">Reason for cancellation</p>
              <textarea
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                rows={3}
                placeholder="Please provide a reason (min 5 characters)…"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleCancel}
                  disabled={cancelReason.trim().length < 5 || loading}
                  className="px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 disabled:opacity-50"
                >
                  {loading ? 'Cancelling…' : 'Confirm Cancel'}
                </button>
                <button
                  onClick={() => setShowCancel(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-600 text-sm rounded-md hover:bg-gray-50"
                >
                  Keep Booking
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
