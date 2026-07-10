import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  appendIncomingMessage,
  setTyping,
  setWsStatus,
  setIncomingCall,
  setActiveCall,
  clearCallState,
} from '../redux/slices/communicationSlice'

const WS_BASE = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000'

/**
 * Connects to the chat WebSocket for a given conversationId.
 * Reconnects with exponential back-off on unexpected close.
 */
export default function useChatSocket(conversationId, { enabled = true } = {}) {
  const dispatch = useDispatch()
  const token = useSelector((s) => s.auth.access)
  const wsRef = useRef(null)
  const retryRef = useRef(0)
  const maxRetries = 5

  useEffect(() => {
    if (!enabled || !conversationId || !token) return

    function connect() {
      const url = `${WS_BASE}/ws/chat/${conversationId}/?token=${token}`
      const ws = new WebSocket(url)
      wsRef.current = ws

      dispatch(setWsStatus({ conversationId, status: 'connecting' }))

      ws.onopen = () => {
        retryRef.current = 0
        dispatch(setWsStatus({ conversationId, status: 'connected' }))
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
        dispatch(setWsStatus({ conversationId, status: 'error' }))
      }

      ws.onclose = (e) => {
        dispatch(setWsStatus({ conversationId, status: 'disconnected' }))
        if (e.code !== 1000 && retryRef.current < maxRetries) {
          const delay = Math.min(1000 * 2 ** retryRef.current, 30_000)
          retryRef.current += 1
          setTimeout(connect, delay)
        }
      }
    }

    function handleMessage(msg) {
      switch (msg.type) {
        case 'new_message':
          dispatch(appendIncomingMessage({ conversationId, message: msg.payload }))
          break
        case 'typing':
          dispatch(setTyping({
            conversationId,
            userId: msg.payload.user_id,
            userName: msg.payload.user_name,
            isTyping: true,
          }))
          break
        case 'stop_typing':
          dispatch(setTyping({
            conversationId,
            userId: msg.payload.user_id,
            userName: msg.payload.user_name,
            isTyping: false,
          }))
          break
        case 'call_initiate':
          dispatch(setIncomingCall({
            call_id: msg.payload.call_id,
            caller_name: msg.payload.caller_name,
            call_type: msg.payload.call_type,
            conversation_id: msg.payload.conversation_id,
            caller_id: msg.payload.caller_id,
          }))
          break
        case 'call_answer':
          dispatch(setActiveCall({
            call_id: msg.payload.call_id,
            conversation_id: conversationId,
          }))
          break
        case 'call_decline':
        case 'call_end':
          dispatch(clearCallState())
          break
        default:
          break
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null
        wsRef.current.close(1000)
      }
    }
  }, [conversationId, token, enabled])

  // Expose send function for typing indicators
  const sendTyping = (isTyping) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: isTyping ? 'typing' : 'stop_typing',
      }))
    }
  }

  return { sendTyping }
}
