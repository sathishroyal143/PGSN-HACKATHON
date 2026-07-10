import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { fetchJourney, fetchJourneyByBooking, updateStep, saveNotes } from '../../redux/slices/careJourneySlice'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { MapPin, CheckCircle, Clock, FileText, UploadCloud, Bell, Activity } from 'lucide-react'

// Fix Leaflet marker icons issue in React
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
})

const STEP_COLOR = {
  PENDING: 'bg-gray-100 text-gray-500',
  IN_PROGRESS: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  DONE: 'bg-green-100 text-green-800 border-green-300',
}

const STEP_ICONS = {
  PENDING: <Clock size={16} />,
  IN_PROGRESS: <Activity size={16} />,
  DONE: <CheckCircle size={16} />
}

export default function JourneyDetailPage() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { currentJourney: journey, loading, error } = useSelector((s) => s.careJourney)
  const user = useSelector((s) => s.auth.user || s.user.profile)
  const location = useLocation()
  const isCompanion = location.pathname.startsWith('/companion')
  
  const [notes, setNotes] = useState('')
  const [savingNotes, setSavingNotes] = useState(false)
  const [activeUploadStep, setActiveUploadStep] = useState(null)

  useEffect(() => {
    dispatch(fetchJourney(id)).unwrap().catch(() => {
      dispatch(fetchJourneyByBooking(id))
    })
  }, [dispatch, id])

  useEffect(() => {
    if (journey) setNotes(journey.companion_notes || '')
  }, [journey])

  const handleAdvance = (stepCode, newStatus) => {
    dispatch(updateStep({ id, data: { step_code: stepCode, status: newStatus } }))
  }

  const handleSaveNotes = async () => {
    setSavingNotes(true)
    await dispatch(saveNotes({ id, data: { companion_notes: notes } }))
    setSavingNotes(false)
  }

  const handleFileUpload = (e) => {
    // Placeholder for actual file upload to API
    const file = e.target.files[0]
    if (file) {
      alert(`File "${file.name}" uploaded successfully for step ${activeUploadStep}!`)
      setActiveUploadStep(null)
    }
  }

  if (loading && !journey) return <div className="p-6 text-center text-gray-500 flex flex-col items-center justify-center h-64"><Activity className="animate-spin text-blue-500 mb-4" size={32}/> Loading Care Journey…</div>
  if (error) return <div className="p-6 text-center text-red-500">{error}</div>
  if (!journey) return null

  // Calculate Progress Percentage
  const totalSteps = journey.steps?.length || 1
  const completedSteps = journey.steps?.filter(s => s.status === 'DONE').length || 0
  const progressPercent = Math.round((completedSteps / totalSteps) * 100)
  
  // Dummy Location for Map
  const position = [17.4326, 78.4071] // Hyderabad placeholder

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline mb-2 flex items-center gap-1">
        ← Back
      </button>
      
      {/* Header Section */}
      <div className="bg-white border-2 border-blue-100 rounded-xl p-5 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Care Journey: {journey.patient_name}</h1>
            {journey.companion_name && (
              <p className="text-sm text-gray-600 font-medium mt-1">Companion: {journey.companion_name}</p>
            )}
          </div>
          <div className="flex flex-col items-end">
            <span className={`px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wider ${
              journey.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
              journey.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
              'bg-red-100 text-red-800'
            }`}>
              {journey.status}
            </span>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-xs font-semibold text-gray-500 mb-1">
            <span>Overall Progress</span>
            <span>{progressPercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-500" style={{ width: `${progressPercent}%` }}></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Timeline (Left Column) */}
        <div className="md:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <h2 className="font-bold text-gray-900 mb-6 text-lg border-b pb-2">Journey Timeline</h2>
          <div className="relative border-l-2 border-gray-200 ml-3 space-y-6">
            {journey.steps?.map((step, index) => {
              const isActive = journey.current_step === step.step_code
              const isDone = step.status === 'DONE'
              
              return (
                <div key={step.id} className="relative pl-6">
                  {/* Timeline Dot */}
                  <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 ${
                    isDone ? 'bg-green-500 border-green-500' : 
                    isActive ? 'bg-yellow-400 border-yellow-500 animate-pulse' : 
                    'bg-white border-gray-300'
                  }`}></div>
                  
                  <div className={`p-4 rounded-lg border ${
                    isActive ? 'border-yellow-400 bg-yellow-50 shadow-sm' : 
                    isDone ? 'border-green-200 bg-green-50/30' : 'border-gray-100 bg-gray-50'
                  }`}>
                    <div className="flex justify-between items-start mb-2">
                      <h3 className={`font-semibold text-sm ${isDone ? 'text-gray-900' : 'text-gray-700'}`}>
                        {step.step_code.replace(/_/g, ' ')}
                      </h3>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1 border ${STEP_COLOR[step.status]}`}>
                        {STEP_ICONS[step.status]} {step.status}
                      </span>
                    </div>
                    
                    {step.started_at && !isDone && (
                      <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                        <Clock size={12}/> Started: {new Date(step.started_at).toLocaleTimeString()}
                      </p>
                    )}
                    {step.completed_at && (
                      <p className="text-xs text-green-700 flex items-center gap-1 mt-1">
                        <CheckCircle size={12}/> Completed: {new Date(step.completed_at).toLocaleTimeString()}
                      </p>
                    )}
                    
                    {step.notes && (
                      <div className="mt-3 bg-white p-2 rounded border border-gray-200 text-sm text-gray-600 italic">
                        "{step.notes}"
                      </div>
                    )}

                    {/* Companion Action Buttons */}
                    {isCompanion && journey.status === 'ACTIVE' && (
                      <div className="mt-4 flex flex-wrap gap-2">
                        {step.status === 'PENDING' && (
                          <button
                            onClick={() => handleAdvance(step.step_code, 'IN_PROGRESS')}
                            className="text-xs px-3 py-1.5 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 transition"
                          >
                            Start Step
                          </button>
                        )}
                        {step.status === 'IN_PROGRESS' && (
                          <>
                            <button
                              onClick={() => handleAdvance(step.step_code, 'DONE')}
                              className="text-xs px-3 py-1.5 bg-green-600 text-white font-medium rounded hover:bg-green-700 transition"
                            >
                              Mark as Completed
                            </button>
                            <div className="relative">
                              <button
                                onClick={() => setActiveUploadStep(step.step_code === activeUploadStep ? null : step.step_code)}
                                className="text-xs px-3 py-1.5 bg-gray-200 text-gray-800 font-medium rounded hover:bg-gray-300 transition flex items-center gap-1"
                              >
                                <UploadCloud size={14}/> Upload Files
                              </button>
                              {activeUploadStep === step.step_code && (
                                <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-200 rounded shadow-lg p-2 z-10">
                                  <input type="file" onChange={handleFileUpload} className="text-xs w-full" />
                                </div>
                              )}
                            </div>
                            <button className="text-xs px-3 py-1.5 bg-orange-100 text-orange-800 font-medium rounded hover:bg-orange-200 transition flex items-center gap-1">
                              <MapPin size={14}/> Share Location
                            </button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Column (Map & Notes) */}
        <div className="space-y-6">
          {/* Live Tracking Map */}
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
            <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-blue-50">
              <h2 className="font-bold text-gray-900 flex items-center gap-2">
                <MapPin className="text-blue-600" size={18}/> Live Tracking
              </h2>
              {journey.status === 'ACTIVE' && <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>}
            </div>
            <div className="h-64 w-full bg-gray-100 relative">
              <MapContainer center={position} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <Marker position={position}>
                  <Popup>Companion's Current Location</Popup>
                </Marker>
              </MapContainer>
            </div>
            <div className="p-4 text-xs text-gray-600 flex justify-between bg-white">
              <span>ETA: 15 mins</span>
              <span>Distance: 2.3 km</span>
            </div>
          </div>

          {/* Companion Notes */}
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <FileText className="text-gray-500" size={18}/> Overall Notes
            </h2>
            
            {isCompanion && journey.status === 'ACTIVE' ? (
              <>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={4}
                  className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
                  placeholder="Keep the family updated with general notes..."
                />
                <button
                  onClick={handleSaveNotes}
                  disabled={savingNotes}
                  className="mt-3 w-full py-2 bg-gray-900 text-white text-sm font-semibold rounded-lg hover:bg-gray-800 transition disabled:opacity-50"
                >
                  {savingNotes ? 'Saving...' : 'Update Notes'}
                </button>
              </>
            ) : (
              <div className="bg-gray-50 border border-gray-100 rounded-lg p-3 text-sm text-gray-700 min-h-[100px] whitespace-pre-wrap">
                {journey.companion_notes || "No general notes provided yet."}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
