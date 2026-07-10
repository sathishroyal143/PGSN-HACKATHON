import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { Calendar, Zap, Siren, Home, Building2, Star } from 'lucide-react'
import {
  fetchCareServices,
  fetchScheduledServices,
  fetchInstantServices,
  fetchEmergencyServices,
  fetchCategories,
} from '../../redux/slices/servicesSlice'

const TABS = [
  { key: 'all',       label: 'All Services',    icon: null },
  { key: 'SCHEDULED_CARE', label: 'Scheduled',  icon: <Calendar size={14} /> },
  { key: 'INSTANT_CARE',   label: 'Instant',    icon: <Zap size={14} /> },
  { key: 'EMERGENCY_CARE', label: 'Emergency',  icon: <Siren size={14} /> },
]

const CATEGORY_COLORS = {
  SCHEDULED_CARE: 'bg-blue-50 border-blue-200 text-blue-700',
  INSTANT_CARE:   'bg-yellow-50 border-yellow-200 text-yellow-700',
  EMERGENCY_CARE: 'bg-red-50 border-red-200 text-red-700',
}

const CATEGORY_BADGE = {
  SCHEDULED_CARE: 'bg-blue-100 text-blue-700',
  INSTANT_CARE:   'bg-yellow-100 text-yellow-700',
  EMERGENCY_CARE: 'bg-red-100 text-red-700',
}

function ServiceCard({ svc, onClick }) {
  const catCode = svc.category_code
  return (
    <div
      onClick={onClick}
      className={`bg-white border rounded-xl p-4 cursor-pointer hover:shadow-md transition-all ${CATEGORY_COLORS[catCode] || 'border-gray-200'}`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          {svc.icon && <span className="text-lg">{svc.icon}</span>}
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">{svc.service_name}</h3>
        </div>
        <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${CATEGORY_BADGE[catCode] || 'bg-gray-100 text-gray-600'}`}>
          {svc.category_name}
        </span>
      </div>

      {svc.description && (
        <p className="text-xs text-gray-500 line-clamp-2 mb-3">{svc.description}</p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500 mt-auto">
        <div className="flex items-center gap-2">
          {svc.home_visit_supported && (
            <span className="flex items-center gap-0.5 text-green-600"><Home size={11} /> Home</span>
          )}
          {svc.hospital_visit_supported && (
            <span className="flex items-center gap-0.5 text-blue-600"><Building2 size={11} /> Hospital</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {svc.ai_recommended && (
            <span className="flex items-center gap-0.5 text-purple-600"><Star size={11} /> AI Pick</span>
          )}
          <span className="font-semibold text-gray-800">₹{parseFloat(svc.base_price).toFixed(0)}</span>
        </div>
      </div>

      <div className="mt-2 text-xs text-gray-400">
        ⏱ ~{svc.estimated_duration_hours}h
      </div>
    </div>
  )
}

export default function ServicesPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { careServices, loading, error } = useSelector((s) => s.services)
  const { user } = useSelector((s) => s.auth)
  const [activeTab, setActiveTab] = useState('all')

  useEffect(() => {
    dispatch(fetchCategories())
    dispatch(fetchCareServices())
  }, [dispatch])

  const handleTabChange = (key) => {
    setActiveTab(key)
    if (key === 'all') dispatch(fetchCareServices())
    else if (key === 'SCHEDULED_CARE') dispatch(fetchScheduledServices())
    else if (key === 'INSTANT_CARE') dispatch(fetchInstantServices())
    else if (key === 'EMERGENCY_CARE') dispatch(fetchEmergencyServices())
  }

  const role = user?.role?.toLowerCase() || 'family'
  const getBookingsPath = () => {
    if (role === 'companion') return '/companion/history'
    if (role === 'admin') return '/admin/bookings'
    return '/family/bookings'
  }
  const getServicePath = (id) => {
    if (role === 'admin') return `/admin/services/${id}`
    return `/family/services/${id}`
  }

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Care Services</h1>
        <button onClick={() => navigate(getBookingsPath())} className="text-sm text-blue-600 hover:underline">
          My Bookings →
        </button>
      </div>

      {/* Care Mode Tabs */}
      <div className="flex gap-2 flex-wrap">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => handleTabChange(tab.key)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              activeTab === tab.key
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {loading && <p className="text-center text-gray-500 py-8">Loading services…</p>}
      {error && <p className="text-center text-red-500 py-4">{error}</p>}

      {!loading && careServices.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <Calendar size={40} className="mx-auto mb-3 opacity-40" />
          <p>No services found.</p>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {careServices.map((svc) => (
          <ServiceCard
            key={svc.id}
            svc={svc}
            onClick={() => navigate(getServicePath(svc.id))}
          />
        ))}
      </div>
    </div>
  )
}
