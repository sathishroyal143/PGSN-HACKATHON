import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  appendGeofenceEvent,
  setWsStatus,
  updateActiveRoute,
  updateLiveLocation,
} from '../redux/slices/trackingSlice'

const WS_BASE = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000'

/**
 * Connects to the tracking WebSocket for a given bookingId.
 * Automatically reconnects on unexpected close (up to maxRetries).
 */
export default function useTrackingSocket(bookingId, { enabled = true } = {}) {
  const dispatch = useDispatch()
  const token = useSelector((s) => s.auth.access)
  const wsRef = useRef(null)
  const retryRef = useRef(0)
  const maxRetries = 5

  useEffect(() => {
    if (!enabled || !bookingId || !token) return

    function connect() {
      const url = `${WS_BASE}/ws/tracking/${bookingId}/?token=${token}`
      const ws = new WebSocket(url)
      wsRef.current = ws

      dispatch(setWsStatus({ bookingId, status: 'connecting' }))

      ws.onopen = () => {
        retryRef.current = 0
        dispatch(setWsStatus({ bookingId, status: 'connected' }))
      }

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          handleMessage(msg)
        } catch {
          // ignore malformed frames
        }
      }

      ws.onerror = () => {
        dispatch(setWsStatus({ bookingId, status: 'error' }))
      }

      ws.onclose = (e) => {
        dispatch(setWsStatus({ bookingId, status: 'disconnected' }))
        // Reconnect with exponential back-off unless intentional close
        if (e.code !== 1000 && retryRef.current < maxRetries) {
          const delay = Math.min(1000 * 2 ** retryRef.current, 30_000)
          retryRef.current += 1
          setTimeout(connect, delay)
        }
      }
    }

    function handleMessage(msg) {
      switch (msg.type) {
        case 'location_update':
          dispatch(updateLiveLocation({ bookingId, location: msg.payload }))
          break
        case 'route_update':
        case 'eta_update':
          dispatch(updateActiveRoute({ bookingId, route: msg.payload }))
          break
        case 'geofence_event':
          dispatch(appendGeofenceEvent({ bookingId, event: msg.payload }))
          break
        default:
          break
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null // prevent reconnect on unmount
        wsRef.current.close(1000)
      }
    }
  }, [bookingId, token, enabled])
}
