import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Bell, Check, CheckCheck, Trash2 } from 'lucide-react'
import {
  fetchNotifications,
  markRead,
  markAllRead,
  deleteNotification,
} from '../../redux/slices/notificationsSlice'

const PRIORITY_COLORS = {
  high: 'border-l-red-500',
  normal: 'border-l-blue-400',
  low: 'border-l-gray-300',
}

function fmt(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  const diff = Date.now() - d
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

export default function NotificationsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { items, unreadCount, loading, error } = useSelector((s) => s.notifications)

  useEffect(() => { dispatch(fetchNotifications()) }, [dispatch])

  const handleMarkRead = (id) => dispatch(markRead(id))
  const handleDelete = (id) => dispatch(deleteNotification(id))
  const handleMarkAll = () => dispatch(markAllRead())

  const handleClick = (notif) => {
    if (!notif.is_read) handleMarkRead(notif.id)
    if (notif.action_url) {
      let url = notif.action_url
      if (url.startsWith('/bookings')) {
        const basePath = window.location.pathname.startsWith('/admin') ? '/admin' 
                       : window.location.pathname.startsWith('/companion') ? '/companion' 
                       : '/family'
        url = `${basePath}${url}`
      }
      navigate(url)
    }
  }

  if (loading && !items.length) {
    return <div className="p-6 text-center text-gray-500">Loading…</div>
  }

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Notifications</h1>
          {unreadCount > 0 && (
            <p className="text-xs text-blue-600 mt-0.5">{unreadCount} unread</p>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAll}
            className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
          >
            <CheckCheck size={14} /> Mark all read
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>
      )}

      {items.length === 0 && !loading ? (
        <div className="text-center py-16 text-gray-400">
          <Bell size={40} className="mx-auto mb-3 opacity-40" />
          <p>No notifications yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((n) => (
            <div
              key={n.id}
              className={`flex gap-3 p-3 bg-white border-l-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${PRIORITY_COLORS[n.priority] || PRIORITY_COLORS.normal} ${!n.is_read ? 'bg-blue-50/30' : ''}`}
              onClick={() => handleClick(n)}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className={`text-sm font-medium ${n.is_read ? 'text-gray-700' : 'text-gray-900'}`}>
                    {n.title}
                  </p>
                  <span className="text-xs text-gray-400 shrink-0">{fmt(n.created_at)}</span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.body}</p>
              </div>
              <div className="flex flex-col items-center gap-1 shrink-0">
                {!n.is_read && (
                  <button
                    onClick={(e) => { e.stopPropagation(); handleMarkRead(n.id) }}
                    className="text-blue-400 hover:text-blue-600"
                    title="Mark read"
                  >
                    <Check size={14} />
                  </button>
                )}
                <button
                  onClick={(e) => { e.stopPropagation(); handleDelete(n.id) }}
                  className="text-gray-300 hover:text-red-400"
                  title="Delete"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
