import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Check, X, Calendar, User, MapPin, Building, ShieldAlert, Siren, Zap } from 'lucide-react'
import { fetchPendingRequests, acceptBookingThunk, rejectBookingThunk } from '../../redux/slices/bookingsSlice'
import { fetchMyProfile } from '../../redux/slices/companionsSlice'

function fmt(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

export default function CompanionRequestsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { pendingRequests, loading, error } = useSelector((s) => s.bookings)
  const { myProfile } = useSelector((s) => s.companions)

  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    dispatch(fetchPendingRequests())
    dispatch(fetchMyProfile())
  }, [dispatch])

  const isVerified = myProfile?.status === 'ACTIVE'

  const handleAccept = async (id) => {
    if (!isVerified) {
      alert('You must complete document verification before accepting requests.')
      return
    }
    if (!window.confirm('Are you sure you want to accept this booking request? You will be responsible for the patient.')) return
    setActionLoading(true)
    try {
      const result = await dispatch(acceptBookingThunk(id))
      if (!result.error) {
        alert('Booking request accepted successfully!')
        navigate(`/bookings/${id}`)
      } else {
        alert(result.payload || 'Failed to accept booking')
      }
    } finally {
      setActionLoading(false)
    }
  }

  const handleRejectDirect = async (id) => {
    if (!window.confirm('Are you sure you want to reject this care request?')) return
    setActionLoading(true)
    try {
      const result = await dispatch(rejectBookingThunk({ id, reason: '' }))
      if (!result.error) {
        dispatch(fetchPendingRequests())
      } else {
        alert(result.payload || 'Failed to reject booking')
      }
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-gray-150 pb-4">
        <div>
          <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline mb-2 block">← Back</button>
          <h1 className="text-2xl font-bold text-gray-900">Pending Care Requests</h1>
          <p className="text-xs text-gray-500 mt-1">Accept care requests in your area to coordinate patient care</p>
        </div>
        <span className="bg-blue-50 text-blue-700 text-xs font-bold px-3 py-1 rounded-full border border-blue-200">
          {pendingRequests?.length || 0} Open Request(s)
        </span>
      </div>

      {!isVerified && myProfile && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md shadow-sm">
          <div className="flex">
            <div className="flex-shrink-0">
              <ShieldAlert className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Verification Required</h3>
              <p className="mt-1 text-sm text-yellow-700">
                You cannot accept care requests until your mandatory document verification is complete and your profile is approved.
              </p>
            </div>
          </div>
        </div>
      )}

      {loading && <p className="text-center text-gray-500 py-8">Loading requests...</p>}
      {error && <p className="text-center text-red-500 py-4">{error}</p>}

      {!loading && pendingRequests?.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-2xl border border-dashed border-gray-300">
          <Calendar className="mx-auto text-gray-400 mb-3 opacity-55" size={40} />
          <h3 className="font-semibold text-gray-700 text-sm">No Pending Requests</h3>
          <p className="text-xs text-gray-400 mt-1">Check back later for new bookings matching your profile.</p>
        </div>
      )}

      <div className="space-y-4">
        {pendingRequests?.map((req) => {
          const isEmergency = req.booking_type === 'EMERGENCY'
          const isInstant = req.booking_type === 'INSTANT'

          return (
            <div
              key={req.id}
              className={`bg-white border rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden ${
                isEmergency ? 'border-red-200 bg-red-50/10' : 'border-gray-200'
              }`}
            >
              {/* Emergency indicator badge */}
              {isEmergency && (
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-red-500" />
              )}

              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-gray-800 text-base">{req.service_name}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-0.5 uppercase ${
                        isEmergency
                          ? 'bg-red-100 text-red-700'
                          : isInstant
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {isEmergency ? (
                        <Siren size={10} />
                      ) : isInstant ? (
                        <Zap size={10} />
                      ) : (
                        <Calendar size={10} />
                      )}
                      {req.booking_type}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1.5 text-xs text-gray-600">
                    <p className="flex items-center gap-1.5 truncate">
                      <User size={14} className="text-gray-400 shrink-0" />
                      Patient: <span className="font-semibold text-gray-800">{req.patient_name}</span>
                    </p>
                    <p className="flex items-center gap-1.5">
                      <Calendar size={14} className="text-gray-400 shrink-0" />
                      Schedule: <span className="font-semibold text-gray-800">{fmt(req.scheduled_start)}</span>
                    </p>
                    <p className="flex items-center gap-1.5 truncate">
                      <MapPin size={14} className="text-gray-400 shrink-0" />
                      Pickup: <span className="font-semibold text-gray-800">{req.pickup_address}</span>
                    </p>
                    {req.hospital_name && (
                      <p className="flex items-center gap-1.5 truncate">
                        <Building size={14} className="text-gray-400 shrink-0" />
                        Hospital: <span className="font-semibold text-gray-800">{req.hospital_name}</span>
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex gap-2 w-full md:w-auto shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-gray-100">
                  <button
                    onClick={() => handleRejectDirect(req.id)}
                    disabled={actionLoading}
                    className="flex-1 md:flex-initial flex items-center justify-center gap-1 px-4 py-2 border border-red-300 text-red-600 font-semibold text-xs rounded-xl hover:bg-red-50 transition-colors disabled:opacity-50"
                  >
                    <X size={14} /> Reject
                  </button>
                  <button
                    onClick={() => handleAccept(req.id)}
                    disabled={actionLoading || !isVerified}
                    className={`flex-1 md:flex-initial flex items-center justify-center gap-1 px-4 py-2 font-semibold text-xs rounded-xl transition-colors disabled:opacity-50 ${
                      !isVerified ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'
                    }`}
                  >
                    <Check size={14} /> Accept Request
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

    </div>
  )
}
