import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import { fetchJourneys } from '../redux/slices/careJourneySlice'
import { fetchConversations } from '../redux/slices/communicationSlice'
import { MapPin, Clock, Phone, User as UserIcon } from 'lucide-react'

export default function ActiveJourneyWidget() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { journeys, loading } = useSelector((s) => s.careJourney)
  const { conversations } = useSelector((s) => s.communication)
  const user = useSelector((s) => s.auth.user || s.user.profile)

  useEffect(() => {
    dispatch(fetchJourneys())
    dispatch(fetchConversations())
  }, [dispatch])

  // Get first active journey
  const activeJourney = journeys.find(j => j.status === 'ACTIVE')

  if (loading) return <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm mb-6 text-center text-gray-500 animate-pulse">Loading Care Journey...</div>
  
  const location = useLocation()
  
  const getBasePath = () => {
    if (location.pathname.startsWith('/companion')) return '/companion/journey'
    if (location.pathname.startsWith('/admin')) return '/admin/journeys'
    return '/family/journeys'
  }

  if (!activeJourney) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm mb-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <MapPin className="text-gray-400" size={20} />
            Care Journey Tracking
          </h2>
          <button 
            onClick={() => navigate(getBasePath())}
            className="text-sm font-semibold text-blue-600 hover:underline"
          >
            View History →
          </button>
        </div>
        <p className="text-sm text-gray-500 text-center py-4 bg-gray-50 rounded-lg border border-dashed border-gray-300">
          No active care journey at the moment. When a companion starts a trip, live tracking will appear here.
        </p>
      </div>
    )
  }

  const stepName = activeJourney.current_step?.replace(/_/g, ' ') || 'Pending'

  return (
    <div className="bg-white border-2 border-blue-200 rounded-xl p-5 shadow-sm mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
          Active Care Journey
        </h2>
        <button 
          onClick={() => navigate(`${getBasePath()}/${activeJourney.id}`)}
          className="text-sm font-semibold text-blue-600 hover:underline"
        >
          View Details →
        </button>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        {/* Companion Details */}
        <div className="flex-1 bg-blue-50 rounded-lg p-4 flex items-start gap-4">
          <div className="w-12 h-12 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 font-bold shrink-0">
            {activeJourney.companion_name ? activeJourney.companion_name[0] : <UserIcon size={20} />}
          </div>
          <div>
            <p className="text-xs text-blue-600 font-medium uppercase tracking-wider mb-0.5">Assigned Companion</p>
            <p className="text-sm font-bold text-gray-900">{activeJourney.companion_name || 'Pending Assignment'}</p>
            <div className="flex items-center gap-3 mt-2 text-xs">
              <button 
                onClick={() => {
                  const role = user?.role
                  let basePath = '/family'
                  if (role === 'COMPANION') basePath = '/companion'
                  if (role === 'ADMIN') basePath = '/admin'
                  
                  const activeConversation = conversations?.find(c => c.booking === activeJourney.booking_id)
                  
                  if (activeConversation) {
                    navigate(`${basePath}/communication/${activeConversation.id}`)
                  } else {
                    navigate(`${basePath}/communication`)
                  }
                }}
                className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold"
              >
                <Phone size={12} /> Contact
              </button>
              <button 
                onClick={() => navigate(`${getBasePath()}/${activeJourney.id}`)}
                className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold"
              >
                <MapPin size={12} /> Track Live
              </button>
            </div>
          </div>
        </div>

        {/* Status Details */}
        <div className="flex-1 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-0.5">Current Status</p>
          <p className="text-sm font-bold text-gray-900 capitalize">{stepName}</p>
          
          <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
            <Clock size={14} className="text-gray-400" />
            <span>Started: {new Date(activeJourney.started_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
