import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchCompanions } from '../../redux/slices/companionsSlice'

const AVAILABILITY_COLOR = {
  AVAILABLE: 'bg-green-100 text-green-800',
  BUSY: 'bg-yellow-100 text-yellow-800',
  OFFLINE: 'bg-gray-100 text-gray-600',
}

const VEHICLE_ICON = { NONE: '🚶', BIKE: '🏍️', CAR: '🚗', AUTO: '🛺' }

const getExperienceString = (createdAt) => {
  if (!createdAt) return '0 days'
  const createdDate = new Date(createdAt)
  const now = new Date()
  const diffDays = Math.max(0, Math.floor((now - createdDate) / (1000 * 60 * 60 * 24)))
  
  if (diffDays < 30) return `${diffDays}d exp`
  const diffMonths = Math.floor(diffDays / 30)
  if (diffMonths < 12) return `${diffMonths}mo exp`
  const diffYears = Math.floor(diffMonths / 12)
  return `${diffYears}y exp`
}

export default function CompanionsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { companions, loading, error } = useSelector((s) => s.companions)
  const [query, setQuery] = useState('')

  useEffect(() => {
    dispatch(fetchCompanions(query ? { q: query } : undefined))
  }, [dispatch])

  const handleSearch = (e) => {
    e.preventDefault()
    dispatch(fetchCompanions(query ? { q: query } : undefined))
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Care Companions</h1>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name…"
          className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >
          Search
        </button>
      </form>

      {loading && <p className="text-center text-gray-500 py-8">Loading…</p>}
      {error   && <p className="text-center text-red-500 py-4">{error}</p>}

      {!loading && companions.length === 0 && (
        <p className="text-center text-gray-500 py-12">No companions found.</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {companions.map((c) => (
          <div
            key={c.id}
            onClick={() => navigate(`/companions/${c.id}`)}
            className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-3">
              {c.profile_picture ? (
                <img src={c.profile_picture} alt="" className="w-12 h-12 rounded-full object-cover" />
              ) : (
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg">
                  {c.full_name?.[0] || '?'}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className="font-semibold text-gray-900 truncate">{c.full_name}</p>
                  <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${AVAILABILITY_COLOR[c.availability_status] || 'bg-gray-100 text-gray-600'}`}>
                    {c.availability_status}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                  <span>⭐ {Number(c.average_rating).toFixed(1)} ({c.total_reviews})</span>
                  <span>{getExperienceString(c.created_at)}</span>
                  <span>{VEHICLE_ICON[c.vehicle_type] || ''}</span>
                </div>
                {c.ai_trust_score > 0 && (
                  <p className="text-xs text-indigo-600 mt-0.5">AI Score: {c.ai_trust_score}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
