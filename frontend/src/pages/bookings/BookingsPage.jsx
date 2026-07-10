import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import { fetchBookings } from '../../redux/slices/bookingsSlice'

const STATUS_COLOR = {
  PENDING:    'bg-yellow-100 text-yellow-800',
  CONFIRMED:  'bg-blue-100 text-blue-800',
  IN_PROGRESS:'bg-indigo-100 text-indigo-800',
  COMPLETED:  'bg-green-100 text-green-800',
  CANCELLED:  'bg-red-100 text-red-800',
  NO_SHOW:    'bg-gray-100 text-gray-600',
}

const STATUSES = ['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

export default function BookingsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  const { bookings, loading, error } = useSelector((s) => s.bookings)
  const [statusFilter, setStatusFilter] = useState('ALL')
  
  const isCompanion = location.pathname.includes('/companion/')
  const isTodayTrips = location.pathname.includes('/requests/today')

  useEffect(() => {
    dispatch(fetchBookings())
  }, [dispatch])
  
  const isTripToday = (b) => {
    const today = new Date().toLocaleDateString('en-IN');
    const datesToCheck = [b.scheduled_start, b.scheduled_end, b.actual_start, b.actual_end];
    
    // Check if any of the dates fall on today
    if (datesToCheck.some(d => d && new Date(d).toLocaleDateString('en-IN') === today)) {
      return true;
    }
    
    // If the trip is currently in progress, it's active today regardless of scheduled dates
    if (b.status === 'IN_PROGRESS') {
      return true;
    }
    
    return false;
  }

  const dateFiltered = isTodayTrips ? bookings.filter(isTripToday) : bookings;

  const filtered = statusFilter === 'ALL'
    ? dateFiltered
    : dateFiltered.filter((b) => b.status === statusFilter)

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {isTodayTrips ? "Today's Trips" : isCompanion ? 'Accepted Trips' : 'My Bookings'}
        </h1>
        {!isCompanion && (
          <button
            onClick={() => navigate('/family/bookings/new')}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
          >
            + New Booking
          </button>
        )}
      </div>

      {/* Status Filter */}
      {!isCompanion && (
        <div className="flex flex-wrap gap-2 mb-6">
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors
                ${statusFilter === s ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'}`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      )}

      {loading && <p className="text-center text-gray-500 py-8">Loading…</p>}
      {error   && <p className="text-center text-red-500 py-4">{error}</p>}

      {!loading && filtered.length === 0 && (
        <p className="text-center text-gray-500 py-12">No bookings found.</p>
      )}

      <div className="space-y-3">
        {filtered.map((b) => (
          <div
            key={b.id}
            onClick={() => navigate(isCompanion ? `/companion/bookings/${b.id}` : `/family/bookings/${b.id}`)}
            className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 truncate">{b.service_name}</p>
                <p className="text-sm text-gray-500 mt-0.5">Patient: {b.patient_name}</p>
                {b.companion_name && (
                  <p className="text-sm text-gray-500">Companion: {b.companion_name}</p>
                )}
              </div>
              <span className={`shrink-0 px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOR[b.status] || 'bg-gray-100 text-gray-600'}`}>
                {b.status.replace('_', ' ')}
              </span>
            </div>
            <div className="mt-3 flex items-center justify-between text-sm text-gray-500">
              <span>📅 {fmt(b.scheduled_start)}</span>
              <span className="font-semibold text-gray-800">
                {b.final_price ? `₹${b.final_price}` : b.quoted_price ? `₹${b.quoted_price}` : '—'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
