import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Users, Calendar, CheckCircle, Clock, Bell } from 'lucide-react'
import { fetchDashboard } from '../../redux/slices/dashboardSlice'
import ActiveJourneyWidget from '../../components/ActiveJourneyWidget'

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-700',
  confirmed: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-purple-100 text-purple-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
}

function StatCard({ icon: Icon, label, value, color = 'text-blue-600' }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center gap-3">
      <div className={`p-2 rounded-lg bg-gray-50 ${color}`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-xl font-bold text-gray-900">{value ?? '—'}</p>
      </div>
    </div>
  )
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : '—'
}

export default function FamilyDashboardPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { stats, recentBookings, loading, error } = useSelector((s) => s.dashboard)

  useEffect(() => { dispatch(fetchDashboard()) }, [dispatch])

  if (loading && !stats) return <div className="p-6 text-center text-gray-500">Loading dashboard…</div>

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-5">
      <h1 className="text-xl font-bold text-gray-900">Family Dashboard</h1>

      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>}

      <ActiveJourneyWidget />

      {/* Stats grid */}
      {stats && (
        <div className="grid grid-cols-2 gap-3">
          <StatCard icon={Users} label="Patients" value={stats.total_patients} />
          <StatCard icon={Calendar} label="Total Bookings" value={stats.total_bookings} />
          <StatCard icon={CheckCircle} label="Completed" value={stats.completed_bookings} color="text-green-600" />
          <StatCard icon={Clock} label="Active" value={stats.active_bookings} color="text-purple-600" />
          <StatCard icon={Bell} label="Unread Alerts" value={stats.unread_notifications} color="text-red-500" />
        </div>
      )}

      {/* Recent bookings */}
      {recentBookings.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-semibold text-gray-700">Recent Bookings</p>
          {recentBookings.map((b) => (
            <div
              key={b.id}
              onClick={() => navigate(`/family/bookings/${b.id}`)}
              className="bg-white border border-gray-200 rounded-lg p-3 flex items-center justify-between cursor-pointer hover:bg-gray-50"
            >
              <div>
                <p className="text-sm font-medium text-gray-900">{b.service_name || 'Booking'}</p>
                <p className="text-xs text-gray-400 mt-0.5">{fmt(b.scheduled_start)}</p>
              </div>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${STATUS_COLORS[b.status?.toLowerCase()] || STATUS_COLORS.pending}`}>
                {b.status?.replace('_', ' ')}
              </span>
            </div>
          ))}
          <button
            onClick={() => navigate('/family/bookings')}
            className="w-full text-center text-xs text-blue-600 hover:underline py-1"
          >
            View all bookings →
          </button>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => navigate('/family/bookings/new')}
          className="col-span-2 flex items-center justify-center gap-2 bg-blue-600 text-white rounded-xl py-3 px-4 text-sm font-semibold hover:bg-blue-700 transition-colors"
        >
          <Calendar size={16} />
          + New Booking
        </button>
      </div>
    </div>
  )
}
