import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Ticket, HelpCircle, MessageCircle, Plus, ChevronDown, ChevronUp, Send } from 'lucide-react'
import { fetchTickets, createTicket, fetchFAQs, sendChatbot } from '../../redux/slices/supportSlice'

const STATUS_COLORS = {
  open: 'bg-red-100 text-red-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  resolved: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-500',
}
const PRIORITY_COLORS = {
  low: 'text-gray-400', medium: 'text-yellow-500',
  high: 'text-orange-500', urgent: 'text-red-600',
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}

function FAQItem({ faq }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 text-left bg-white hover:bg-gray-50"
      >
        <span className="text-sm font-medium text-gray-800">{faq.question}</span>
        {open ? <ChevronUp size={16} className="text-gray-400 shrink-0" /> : <ChevronDown size={16} className="text-gray-400 shrink-0" />}
      </button>
      {open && <div className="px-3 pb-3 text-sm text-gray-600 bg-gray-50">{faq.answer}</div>}
    </div>
  )
}

export default function SupportPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { tickets, faqs, loading, error } = useSelector((s) => s.support)
  const [tab, setTab] = useState('tickets')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ subject: '', description: '', category: 'other', priority: 'medium' })
  const [submitting, setSubmitting] = useState(false)
  const [chatMessages, setChatMessages] = useState([
    { from: 'bot', text: "Hi! I'm the CareBridge assistant. How can I help you today?" }
  ])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  useEffect(() => {
    dispatch(fetchTickets())
    dispatch(fetchFAQs())
  }, [dispatch])

  async function handleCreateTicket(e) {
    e.preventDefault()
    setSubmitting(true)
    await dispatch(createTicket(form))
    setSubmitting(false)
    setShowForm(false)
    setForm({ subject: '', description: '', category: 'other', priority: 'medium' })
  }

  async function handleChatSend(e) {
    e.preventDefault()
    if (!chatInput.trim()) return
    const userMsg = chatInput.trim()
    setChatMessages((prev) => [...prev, { from: 'user', text: userMsg }])
    setChatInput('')
    setChatLoading(true)
    const result = await dispatch(sendChatbot(userMsg))
    setChatLoading(false)
    if (result.payload?.response) {
      setChatMessages((prev) => [...prev, { from: 'bot', text: result.payload.response }])
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Support Center</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200">
        {[
          { key: 'tickets', label: 'My Tickets', icon: Ticket },
          { key: 'faqs', label: 'FAQs', icon: HelpCircle },
          { key: 'chatbot', label: 'Chat Assistant', icon: MessageCircle },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-1.5 pb-2 px-3 text-sm font-medium border-b-2 transition-colors ${tab === key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <Icon size={14} />{label}
          </button>
        ))}
      </div>

      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>}

      {/* Tickets tab */}
      {tab === 'tickets' && (
        <div className="space-y-3">
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 w-full justify-center py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            <Plus size={16} />{showForm ? 'Cancel' : 'New Ticket'}
          </button>

          {showForm && (
            <form onSubmit={handleCreateTicket} className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="Subject"
                value={form.subject}
                onChange={(e) => setForm({ ...form, subject: e.target.value })}
                required
              />
              <textarea
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                placeholder="Describe your issue…"
                rows={3}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                required
              />
              <div className="grid grid-cols-2 gap-2">
                <select
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                >
                  {['booking', 'payment', 'companion', 'account', 'technical', 'other'].map((c) => (
                    <option key={c} value={c} className="capitalize">{c}</option>
                  ))}
                </select>
                <select
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  value={form.priority}
                  onChange={(e) => setForm({ ...form, priority: e.target.value })}
                >
                  {['low', 'medium', 'high', 'urgent'].map((p) => (
                    <option key={p} value={p} className="capitalize">{p}</option>
                  ))}
                </select>
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Submitting…' : 'Submit Ticket'}
              </button>
            </form>
          )}

          {loading && !tickets.length ? (
            <p className="text-center text-gray-400 py-10">Loading…</p>
          ) : tickets.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <Ticket size={40} className="mx-auto mb-3 opacity-40" />
              <p>No support tickets yet.</p>
            </div>
          ) : tickets.map((t) => (
            <div
              key={t.id}
              onClick={() => navigate(`/support/tickets/${t.id}`)}
              className="bg-white border border-gray-200 rounded-lg p-3 cursor-pointer hover:bg-gray-50 space-y-1"
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900">{t.subject}</p>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${STATUS_COLORS[t.status] || STATUS_COLORS.open}`}>
                  {t.status?.replace('_', ' ')}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-gray-400">
                <span className="capitalize">{t.category}</span>
                <span className={`font-medium capitalize ${PRIORITY_COLORS[t.priority]}`}>{t.priority}</span>
                <span className="ml-auto">{fmt(t.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* FAQs tab */}
      {tab === 'faqs' && (
        <div className="space-y-2">
          {faqs.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <HelpCircle size={40} className="mx-auto mb-3 opacity-40" />
              <p>No FAQs available yet.</p>
            </div>
          ) : faqs.map((faq) => <FAQItem key={faq.id} faq={faq} />)}
        </div>
      )}

      {/* Chatbot tab */}
      {tab === 'chatbot' && (
        <div className="flex flex-col h-[480px] bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] px-3 py-2 rounded-xl text-sm ${msg.from === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-500 px-3 py-2 rounded-xl text-sm rounded-bl-none">Typing…</div>
              </div>
            )}
          </div>
          <form onSubmit={handleChatSend} className="flex items-center gap-2 p-3 border-t border-gray-200">
            <input
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Type a message…"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <button
              type="submit"
              disabled={!chatInput.trim() || chatLoading}
              className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
