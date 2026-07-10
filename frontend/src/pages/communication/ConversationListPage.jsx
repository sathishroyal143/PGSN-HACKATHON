import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { MessageSquare, Phone } from 'lucide-react'
import { fetchConversations, setActiveConversation } from '../../redux/slices/communicationSlice'

function fmt(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  const now = new Date()
  const diffDays = Math.floor((now - d) / 86400000)
  if (diffDays === 0) return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
  if (diffDays === 1) return 'Yesterday'
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

function ConvTypeIcon({ type }) {
  if (type === 'booking') return <MessageSquare size={16} className="text-blue-500" />
  if (type === 'support') return <Phone size={16} className="text-green-500" />
  return <MessageSquare size={16} className="text-gray-400" />
}

export default function ConversationListPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { conversations, loading, error } = useSelector((s) => s.communication)
  const user = useSelector((s) => s.auth.user)
  const currentUserId = user?.id

  useEffect(() => {
    dispatch(fetchConversations())
  }, [dispatch])

  const handleOpen = (conv) => {
    dispatch(setActiveConversation(conv.id))
    const role = user?.role
    let basePath = '/family'
    if (role === 'COMPANION') basePath = '/companion'
    if (role === 'ADMIN') basePath = '/admin'
    navigate(`${basePath}/communication/${conv.id}`)
  }

  const totalUnread = conversations.reduce((sum, c) => {
    const p = c.participants?.find((p) => p.user === currentUserId)
    return sum + (p?.unread_count || 0)
  }, 0)

  if (loading && !conversations.length) {
    return <div className="p-6 text-center text-gray-500">Loading conversations…</div>
  }

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Messages</h1>
          {totalUnread > 0 && (
            <p className="text-xs text-blue-600 mt-0.5">{totalUnread} unread</p>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>
      )}

      {conversations.length === 0 && !loading ? (
        <div className="text-center py-16 text-gray-400">
          <MessageSquare size={40} className="mx-auto mb-3 opacity-40" />
          <p>No conversations yet.</p>
        </div>
      ) : (
        <div className="space-y-1">
          {conversations.map((conv) => {
            const participant = conv.participants?.find((p) => p.user === currentUserId)
            const unread = participant?.unread_count || 0
            return (
              <button
                key={conv.id}
                onClick={(e) => {
                  if (conv.status === 'closed') {
                    e.preventDefault();
                    alert("This care journey has been completed. The chat is now closed.");
                    return;
                  }
                  handleOpen(conv);
                }}
                className={`w-full flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-left transition-colors ${conv.status === 'closed' ? 'opacity-60 cursor-not-allowed' : ''}`}
              >
                <div className="shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <ConvTypeIcon type={conv.conversation_type} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-gray-900 truncate">
                      {conv.title || `Conversation ${conv.id.slice(0, 8)}`}
                    </p>
                    <span className="text-xs text-gray-400 shrink-0">{fmt(conv.last_message_at)}</span>
                  </div>
                  <div className="flex items-center justify-between mt-0.5">
                    <p className="text-xs text-gray-500 capitalize">{conv.conversation_type} · {conv.status}</p>
                    {unread > 0 && (
                      <span className="ml-2 shrink-0 bg-blue-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                        {unread > 9 ? '9+' : unread}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
