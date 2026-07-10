import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { PhoneOff, Mic, MicOff, Volume2 } from 'lucide-react'
import communicationApi from '../../api/communicationApi'
import { clearCallState } from '../../redux/slices/communicationSlice'

export default function ActiveCallModal() {
  const dispatch = useDispatch()
  const activeCall = useSelector((s) => s.communication.activeCall)
  const incomingCall = useSelector((s) => s.communication.incomingCall)
  const user = useSelector((s) => s.auth.user)
  const [duration, setDuration] = useState(0)
  const [isMuted, setIsMuted] = useState(false)

  useEffect(() => {
    if (!activeCall) {
      setDuration(0)
      return
    }
    setDuration(0)
    const timer = setInterval(() => {
      setDuration(d => d + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [activeCall])

  const handleEndCall = async () => {
    try {
      const convId = activeCall?.conversation_id || incomingCall?.conversation_id
      const cId = activeCall?.call_id || incomingCall?.call_id
      
      if (convId && cId) {
        await communicationApi.endCall(convId, cId)
      }
      dispatch(clearCallState())
    } catch {
      // ignore
      dispatch(clearCallState())
    }
  }

  // If there's an incoming call but not active yet, and we are the caller (ringing state)
  const isCallerRinging = !activeCall && incomingCall && incomingCall.caller_id == user?.id

  if (!activeCall && !isCallerRinging) return null

  const isRinging = isCallerRinging

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-md">
      <div className="bg-gray-900 border border-gray-700 rounded-[3rem] shadow-2xl p-8 w-80 h-[32rem] flex flex-col items-center justify-between">
        
        {/* Caller Info */}
        <div className="flex flex-col items-center mt-8">
          <div className="w-28 h-28 rounded-full bg-gray-800 flex items-center justify-center mb-6 relative border border-gray-700">
            <span className="text-5xl text-gray-400 font-bold">
              ?
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">CareBridge Call</h2>
          <p className="text-gray-400 font-medium">
            {isRinging ? 'Ringing...' : `${Math.floor(duration / 60).toString().padStart(2, '0')}:${(duration % 60).toString().padStart(2, '0')}`}
          </p>
        </div>
        
        {/* Controls */}
        <div className="w-full mb-8">
          <div className="flex justify-center gap-6 mb-8 opacity-80">
            <button 
              onClick={() => setIsMuted(!isMuted)}
              className={`w-14 h-14 rounded-full flex items-center justify-center transition-colors ${isMuted ? 'bg-white text-gray-900' : 'bg-gray-800 text-white border border-gray-700'}`}
            >
              {isMuted ? <MicOff size={24} /> : <Mic size={24} />}
            </button>
            <button className="w-14 h-14 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-white">
              <Volume2 size={24} />
            </button>
          </div>
          
          <div className="flex justify-center">
            <button
              onClick={handleEndCall}
              className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center text-white hover:bg-red-600 shadow-lg shadow-red-500/20 transition-transform hover:scale-105"
            >
              <PhoneOff size={28} />
            </button>
          </div>
        </div>
        
      </div>
    </div>
  )
}
