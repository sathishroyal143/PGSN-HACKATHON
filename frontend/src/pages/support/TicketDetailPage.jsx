import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send } from 'lucide-react'
import { fetchTicketDetail } from '../../redux/slices/supportSlice'
import supportApi from '../../api/supportApi'

const STATUS_COLORS = {
  open: 'bg-red-100 text-red-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  resolved: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-500',
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—'
}

export default function TicketDetailPage() {
  const { ticketId } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { activeTicket: ticket, activeMessages: messages } = useSelector((s) => s.support)
  const [reply, setReply] = useState('')
  const [sending, setSending] = useState(false)

  useEffect(() => { dispatch(fetchTicketDetail(ticketId)) }, [dispatch, ticketId])

  async function handleReply(e) {
    e.preventDefault()
    if (!reply.trim()) return
    setSending(true)
    await supportApi.replyTicket(ticketId, { body: reply })
    setReply('')
    dispatch(fetchTicketDetail(ticketId))
    setSending(false)
  }

  if (!ticket) return <div className="p-6 text-center text-gray-400">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <button onClick={() => navigate('/support')} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={16} /> Back to Support
      </button>

      <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h2 className="text-base font-semibold text-gray-900">{ticket.subject}</h2>
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize shrink-0 ${STATUS_COLORS[ticket.status] || STATUS_COLORS.open}`}>
            {ticket.status?.replace('_', ' ')}
          </span>
        </div>
        <p className="text-sm text-gray-600">{ticket.description}</p>
        <div className="flex gap-3 text-xs text-gray-400">
          <span className="capitalize">{ticket.category}</span>
          <span className="capitalize font-medium">{ticket.priority}</span>
          <span className="ml-auto">{fmt(ticket.created_at)}</span>
        </div>
        {ticket.resolution_notes && (
          <div className="mt-2 bg-green-50 border-l-2 border-green-400 rounded p-2 text-xs text-green-700">
            <span className="font-medium">Resolution: </span>{ticket.resolution_notes}
          </div>
        )}
      </div>

      {/* Messages thread */}
      <div className="space-y-2">
        <p className="text-sm font-semibold text-gray-700">Conversation</p>
        {messages.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">No messages yet. Add a reply below.</p>
        ) : messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.is_staff_reply ? 'justify-start' : 'justify-end'}`}>
            <div className={`max-w-[80%] px-3 py-2 rounded-xl text-sm ${msg.is_staff_reply ? 'bg-blue-50 text-blue-900 rounded-bl-none' : 'bg-gray-100 text-gray-800 rounded-br-none'}`}>
              <p>{msg.body}</p>
              <p className="text-xs opacity-60 mt-1 text-right">{fmt(msg.created_at)}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Reply form */}
      {ticket.status !== 'closed' && ticket.status !== 'resolved' && (
        <form onSubmit={handleReply} className="flex items-end gap-2">
          <textarea
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Write a reply…"
            rows={2}
            value={reply}
            onChange={(e) => setReply(e.target.value)}
          />
          <button
            type="submit"
            disabled={!reply.trim() || sending}
            className="p-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </form>
      )}
    </div>
  )
}
