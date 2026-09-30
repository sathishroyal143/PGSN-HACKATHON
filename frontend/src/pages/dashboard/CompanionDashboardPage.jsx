import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Calendar, CheckCircle, Clock, Star, Bell, ArrowRight, Activity, CalendarDays, TrendingUp } from 'lucide-react'
import { fetchDashboard } from '../../redux/slices/dashboardSlice'
import ActiveJourneyWidget from '../../components/ActiveJourneyWidget'

const STATUS_COLORS = {
  pending: 'bg-amber-100 text-amber-800 border-amber-200',
  confirmed: 'bg-blue-100 text-blue-800 border-blue-200',
  in_progress: 'bg-purple-100 text-purple-800 border-purple-200',
  completed: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  cancelled: 'bg-rose-100 text-rose-800 border-rose-200',
}

function StatCard({ icon: Icon, label, value, trend, color, bgColor, ringColor }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
      <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full ${bgColor} opacity-20 group-hover:scale-150 transition-transform duration-500`} />
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 rounded-xl ${bgColor} ${color} ${ringColor} ring-1 ring-inset relative z-10`}>
          <Icon size={22} strokeWidth={2.5} />
        </div>
        {trend && (
          <div className="flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2 py-1 rounded-md text-xs font-semibold relative z-10">
            <TrendingUp size={14} />
            {trend}
          </div>
        )}
      </div>
      <div className="relative z-10">
        <h3 className="text-3xl font-extrabold text-gray-900 mb-1">{value ?? '—'}</h3>
        <p className="text-sm font-medium text-gray-500">{label}</p>
      </div>
    </div>
  )
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—'
}

export default function CompanionDashboardPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { stats, recentBookings, loading, error } = useSelector((s) => s.dashboard)
  const { user } = useSelector((s) => s.auth)

  useEffect(() => { dispatch(fetchDashboard()) }, [dispatch])

  if (loading && !stats) return (
    <div className="flex items-center justify-center h-full min-h-[400px]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  )

  const currentDate = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
      
      {/* Dashboard Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            Welcome back, {user?.first_name || 'Companion'}! 👋
          </h1>
          <p className="text-gray-500 mt-1 font-medium">{currentDate} • Ready for your next shift?</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate('/companion/requests/pending')}
            className="flex items-center gap-2 bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 hover:text-gray-900 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-sm"
          >
            <Bell size={18} className="text-gray-500" />
            Notifications
            <span className="bg-rose-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full ml-1">3</span>
          </button>
          <button 
            onClick={() => navigate('/companion/requests/pending')}
            className="flex items-center gap-2 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-md shadow-primary-500/20"
          >
            <CalendarDays size={18} />
            View Schedule
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center text-red-700 gap-3 shadow-sm">
          <div className="bg-red-100 p-2 rounded-lg"><Activity size={20} /></div>
          <div>
            <p className="font-semibold text-sm">Dashboard Error</p>
            <p className="text-sm opacity-90">{error}</p>
          </div>
        </div>
      )}

      {/* KPI Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard 
            icon={Calendar} label="Total Trips" value={stats.total_bookings} trend="+12%"
            color="text-blue-600" bgColor="bg-blue-50" ringColor="ring-blue-100" 
          />
          <StatCard 
            icon={CheckCircle} label="Completed" value={stats.completed_bookings} trend="+5%"
            color="text-emerald-600" bgColor="bg-emerald-50" ringColor="ring-emerald-100" 
          />
          <StatCard 
            icon={Clock} label="Active Bookings" value={stats.active_bookings} 
            color="text-purple-600" bgColor="bg-purple-50" ringColor="ring-purple-100" 
          />
          <StatCard 
            icon={Star} label="Average Rating" value={stats.average_rating} trend="+0.2"
            color="text-amber-600" bgColor="bg-amber-50" ringColor="ring-amber-100" 
          />
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Main Content Column */}
        <div className="xl:col-span-2 space-y-8">
          
          <ActiveJourneyWidget />

          {/* Recent Bookings Table */}
          <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h2 className="text-lg font-bold text-gray-900">Recent Assignments</h2>
              <button 
                onClick={() => navigate('/companion/requests/accepted')}
                className="text-sm font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1 transition-colors"
              >
                View All <ArrowRight size={16} />
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50/50">
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Patient / Service</th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Schedule</th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {recentBookings.length > 0 ? (
                    recentBookings.map((b) => (
                      <tr 
                        key={b.id} 
                        onClick={() => navigate(`/companion/journey`)}
                        className="hover:bg-gray-50/80 transition-colors cursor-pointer group"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-100 to-primary-100 flex items-center justify-center text-primary-700 font-bold border border-primary-200">
                              {b.service_name ? b.service_name.charAt(0).toUpperCase() : 'B'}
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">{b.service_name || 'Care Booking'}</p>
                              <p className="text-xs text-gray-500">ID: #{b.id.substring(0, 8)}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-900 font-medium">{fmt(b.scheduled_start)}</p>
                          <p className="text-xs text-gray-500 mt-0.5">Duration: {b.duration_hours || 1} hrs</p>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border capitalize ${STATUS_COLORS[b.status?.toLowerCase()] || STATUS_COLORS.pending}`}>
                            {b.status?.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="text-gray-400 group-hover:text-primary-600 transition-colors inline-block transform group-hover:translate-x-1">
                            <ArrowRight size={20} />
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="px-6 py-12 text-center text-gray-500">
                        <div className="flex flex-col items-center justify-center">
                          <div className="bg-gray-100 p-4 rounded-full mb-3">
                            <Calendar size={24} className="text-gray-400" />
                          </div>
                          <p className="font-medium text-gray-900">No recent assignments</p>
                          <p className="text-sm mt-1">Your upcoming trips will appear here.</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Side Column */}
        <div className="space-y-8">
          {/* Action Card */}
          <div className="bg-gradient-to-br from-[#0d131a] to-[#1a2333] rounded-2xl p-6 shadow-xl relative overflow-hidden group">
            <div className="absolute -right-10 -top-10 w-40 h-40 bg-primary-500/20 rounded-full blur-3xl pointer-events-none" />
            <h3 className="text-xl font-bold text-white mb-2">Ready for work?</h3>
            <p className="text-gray-400 text-sm mb-6 relative z-10">Check the marketplace for new care requests in your area.</p>
            <button 
              onClick={() => navigate('/companion/requests/pending')}
              className="relative z-10 w-full bg-white text-gray-900 font-bold py-3 px-4 rounded-xl shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all flex items-center justify-center gap-2"
            >
              <Bell size={18} className="text-primary-600" />
              Browse Pending Requests
            </button>
          </div>

          {/* Quick Summary / Performance Snapshot */}
          <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-5">Performance Snapshot</h3>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-semibold text-gray-700">Completion Rate</span>
                  <span className="font-bold text-emerald-600">98%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                  <div className="bg-emerald-500 h-2.5 rounded-full w-[98%] shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-semibold text-gray-700">Response Time</span>
                  <span className="font-bold text-primary-600">&lt; 15 mins</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                  <div className="bg-primary-500 h-2.5 rounded-full w-[85%] shadow-[0_0_10px_rgba(8,145,178,0.5)]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-semibold text-gray-700">Client Satisfaction</span>
                  <span className="font-bold text-amber-500">{stats?.average_rating || '5.0'} / 5.0</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                  <div className="bg-amber-400 h-2.5 rounded-full w-[100%] shadow-[0_0_10px_rgba(251,191,36,0.5)]" />
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
