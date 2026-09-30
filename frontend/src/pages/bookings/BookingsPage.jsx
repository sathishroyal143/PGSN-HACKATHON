import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import { fetchBookings } from '../../redux/slices/bookingsSlice'
import { Calendar, User, Clock, ArrowRight, Wallet, CheckCircle2, Filter } from 'lucide-react'

const STATUS_COLOR = {
  PENDING:    'bg-amber-100 text-amber-800 border-amber-200',
  CONFIRMED:  'bg-blue-100 text-blue-800 border-blue-200',
  IN_PROGRESS:'bg-purple-100 text-purple-800 border-purple-200',
  COMPLETED:  'bg-emerald-100 text-emerald-800 border-emerald-200',
  CANCELLED:  'bg-rose-100 text-rose-800 border-rose-200',
  NO_SHOW:    'bg-gray-100 text-gray-600 border-gray-200',
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
    if (datesToCheck.some(d => d && new Date(d).toLocaleDateString('en-IN') === today)) return true;
    if (b.status === 'IN_PROGRESS') return true;
    return false;
  }

  const dateFiltered = isTodayTrips ? bookings.filter(isTripToday) : bookings;
  const filtered = statusFilter === 'ALL'
    ? dateFiltered
    : dateFiltered.filter((b) => b.status === statusFilter)

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            {isTodayTrips ? "Today's Schedule" : isCompanion ? 'Accepted Assignments' : 'My Bookings'}
          </h1>
          <p className="text-gray-500 mt-1 font-medium">
            {isCompanion 
              ? "Manage and track your upcoming care responsibilities."
              : "View and manage all your family's care bookings."}
          </p>
        </div>
        {!isCompanion && (
          <button
            onClick={() => navigate('/family/bookings/new')}
            className="flex items-center gap-2 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-primary-500/20"
          >
            <Calendar size={18} />
            Schedule New Care
          </button>
        )}
      </div>

      {/* Status Filter */}
      {!isCompanion && (
        <div className="flex items-center gap-3 overflow-x-auto pb-2 scrollbar-hide">
          <div className="flex items-center gap-2 text-gray-500 font-semibold text-sm mr-2 shrink-0">
            <Filter size={16} /> Filter by Status:
          </div>
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`shrink-0 px-4 py-2 rounded-full text-sm font-bold border transition-all
                ${statusFilter === s 
                  ? 'bg-primary-600 text-white border-primary-600 shadow-md shadow-primary-500/20' 
                  : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300 hover:bg-primary-50'}`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-center font-semibold">
          {error}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-dashed border-gray-200 shadow-sm">
          <div className="bg-gray-50 p-6 rounded-full mb-4">
            <Calendar className="text-gray-400" size={48} strokeWidth={1.5} />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Bookings Found</h3>
          <p className="text-gray-500 font-medium text-center max-w-sm">
            {isCompanion 
              ? "You don't have any accepted assignments matching this criteria." 
              : "You haven't scheduled any care services matching this criteria."}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((b) => {
          const isEmergency = b.booking_type === 'EMERGENCY'
          return (
            <div
              key={b.id}
              onClick={() => navigate(isCompanion ? `/companion/bookings/${b.id}` : `/family/bookings/${b.id}`)}
              className={`bg-white border rounded-2xl p-6 cursor-pointer hover:shadow-xl transition-all relative overflow-hidden group flex flex-col ${
                isEmergency ? 'border-red-200 hover:border-red-300' : 'border-gray-100 hover:border-primary-200'
              }`}
            >
              {isEmergency && (
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-red-500 to-rose-500" />
              )}
              
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg border ${
                    isEmergency ? 'bg-red-50 text-red-600 border-red-100' : 'bg-primary-50 text-primary-600 border-primary-100'
                  }`}>
                    {b.service_name ? b.service_name.charAt(0).toUpperCase() : 'B'}
                  </div>
                  <div>
                    <p className="font-bold text-gray-900 text-lg leading-tight">{b.service_name}</p>
                    <p className="text-xs text-gray-500 font-medium mt-1">ID: #{b.id.substring(0, 8)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-xl p-4 space-y-3 mb-4 flex-1 border border-gray-100/50 group-hover:bg-primary-50/30 transition-colors">
                <div className="flex items-center justify-between pb-3 border-b border-gray-200/60">
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border ${STATUS_COLOR[b.status] || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                    {b.status.replace('_', ' ')}
                  </span>
                  <div className="flex items-center gap-1.5 font-bold text-gray-900 bg-white px-2 py-1 rounded-lg border border-gray-200">
                    <Wallet size={14} className="text-emerald-500" />
                    {b.final_price ? `₹${b.final_price}` : b.quoted_price ? `₹${b.quoted_price}` : '—'}
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <User size={16} className="text-gray-400 shrink-0" />
                  <p className="text-sm font-semibold text-gray-800 truncate">
                    <span className="text-gray-500 font-medium">Patient:</span> {b.patient_name}
                  </p>
                </div>
                
                {b.companion_name && (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-emerald-500 shrink-0" />
                    <p className="text-sm font-semibold text-gray-800 truncate">
                      <span className="text-gray-500 font-medium">Companion:</span> {b.companion_name}
                    </p>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between mt-auto pt-4 border-t border-gray-100">
                <div className="flex items-center gap-2 text-sm font-semibold text-gray-600">
                  <Clock size={16} className="text-gray-400" />
                  {fmt(b.scheduled_start)}
                </div>
                <div className="w-8 h-8 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 group-hover:bg-primary-600 group-hover:text-white group-hover:border-primary-600 transition-colors">
                  <ArrowRight size={16} />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
