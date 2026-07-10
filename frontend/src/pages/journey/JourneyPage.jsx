import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import { fetchJourneys } from '../../redux/slices/careJourneySlice'

const STATUS_COLOR = {
  ACTIVE: 'bg-green-100 text-green-800',
  COMPLETED: 'bg-blue-100 text-blue-800',
  CANCELLED: 'bg-red-100 text-red-800',
}

export default function JourneyPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { journeys, loading, error } = useSelector((s) => s.careJourney)

  const user = useSelector((s) => s.auth.user || s.user.profile)
  
  useEffect(() => { dispatch(fetchJourneys()) }, [dispatch])

  const location = useLocation()
  
  const getBasePath = () => {
    if (location.pathname.startsWith('/companion')) return '/companion/journey'
    if (location.pathname.startsWith('/admin')) return '/admin/journeys'
    return '/family/journeys'
  }

  if (loading) return <div className="p-6 text-center text-gray-500">Loading journeys…</div>
  if (error)   return <div className="p-6 text-center text-red-500">{error}</div>

  const activeJourneys = journeys.filter(j => j.status === 'ACTIVE')

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Care Journeys</h1>
        <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline">← Back</button>
      </div>

      {activeJourneys.length === 0 ? (
        <p className="text-gray-500 text-center py-12">No active journeys found.</p>
      ) : (
        <div className="space-y-3">
          {activeJourneys.map((j) => (
            <div
              key={j.id}
              onClick={() => navigate(`${getBasePath()}/${j.id}`)}
              className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{j.patient_name}</p>
                  <p className="text-sm text-gray-500 mt-0.5">
                    Current step: <span className="font-medium">{j.current_step?.replace(/_/g, ' ')}</span>
                  </p>
                  {j.started_at && (
                    <p className="text-xs text-gray-400 mt-0.5">
                      Started: {new Date(j.started_at).toLocaleString()}
                    </p>
                  )}
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLOR[j.status] || 'bg-gray-100 text-gray-700'}`}>
                  {j.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
