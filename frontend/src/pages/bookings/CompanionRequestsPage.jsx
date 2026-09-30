import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Check, X, Calendar, User, MapPin, Building, ShieldAlert, Siren, Zap, Clock, Bell } from 'lucide-react'
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
        navigate(`/companion/bookings/${id}`)
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
    <div className="max-w-7xl mx-auto p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-100 pb-6">
        <div>
          <button onClick={() => navigate(-1)} className="text-sm font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1 transition-colors mb-3">
            &larr; Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Pending Care Requests</h1>
          <p className="text-gray-500 mt-1 font-medium">Review and accept care requests in your local area.</p>
        </div>
        <div className="bg-white border border-gray-200 shadow-sm text-gray-700 px-4 py-2.5 rounded-xl font-semibold flex items-center gap-2">
          <Bell size={18} className="text-primary-600" />
          <span>{pendingRequests?.length || 0} Open Request(s)</span>
        </div>
      </div>

      {!isVerified && myProfile && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 p-5 rounded-2xl shadow-sm flex items-start gap-4">
          <div className="bg-amber-100 p-2.5 rounded-xl shrink-0">
            <ShieldAlert className="h-6 w-6 text-amber-600" />
          </div>
          <div>
            <h3 className="text-base font-bold text-amber-900">Verification Required</h3>
            <p className="mt-1 text-sm text-amber-800 font-medium">
              You cannot accept care requests until your mandatory document verification is complete and your profile is approved.
            </p>
            <button onClick={() => navigate('/companion/verification')} className="mt-3 text-sm font-bold text-amber-700 hover:text-amber-800 underline underline-offset-2">
              Complete Verification Now &rarr;
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-center font-semibold">
          {error}
        </div>
      )}

      {!loading && pendingRequests?.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-dashed border-gray-200 shadow-sm">
          <div className="bg-gray-50 p-6 rounded-full mb-4">
            <Calendar className="text-gray-400" size={48} strokeWidth={1.5} />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Pending Requests</h3>
          <p className="text-gray-500 font-medium text-center max-w-sm">
            You're all caught up! Check back later for new bookings matching your profile and location.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {pendingRequests?.map((req) => {
          const isEmergency = req.booking_type === 'EMERGENCY'
          const isInstant = req.booking_type === 'INSTANT'

          return (
            <div
              key={req.id}
              className={`bg-white border rounded-2xl p-6 shadow-sm hover:shadow-md transition-all relative overflow-hidden group flex flex-col ${
                isEmergency ? 'border-red-200' : 'border-gray-100'
              }`}
            >
              {isEmergency && (
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-red-500 to-rose-500" />
              )}

              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="font-bold text-xl text-gray-900">{req.service_name}</h3>
                  <p className="text-sm text-gray-500 font-medium mt-1">ID: #{req.id.substring(0, 8)}</p>
                </div>
                <span
                  className={`text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5 uppercase tracking-wide border ${
                    isEmergency
                      ? 'bg-red-50 text-red-700 border-red-200'
                      : isInstant
                      ? 'bg-amber-50 text-amber-700 border-amber-200'
                      : 'bg-blue-50 text-blue-700 border-blue-200'
                  }`}
                >
                  {isEmergency ? <Siren size={14} /> : isInstant ? <Zap size={14} /> : <Calendar size={14} />}
                  {req.booking_type}
                </span>
              </div>

              <div className="bg-gray-50/50 rounded-xl p-4 space-y-3 mb-6 flex-1">
                <div className="flex items-start gap-3">
                  <User size={16} className="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Patient</p>
                    <p className="font-bold text-gray-900">{req.patient_name}</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <Clock size={16} className="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Schedule</p>
                    <p className="font-bold text-gray-900">{fmt(req.scheduled_start)}</p>
                    {req.duration_hours && <p className="text-xs text-gray-500 mt-0.5">Duration: {req.duration_hours} hrs</p>}
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <MapPin size={16} className="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Pickup Location</p>
                    <p className="font-bold text-gray-900">{req.pickup_address}</p>
                  </div>
                </div>

                {req.hospital_name && (
                  <div className="flex items-start gap-3">
                    <Building size={16} className="text-gray-400 mt-0.5 shrink-0" />
                    <div>
                      <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Destination</p>
                      <p className="font-bold text-gray-900">{req.hospital_name}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-3 mt-auto pt-4 border-t border-gray-100">
                <button
                  onClick={() => handleRejectDirect(req.id)}
                  disabled={actionLoading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-white border border-gray-200 text-gray-700 font-bold text-sm rounded-xl hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors disabled:opacity-50"
                >
                  <X size={16} /> Decline
                </button>
                <button
                  onClick={() => handleAccept(req.id)}
                  disabled={actionLoading || !isVerified}
                  className={`flex-[2] flex items-center justify-center gap-2 px-4 py-3 font-bold text-sm rounded-xl shadow-sm transition-all disabled:opacity-50 ${
                    !isVerified 
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                      : 'bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 text-white hover:shadow-md'
                  }`}
                >
                  <Check size={16} /> Accept Assignment
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
