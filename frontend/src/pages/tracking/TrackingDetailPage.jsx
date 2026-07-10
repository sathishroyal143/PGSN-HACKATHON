import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { MapPin, Route, Shield, List } from 'lucide-react'
import { fetchRoutes, fetchGeofenceEvents, fetchTrackingSummary } from '../../redux/slices/trackingSlice'

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

function Badge({ value, colorMap, defaultCls = 'bg-gray-100 text-gray-600' }) {
  const cls = colorMap?.[value] || defaultCls
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {value}
    </span>
  )
}

const ROUTE_STATUS_COLOR = {
  planned:   'bg-yellow-100 text-yellow-700',
  active:    'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
}

export default function TrackingDetailPage() {
  const { bookingId } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const routes = useSelector((s) => s.tracking.routes[bookingId] || [])
  const geofenceEvents = useSelector((s) => s.tracking.geofenceEvents[bookingId] || [])
  const summary = useSelector((s) => s.tracking.summaries[bookingId])

  useEffect(() => {
    if (!bookingId) return
    dispatch(fetchTrackingSummary(bookingId))
    dispatch(fetchRoutes(bookingId))
    dispatch(fetchGeofenceEvents(bookingId))
  }, [dispatch, bookingId])

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline mb-1 block">
            ← Back
          </button>
          <h1 className="text-xl font-bold text-gray-900">Tracking Detail</h1>
          <p className="text-xs text-gray-500 mt-0.5">Booking #{bookingId?.slice(0, 8)}</p>
        </div>
        <Link
          to={`/tracking/${bookingId}`}
          className="flex items-center gap-1.5 px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >
          <MapPin size={14} /> Live Map
        </Link>
      </div>

      {/* Active Geofences */}
      {summary?.geofences?.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Shield size={16} className="text-blue-500" />
            <h2 className="font-semibold text-gray-800">Active Geofences</h2>
          </div>
          <div className="space-y-2">
            {summary.geofences.map((fence) => (
              <div key={fence.id} className="flex items-center justify-between text-sm py-1.5 border-b border-gray-50 last:border-0">
                <div>
                  <p className="font-medium text-gray-800">{fence.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {Number(fence.latitude).toFixed(4)}, {Number(fence.longitude).toFixed(4)} · r={fence.radius_meters}m
                  </p>
                </div>
                <Badge value={fence.fence_type} colorMap={{ pickup: 'bg-purple-100 text-purple-700', hospital: 'bg-red-100 text-red-700', drop: 'bg-green-100 text-green-700' }} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Routes */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Route size={16} className="text-blue-500" />
          <h2 className="font-semibold text-gray-800">Routes</h2>
        </div>
        {routes.length === 0 ? (
          <p className="text-sm text-gray-400">No routes created yet.</p>
        ) : (
          <div className="space-y-3">
            {routes.map((r) => (
              <div key={r.id} className="border border-gray-100 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-800 capitalize">{r.leg} leg</span>
                  <Badge value={r.status} colorMap={ROUTE_STATUS_COLOR} />
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-gray-500">
                  <span>Distance: {r.distance_meters ? `${(r.distance_meters / 1000).toFixed(1)} km` : '—'}</span>
                  <span>Duration: {r.duration_seconds ? `${Math.round(r.duration_seconds / 60)} min` : '—'}</span>
                  <span>ETA: {fmt(r.estimated_arrival)}</span>
                  {r.started_at   && <span>Started: {fmt(r.started_at)}</span>}
                  {r.completed_at && <span>Completed: {fmt(r.completed_at)}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Geofence Event Log */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <List size={16} className="text-blue-500" />
          <h2 className="font-semibold text-gray-800">Zone Event Log</h2>
        </div>
        {geofenceEvents.length === 0 ? (
          <p className="text-sm text-gray-400">No zone events recorded yet.</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {geofenceEvents.map((ev, i) => (
              <div key={ev.id || i} className="flex items-center gap-3 text-sm py-1.5 border-b border-gray-50 last:border-0">
                <span className={`w-2 h-2 rounded-full shrink-0 ${ev.event_type === 'enter' ? 'bg-green-500' : 'bg-orange-400'}`} />
                <span className="text-gray-700">
                  <span className="font-medium capitalize">{ev.event_type === 'enter' ? 'Entered' : 'Exited'}</span>{' '}
                  {ev.fence_name || ev.fence_type}
                </span>
                <span className="text-gray-400 text-xs ml-auto shrink-0">{fmt(ev.occurred_at)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
