import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { MapPin, Navigation, Clock, AlertCircle, Wifi, WifiOff } from 'lucide-react'
import {
  fetchTrackingSummary,
  fetchLocationHistory,
  fetchGeofenceEvents,
} from '../../redux/slices/trackingSlice'
import useTrackingSocket from '../../hooks/useTrackingSocket'

// Leaflet loaded via CDN — add to index.html:
// <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
// <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

function WsIndicator({ status }) {
  const map = {
    connected:    { icon: <Wifi size={14} />,    cls: 'text-green-600',  label: 'Live' },
    connecting:   { icon: <Wifi size={14} />,    cls: 'text-yellow-500', label: 'Connecting…' },
    disconnected: { icon: <WifiOff size={14} />, cls: 'text-gray-400',   label: 'Offline' },
    error:        { icon: <WifiOff size={14} />, cls: 'text-red-500',    label: 'Error' },
  }
  const s = map[status] || map.disconnected
  return (
    <span className={`flex items-center gap-1 text-xs font-medium ${s.cls}`}>
      {s.icon} {s.label}
    </span>
  )
}

function InfoCard({ icon, label, value }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 flex items-start gap-3">
      <div className="text-blue-500 mt-0.5">{icon}</div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-sm font-semibold text-gray-800 mt-0.5">{value || '—'}</p>
      </div>
    </div>
  )
}

export default function TrackingPage() {
  const { bookingId } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const mapRef = useRef(null)
  const leafletMapRef = useRef(null)
  const markerRef = useRef(null)
  const polylineRef = useRef(null)

  const summary = useSelector((s) => s.tracking.summaries[bookingId])
  const history = useSelector((s) => s.tracking.histories[bookingId] || [])
  const geofenceEvents = useSelector((s) => s.tracking.geofenceEvents[bookingId] || [])
  const wsStatus = useSelector((s) => s.tracking.wsStatus[bookingId] || 'disconnected')
  const loading = useSelector((s) => s.tracking.loading)
  const error = useSelector((s) => s.tracking.error)

  useTrackingSocket(bookingId, { enabled: !!bookingId })

  useEffect(() => {
    if (!bookingId) return
    dispatch(fetchTrackingSummary(bookingId))
    dispatch(fetchLocationHistory({ bookingId, limit: 500 }))
    dispatch(fetchGeofenceEvents(bookingId))
  }, [dispatch, bookingId])

  // Initialize Leaflet map once
  useEffect(() => {
    if (!mapRef.current || leafletMapRef.current) return
    if (typeof window.L === 'undefined') return
    const L = window.L
    const map = L.map(mapRef.current).setView([20.5937, 78.9629], 5)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
    }).addTo(map)
    leafletMapRef.current = map
  }, [])

  // Update companion marker on live location change
  useEffect(() => {
    if (typeof window.L === 'undefined' || !leafletMapRef.current) return
    const loc = summary?.live_location
    if (!loc) return
    const L = window.L
    const latlng = [loc.latitude, loc.longitude]
    if (!markerRef.current) {
      const icon = L.divIcon({
        className: '',
        html: '<div style="width:16px;height:16px;background:#2563eb;border:3px solid white;border-radius:50%;box-shadow:0 0 6px rgba(0,0,0,0.4)"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8],
      })
      markerRef.current = L.marker(latlng, { icon }).addTo(leafletMapRef.current)
    } else {
      markerRef.current.setLatLng(latlng)
    }
    leafletMapRef.current.setView(latlng, 15)
  }, [summary?.live_location])

  // Draw polyline trail
  useEffect(() => {
    if (typeof window.L === 'undefined' || !leafletMapRef.current || history.length < 2) return
    const L = window.L
    const points = history.map((p) => [p.latitude, p.longitude])
    if (polylineRef.current) {
      polylineRef.current.setLatLngs(points)
    } else {
      polylineRef.current = L.polyline(points, { color: '#2563eb', weight: 3, opacity: 0.7 })
        .addTo(leafletMapRef.current)
    }
  }, [history])

  const live = summary?.live_location
  const route = summary?.active_route

  if (loading && !summary) {
    return <div className="p-6 text-center text-gray-500">Loading tracking data…</div>
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="mx-auto text-red-400 mb-2" size={32} />
        <p className="text-red-500">{error}</p>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline mb-1 block">
            ← Back
          </button>
          <h1 className="text-xl font-bold text-gray-900">Live Tracking</h1>
          <p className="text-xs text-gray-500 mt-0.5">Booking #{bookingId?.slice(0, 8)}</p>
        </div>
        <WsIndicator status={wsStatus} />
      </div>

      {/* Info cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <InfoCard
          icon={<MapPin size={18} />}
          label="Current Location"
          value={live ? `${Number(live.latitude).toFixed(4)}, ${Number(live.longitude).toFixed(4)}` : 'Awaiting…'}
        />
        <InfoCard
          icon={<Navigation size={18} />}
          label="Speed"
          value={live?.speed != null ? `${live.speed} km/h` : '—'}
        />
        <InfoCard
          icon={<Clock size={18} />}
          label="ETA"
          value={route?.estimated_arrival ? fmt(route.estimated_arrival) : '—'}
        />
        <InfoCard
          icon={<MapPin size={18} />}
          label="Current Leg"
          value={route?.leg ? route.leg.replace('_', ' ').toUpperCase() : '—'}
        />
      </div>

      {/* Map */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div ref={mapRef} style={{ height: '420px', width: '100%' }} />
        {typeof window !== 'undefined' && typeof window.L === 'undefined' && (
          <div className="p-4 text-center text-sm text-gray-500">
            Map requires Leaflet CDN links in index.html.
          </div>
        )}
      </div>

      {/* Stale location warning */}
      {live?.is_stale && (
        <div className="flex items-center gap-2 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-700">
          <AlertCircle size={16} />
          Location data is stale — companion may be offline.
        </div>
      )}

      {/* Geofence Events */}
      {geofenceEvents.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="font-semibold text-gray-800 mb-3">Zone Events</h2>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {geofenceEvents.map((ev, i) => (
              <div key={ev.id || i} className="flex items-center gap-3 text-sm">
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${
                    ev.event_type === 'enter' ? 'bg-green-500' : 'bg-orange-400'
                  }`}
                />
                <span className="text-gray-700 capitalize">
                  {ev.event_type === 'enter' ? 'Entered' : 'Exited'}{' '}
                  <span className="font-medium">{ev.fence_name || ev.fence_type}</span>
                </span>
                <span className="text-gray-400 text-xs ml-auto shrink-0">{fmt(ev.occurred_at)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Route Details */}
      {route && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="font-semibold text-gray-800 mb-3">Active Route</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
            <div>
              <p className="text-gray-500 text-xs">Leg</p>
              <p className="font-medium text-gray-800 capitalize">{route.leg}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Distance</p>
              <p className="font-medium text-gray-800">
                {route.distance_meters ? `${(route.distance_meters / 1000).toFixed(1)} km` : '—'}
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Duration</p>
              <p className="font-medium text-gray-800">
                {route.duration_seconds ? `${Math.round(route.duration_seconds / 60)} min` : '—'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
