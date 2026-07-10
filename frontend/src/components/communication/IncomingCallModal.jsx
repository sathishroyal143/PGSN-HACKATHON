import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Phone, PhoneOff } from 'lucide-react'
import communicationApi from '../../api/communicationApi'
import { setActiveCall, clearCallState } from '../../redux/slices/communicationSlice'

export default function IncomingCallModal() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const incomingCall = useSelector((s) => s.communication.incomingCall)
  const user = useSelector((s) => s.auth.user)

  // If there's no incoming call, don't render anything
  if (!incomingCall) return null

  // Check if we are the caller (we shouldn't see incoming call modal for our own calls)
  if (incomingCall.caller_id == user?.id) return null

  const handleAccept = async () => {
    try {
      await communicationApi.answerCall(incomingCall.conversation_id, incomingCall.call_id)
      dispatch(setActiveCall({
        call_id: incomingCall.call_id,
        conversation_id: incomingCall.conversation_id,
      }))
      
      // Navigate to the chat page so they are in the right place
      let basePath = '/family'
      if (user?.role === 'COMPANION') basePath = '/companion'
      if (user?.role === 'ADMIN') basePath = '/admin'
      navigate(`${basePath}/communication/${incomingCall.conversation_id}`)
    } catch {
      // ignore
    }
  }

  const handleDecline = async () => {
    try {
      await communicationApi.declineCall(incomingCall.conversation_id, incomingCall.call_id)
      dispatch(clearCallState())
    } catch {
      // ignore
      dispatch(clearCallState())
    }
  }

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-white rounded-3xl shadow-2xl p-8 w-80 flex flex-col items-center animate-bounce">
        <div className="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center mb-6 relative">
          <div className="absolute inset-0 rounded-full border-4 border-blue-400 opacity-30 animate-ping"></div>
          <span className="text-4xl text-blue-600 font-bold">
            {incomingCall.caller_name ? incomingCall.caller_name[0] : '?'}
          </span>
        </div>
        
        <h2 className="text-2xl font-bold text-gray-900 mb-1">{incomingCall.caller_name}</h2>
        <p className="text-gray-500 mb-8 capitalize">{incomingCall.call_type} Call...</p>
        
        <div className="flex w-full justify-between px-4">
          <button
            onClick={handleDecline}
            className="w-14 h-14 rounded-full bg-red-500 flex items-center justify-center text-white hover:bg-red-600 shadow-lg shadow-red-500/30 transition-transform hover:scale-110"
          >
            <PhoneOff size={24} />
          </button>
          
          <button
            onClick={handleAccept}
            className="w-14 h-14 rounded-full bg-green-500 flex items-center justify-center text-white hover:bg-green-600 shadow-lg shadow-green-500/30 transition-transform hover:scale-110 animate-pulse"
          >
            <Phone size={24} />
          </button>
        </div>
      </div>
    </div>
  )
}
