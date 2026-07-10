import { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, Phone, Wifi, WifiOff, Trash2 } from 'lucide-react'
import {
  fetchMessages,
  sendMessage,
  markConversationRead,
  setActiveCall,
} from '../../redux/slices/communicationSlice'
import communicationApi from '../../api/communicationApi'
import useChatSocket from '../../hooks/useChatSocket'

function fmt(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

function WsIndicator({ status }) {
  const map = {
    connected:    { icon: <Wifi size={12} />,    cls: 'text-green-500' },
    connecting:   { icon: <Wifi size={12} />,    cls: 'text-yellow-400' },
    disconnected: { icon: <WifiOff size={12} />, cls: 'text-gray-400' },
    error:        { icon: <WifiOff size={12} />, cls: 'text-red-400' },
  }
  const s = map[status] || map.disconnected
  return <span className={s.cls}>{s.icon}</span>
}

export default function ChatPage() {
  const { id: conversationId } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const bottomRef = useRef(null)
  const typingTimerRef = useRef(null)

  const messages = useSelector((s) => s.communication.messages[conversationId] || [])
  const wsStatus = useSelector((s) => s.communication.wsStatus[conversationId] || 'disconnected')
  const typingUsers = useSelector((s) => s.communication.typingUsers[conversationId] || {})
  const sending = useSelector((s) => s.communication.sending)
  const currentUser = useSelector((s) => s.auth.user)
  const currentConversation = useSelector((s) => s.communication.conversations?.find((c) => c.id === conversationId))

  const [text, setText] = useState('')
  const { sendTyping } = useChatSocket(conversationId, { enabled: !!conversationId })

  useEffect(() => {
    if (!conversationId) return
    dispatch(fetchMessages({ conversationId }))
    communicationApi.markRead(conversationId).catch(() => {})
    dispatch(markConversationRead(conversationId))
  }, [dispatch, conversationId])

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    const content = text.trim()
    if (!content) return
    setText('')
    sendTyping(false)
    dispatch(sendMessage({ conversationId, data: { message_type: 'text', content } }))
  }

  const handleTextChange = (e) => {
    setText(e.target.value)
    sendTyping(true)
    clearTimeout(typingTimerRef.current)
    typingTimerRef.current = setTimeout(() => sendTyping(false), 2000)
  }

  const handleDeleteMessage = async (messageId) => {
    try {
      await communicationApi.deleteMessage(conversationId, messageId)
      dispatch(fetchMessages({ conversationId }))
    } catch {
      // ignore
    }
  }

  const handleCall = async (callType) => {
    try {
      const receiver = currentConversation?.participants?.find((p) => p.user !== currentUser?.id)
      if (!receiver) return
      
      await communicationApi.initiateCall(conversationId, {
        receiver_id: receiver.user,
        call_type: callType,
      })
    } catch {
      // ignore
    }
  }

  const typingNames = Object.values(typingUsers).filter(Boolean)

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 shrink-0">
        <button 
          onClick={() => {
            const role = currentUser?.role
            let basePath = '/family'
            if (role === 'COMPANION') basePath = '/companion'
            if (role === 'ADMIN') basePath = '/admin'
            navigate(`${basePath}/communication`)
          }} 
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back
        </button>
        <div className="flex-1">
          <p className="text-sm font-semibold text-gray-900 truncate">
            Conversation #{conversationId?.slice(0, 8)}
          </p>
        </div>
        <WsIndicator status={wsStatus} />
        <button
          onClick={() => handleCall('audio')}
          className="p-1.5 rounded-md hover:bg-gray-100 text-gray-500"
          title="Audio call"
        >
          <Phone size={16} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
        {messages.map((msg) => {
          const isOwn = msg.sender === currentUser?.id
          return (
            <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'} group`}>
              <div className={`max-w-xs lg:max-w-md relative ${isOwn ? 'items-end' : 'items-start'} flex flex-col`}>
                {!isOwn && (
                  <p className="text-xs text-gray-400 mb-0.5 ml-1">{msg.sender_name}</p>
                )}
                <div
                  className={`px-3 py-2 rounded-2xl text-sm ${
                    msg.is_deleted
                      ? 'bg-gray-100 text-gray-400 italic'
                      : isOwn
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  {msg.is_deleted ? 'Message deleted' : msg.content}
                </div>
                <div className="flex items-center gap-1 mt-0.5">
                  <span className="text-xs text-gray-400">{fmt(msg.created_at)}</span>
                  {isOwn && !msg.is_deleted && (
                    <button
                      onClick={() => handleDeleteMessage(msg.id)}
                      className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition-opacity"
                    >
                      <Trash2 size={10} />
                    </button>
                  )}
                </div>
              </div>
            </div>
          )
        })}

        {/* Typing indicator */}
        {typingNames.length > 0 && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-3 py-2 text-xs text-gray-400">
              {typingNames.join(', ')} {typingNames.length === 1 ? 'is' : 'are'} typing…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSend}
        className="bg-white border-t border-gray-200 px-4 py-3 flex items-center gap-2 shrink-0"
      >
        <input
          type="text"
          value={text}
          onChange={handleTextChange}
          placeholder="Type a message…"
          className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          type="submit"
          disabled={!text.trim() || sending}
          className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}
