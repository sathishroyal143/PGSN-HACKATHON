import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { Home, Building2, Siren, Star, Clock } from 'lucide-react'
import { fetchCareService, clearCurrentCareService } from '../../redux/slices/servicesSlice'
import { getAllPackages, calculatePrice } from '../../api/servicesApi'

const CATEGORY_COLORS = {
  SCHEDULED_CARE: 'text-blue-600 bg-blue-50',
  INSTANT_CARE:   'text-yellow-600 bg-yellow-50',
  EMERGENCY_CARE: 'text-red-600 bg-red-50',
}

export default function ServiceDetailPage() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { currentCareService: svc, loading, error } = useSelector((s) => s.services)
  const { user } = useSelector((s) => s.auth)

  const [hours, setHours] = useState(2)
  const [isEmergency, setIsEmergency] = useState(false)
  const [isNight, setIsNight] = useState(false)
  const [priceResult, setPriceResult] = useState(null)
  const [calcLoading, setCalcLoading] = useState(false)
  const [linkedPackageId, setLinkedPackageId] = useState(null)

  useEffect(() => {
    dispatch(fetchCareService(id))
    return () => dispatch(clearCurrentCareService())
  }, [dispatch, id])

  // Find linked package for price calculator
  useEffect(() => {
    if (!svc) return
    getAllPackages().then((res) => {
      const pkgs = res.data?.data || []
      // Match by service_code embedded in package name or slug
      const match = pkgs.find((p) =>
        p.slug?.includes(svc.service_code?.toLowerCase().replace(/_/g, '-')) ||
        p.name?.toLowerCase().includes(svc.service_name?.toLowerCase().slice(0, 10))
      )
      if (match) setLinkedPackageId(match.id)
    }).catch(() => {})
  }, [svc])

  const handleCalc = async (e) => {
    e.preventDefault()
    if (!linkedPackageId) return
    setCalcLoading(true)
    try {
      const res = await calculatePrice({ package_id: linkedPackageId, hours, is_emergency: isEmergency, is_night: isNight })
      setPriceResult(res.data?.data || res.data)
    } catch {
      setPriceResult(null)
    } finally {
      setCalcLoading(false)
    }
  }

  if (loading && !svc) return <div className="p-6 text-center text-gray-500">Loading…</div>
  if (error) return <div className="p-6 text-center text-red-500">{error}</div>
  if (!svc) return null

  const catCode = svc.service_category?.code || svc.category_code
  const pricing = svc.pricing

  const role = user?.role?.toLowerCase() || 'family'
  const getServicesPath = () => {
    if (role === 'admin') return '/admin/services'
    return '/family/services'
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <button onClick={() => navigate(getServicesPath())} className="text-sm text-blue-600 hover:underline">
        ← Back to Services
      </button>

      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{svc.service_name}</h1>
            <span className={`inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${CATEGORY_COLORS[catCode] || 'text-gray-600 bg-gray-100'}`}>
              {svc.service_category?.name || svc.category_name}
            </span>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">₹{parseFloat(svc.base_price).toFixed(0)}</p>
            <p className="text-xs text-gray-400">base price</p>
          </div>
        </div>

        {svc.description && (
          <p className="mt-3 text-sm text-gray-600 border-t border-gray-100 pt-3">{svc.description}</p>
        )}

        {/* Feature badges */}
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="flex items-center gap-1 text-xs px-2 py-1 bg-gray-50 rounded-full text-gray-600">
            <Clock size={12} /> ~{svc.estimated_duration_hours}h
          </span>
          {svc.home_visit_supported && (
            <span className="flex items-center gap-1 text-xs px-2 py-1 bg-green-50 rounded-full text-green-700">
              <Home size={12} /> Home Visit
            </span>
          )}
          {svc.hospital_visit_supported && (
            <span className="flex items-center gap-1 text-xs px-2 py-1 bg-blue-50 rounded-full text-blue-700">
              <Building2 size={12} /> Hospital Visit
            </span>
          )}
          {svc.emergency_supported && (
            <span className="flex items-center gap-1 text-xs px-2 py-1 bg-red-50 rounded-full text-red-700">
              <Siren size={12} /> Emergency
            </span>
          )}
          {svc.ai_recommended && (
            <span className="flex items-center gap-1 text-xs px-2 py-1 bg-purple-50 rounded-full text-purple-700">
              <Star size={12} /> AI Recommended
            </span>
          )}
        </div>
      </div>

      {/* Pricing breakdown */}
      {pricing && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-800 mb-3 text-sm">Pricing Details</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
            <div className="bg-gray-50 rounded-lg p-2 text-center">
              <p className="text-xs text-gray-400">Base Price</p>
              <p className="font-semibold text-gray-800">₹{parseFloat(pricing.base_price).toFixed(0)}</p>
            </div>
            {parseFloat(pricing.emergency_charge) > 0 && (
              <div className="bg-red-50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-400">Emergency Charge</p>
                <p className="font-semibold text-red-700">+₹{parseFloat(pricing.emergency_charge).toFixed(0)}</p>
              </div>
            )}
            {parseFloat(pricing.instant_charge) > 0 && (
              <div className="bg-yellow-50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-400">Instant Charge</p>
                <p className="font-semibold text-yellow-700">+₹{parseFloat(pricing.instant_charge).toFixed(0)}</p>
              </div>
            )}
            {parseFloat(pricing.tax) > 0 && (
              <div className="bg-gray-50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-400">Tax (GST)</p>
                <p className="font-semibold text-gray-700">+₹{parseFloat(pricing.tax).toFixed(0)}</p>
              </div>
            )}
            {parseFloat(pricing.discount) > 0 && (
              <div className="bg-green-50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-400">Discount</p>
                <p className="font-semibold text-green-700">-₹{parseFloat(pricing.discount).toFixed(0)}</p>
              </div>
            )}
            <div className="bg-blue-50 rounded-lg p-2 text-center">
              <p className="text-xs text-gray-400">Total Price</p>
              <p className="font-bold text-blue-700">₹{parseFloat(pricing.total_price).toFixed(0)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Price Calculator (only if linked package found) */}
      {linkedPackageId && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="font-semibold text-gray-800 mb-3 text-sm">Price Calculator</h2>
          <form onSubmit={handleCalc} className="space-y-3">
            <div className="flex items-center gap-4">
              <label className="text-sm text-gray-600 w-20">Hours</label>
              <input
                type="number" min={0.5} max={24} step={0.5} value={hours}
                onChange={(e) => setHours(Number(e.target.value))}
                className="w-24 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
            <div className="flex gap-6">
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" checked={isEmergency} onChange={(e) => setIsEmergency(e.target.checked)} className="rounded" />
                Emergency
              </label>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" checked={isNight} onChange={(e) => setIsNight(e.target.checked)} className="rounded" />
                Night hours
              </label>
            </div>
            <button
              type="submit" disabled={calcLoading}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {calcLoading ? 'Calculating…' : 'Calculate Price'}
            </button>
          </form>

          {priceResult && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Estimated Total</p>
              <p className="text-2xl font-bold text-blue-700">₹{priceResult.total?.toFixed(2) || priceResult.total_price}</p>
              <div className="mt-2 space-y-1">
                {Object.entries(priceResult).filter(([k]) => k !== 'total').map(([k, v]) => (
                  <div key={k} className="flex justify-between text-xs text-gray-600">
                    <span className="capitalize">{k.replace(/_/g, ' ')}</span>
                    <span>₹{typeof v === 'number' ? v.toFixed(2) : v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Book CTA */}
      <button
        onClick={() => {
          const rolePath = user?.role?.toLowerCase() || 'family'
          navigate(`/${rolePath}/bookings/new?serviceId=${svc.id}`)
        }}
        className="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors"
      >
        Book This Service
      </button>
    </div>
  )
}
