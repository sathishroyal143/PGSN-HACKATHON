import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchCompanion, fetchMyProfile, setAvailability } from '../../redux/slices/companionsSlice'

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const AVAILABILITY_COLOR = {
  AVAILABLE: 'bg-green-100 text-green-800',
  BUSY: 'bg-yellow-100 text-yellow-800',
  OFFLINE: 'bg-gray-100 text-gray-600',
}

const STATUS_COLOR = {
  ACTIVE: 'bg-green-100 text-green-800',
  PENDING_VERIFICATION: 'bg-yellow-100 text-yellow-800',
  INACTIVE: 'bg-gray-100 text-gray-600',
  SUSPENDED: 'bg-red-100 text-red-800',
}

const getExperienceString = (createdAt) => {
  if (!createdAt) return '0 days experience'
  const createdDate = new Date(createdAt)
  const now = new Date()
  const diffDays = Math.max(0, Math.floor((now - createdDate) / (1000 * 60 * 60 * 24)))
  
  if (diffDays < 30) return `${diffDays} days experience`
  const diffMonths = Math.floor(diffDays / 30)
  if (diffMonths < 12) return `${diffMonths} months experience`
  const diffYears = Math.floor(diffMonths / 12)
  return `${diffYears} yrs experience`
}

export default function CompanionDetailPage() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { currentCompanion: companion, myProfile, loading, error } = useSelector((s) => s.companions)

  const isMe = !id
  const profile = isMe ? myProfile : companion

  useEffect(() => {
    if (isMe) dispatch(fetchMyProfile())
    else dispatch(fetchCompanion(id))
  }, [dispatch, id, isMe])

  const handleAvailability = (status) => {
    dispatch(setAvailability({ availability_status: status }))
  }

  if (loading && !profile) return <div className="p-6 text-center text-gray-500">Loading…</div>
  if (error) return <div className="p-6 text-center text-red-500">{error}</div>
  if (!profile) return null

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-5">
      {/* Back */}
      {!isMe && (
        <button onClick={() => navigate(-1)} className="text-sm text-blue-600 hover:underline">
          ← Back
        </button>
      )}

      {/* Header card */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-start gap-4">
          {profile.profile_picture ? (
            <img src={profile.profile_picture} alt="" className="w-16 h-16 rounded-full object-cover" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-2xl">
              {profile.full_name?.[0] || '?'}
            </div>
          )}
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold text-gray-900">{profile.full_name}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOR[profile.status] || 'bg-gray-100 text-gray-600'}`}>
                {profile.status?.replace(/_/g, ' ')}
              </span>
            </div>
            {profile.email && <p className="text-sm text-gray-500 mt-0.5">{profile.email}</p>}
            {profile.phone && <p className="text-sm text-gray-500">{profile.phone}</p>}
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <span>⭐ {Number(profile.average_rating).toFixed(1)} ({profile.total_reviews} reviews)</span>
              <span>{getExperienceString(profile.created_at)}</span>
              <span>{profile.total_bookings_completed} bookings</span>
            </div>
          </div>
        </div>

        {profile.bio && (
          <p className="mt-3 text-sm text-gray-700 border-t border-gray-100 pt-3">{profile.bio}</p>
        )}

        {/* Availability toggle — only for own profile */}
        {isMe && profile.status === 'ACTIVE' && (
          <div className="mt-4 flex gap-2 border-t border-gray-100 pt-4">
            <span className="text-sm text-gray-600 self-center mr-1">Set availability:</span>
            {['AVAILABLE', 'BUSY', 'OFFLINE'].map((s) => (
              <button
                key={s}
                onClick={() => handleAvailability(s)}
                disabled={profile.availability_status === s}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors
                  ${profile.availability_status === s
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'}`}
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Skills */}
      {profile.skills?.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h2 className="font-semibold text-gray-800 mb-3">Skills</h2>
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((s) => (
              <span
                key={s.id}
                className={`px-3 py-1 rounded-full text-sm border ${s.verified ? 'bg-green-50 border-green-300 text-green-800' : 'bg-gray-50 border-gray-200 text-gray-600'}`}
              >
                {s.skill.replace(/_/g, ' ')}
                {s.verified && ' ✓'}
                <span className="ml-1 text-xs opacity-60">L{s.proficiency_level}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Languages & Certifications */}
      {(profile.languages_spoken?.length > 0 || profile.certifications?.length > 0) && (
        <div className="bg-white border border-gray-200 rounded-lg p-5 grid grid-cols-2 gap-4">
          {profile.languages_spoken?.length > 0 && (
            <div>
              <h2 className="font-semibold text-gray-800 mb-2 text-sm">Languages</h2>
              <div className="flex flex-wrap gap-1">
                {profile.languages_spoken.map((l) => (
                  <span key={l} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{l}</span>
                ))}
              </div>
            </div>
          )}
          {profile.certifications?.length > 0 && (
            <div>
              <h2 className="font-semibold text-gray-800 mb-2 text-sm">Certifications</h2>
              <ul className="space-y-0.5">
                {profile.certifications.map((c, i) => (
                  <li key={i} className="text-sm text-gray-700">• {c}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Availability Slots */}
      {profile.availability_slots?.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h2 className="font-semibold text-gray-800 mb-3">Weekly Availability</h2>
          <div className="space-y-2">
            {profile.availability_slots.filter((s) => s.is_active).map((slot) => (
              <div key={slot.id} className="flex items-center gap-3 text-sm">
                <span className="w-10 font-medium text-gray-600">{DAYS[slot.day_of_week]}</span>
                <span className="text-gray-800">{slot.start_time} – {slot.end_time}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vehicle */}
      {profile.vehicle_type && profile.vehicle_type !== 'NONE' && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h2 className="font-semibold text-gray-800 mb-1">Vehicle</h2>
          <p className="text-sm text-gray-700">
            {profile.vehicle_type}
            {profile.vehicle_number && ` — ${profile.vehicle_number}`}
          </p>
        </div>
      )}
    </div>
  )
}
