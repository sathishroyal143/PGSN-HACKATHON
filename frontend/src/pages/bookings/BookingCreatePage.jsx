import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Calendar, Clock, MapPin, User, Building, ShieldAlert, CheckCircle, ArrowLeft, ArrowRight } from 'lucide-react'
import { fetchPatients } from '../../redux/slices/patientSlice'
import { fetchCareServices } from '../../redux/slices/servicesSlice'
import { addBooking } from '../../redux/slices/bookingsSlice'
import { calculatePrice } from '../../api/servicesApi'
import { getAllPackages } from '../../api/servicesApi'

const STEPS = [
  { title: 'Select Patient', desc: 'Who is receiving care?' },
  { title: 'Care Details', desc: 'Select service & category' },
  { title: 'Logistics', desc: 'Pickup & hospital location' },
  { title: 'Review & Book', desc: 'Confirm details' },
]

export default function BookingCreatePage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const initialServiceId = searchParams.get('serviceId')

  const { list: patients, loading: patientsLoading } = useSelector((s) => s.patient)
  const { careServices, loading: servicesLoading } = useSelector((s) => s.services)
  const { loading: bookingLoading, error: bookingError } = useSelector((s) => s.bookings)
  const { user } = useSelector((s) => s.auth)

  const [step, setStep] = useState(0)

  // Form state
  const [patientId, setPatientId] = useState('')
  const [careServiceId, setCareServiceId] = useState(initialServiceId || '')
  const [bookingType, setBookingType] = useState('SCHEDULED')
  const [startDate, setStartDate] = useState('')
  const [startTime, setStartTime] = useState('')
  const [hours, setHours] = useState(2)
  const [pickupAddress, setPickupAddress] = useState('')
  const [hospitalName, setHospitalName] = useState('')
  const [hospitalAddress, setHospitalAddress] = useState('')
  const [requiresWheelchair, setRequiresWheelchair] = useState(false)
  const [requiresOxygen, setRequiresOxygen] = useState(false)
  const [specialInstructions, setSpecialInstructions] = useState('')

  // Price calculation state
  const [estimatedPrice, setEstimatedPrice] = useState(null)
  const [priceLoading, setPriceLoading] = useState(false)
  const [linkedPackageId, setLinkedPackageId] = useState(null)

  useEffect(() => {
    dispatch(fetchPatients())
    dispatch(fetchCareServices())
  }, [dispatch])

  // Select default patient if available
  useEffect(() => {
    if (patients && patients.length > 0 && !patientId) {
      const primary = patients.find((p) => p.is_primary)
      setPatientId(primary ? primary.id : patients[0].id)
    }
  }, [patients])

  // Resolve linked package whenever service changes
  const selectedService = careServices.find((s) => s.id === careServiceId)
  useEffect(() => {
    if (!selectedService) return
    getAllPackages().then((res) => {
      const pkgs = res.data?.data || []
      const match = pkgs.find((p) =>
        p.slug?.includes(selectedService.service_code?.toLowerCase().replace(/_/g, '-')) ||
        p.name?.toLowerCase().includes(selectedService.service_name?.toLowerCase().slice(0, 10))
      )
      if (match) {
        setLinkedPackageId(match.id)
      } else {
        setLinkedPackageId(null)
      }
    }).catch(() => setLinkedPackageId(null))

    // Set default booking type depending on service category code
    const categoryCode = selectedService.category_code || selectedService.service_category?.code
    if (categoryCode) {
      if (categoryCode.includes('EMERGENCY')) {
        setBookingType('EMERGENCY')
      } else if (categoryCode.includes('INSTANT')) {
        setBookingType('INSTANT')
      } else {
        setBookingType('SCHEDULED')
      }
    }
  }, [careServiceId, selectedService, careServices])

  // Auto-fill dates for Emergency and Instant care
  useEffect(() => {
    if (bookingType === 'EMERGENCY' || bookingType === 'INSTANT') {
      const now = new Date()
      // format date to YYYY-MM-DD
      const yyyy = now.getFullYear()
      const mm = String(now.getMonth() + 1).padStart(2, '0')
      const dd = String(now.getDate()).padStart(2, '0')
      setStartDate(`${yyyy}-${mm}-${dd}`)

      // format time to HH:MM
      const hh = String(now.getHours()).padStart(2, '0')
      const min = String(now.getMinutes()).padStart(2, '0')
      setStartTime(`${hh}:${min}`)
    }
  }, [bookingType])

  // Calculate pricing when dependencies change
  useEffect(() => {
    if (!linkedPackageId || !startDate || !startTime) {
      setEstimatedPrice(null)
      return
    }

    const calcPrice = async () => {
      setPriceLoading(true)
      try {
        const res = await calculatePrice({
          package_id: linkedPackageId,
          hours,
          is_emergency: bookingType === 'EMERGENCY',
          is_night: false, // Default night factor logic
        })
        setEstimatedPrice(res.data?.data || res.data)
      } catch (err) {
        setEstimatedPrice(null)
      } finally {
        setPriceLoading(false)
      }
    }

    const timer = setTimeout(calcPrice, 400)
    return () => clearTimeout(timer)
  }, [linkedPackageId, hours, bookingType, startDate, startTime])

  const handleNext = () => {
    if (step === 0 && !patientId) return alert('Please select a patient.')
    if (step === 1 && (!careServiceId || !startDate || !startTime)) {
      return alert('Please select a care service, date, and time.')
    }
    if (step === 2 && !pickupAddress) {
      return alert('Please enter a pickup address.')
    }
    setStep((prev) => Math.min(prev + 1, STEPS.length - 1))
  }

  const handleBack = () => {
    setStep((prev) => Math.max(prev - 1, 0))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!patientId || !careServiceId || !startDate || !startTime || !pickupAddress) {
      return alert('Please fill in all required fields.')
    }

    const startDateTime = new Date(`${startDate}T${startTime}`)
    const endDateTime = new Date(startDateTime.getTime() + hours * 60 * 60 * 1000)

    const payload = {
      patient_id: patientId,
      care_service_id: careServiceId,
      booking_type: bookingType,
      scheduled_start: startDateTime.toISOString(),
      scheduled_end: endDateTime.toISOString(),
      pickup_address: pickupAddress,
      hospital_name: hospitalName,
      hospital_address: hospitalAddress,
      requires_wheelchair: requiresWheelchair,
      requires_oxygen: requiresOxygen,
      special_instructions: specialInstructions,
    }

    const result = await dispatch(addBooking(payload))
    if (!result.error) {
      const newBooking = result.payload
      const role = user?.role?.toLowerCase() || 'family'
      navigate(`/${role}/bookings/${newBooking.id}`)
    }
  }

  const activePatient = patients?.find((p) => p.id === patientId)
  const role = user?.role?.toLowerCase() || 'family'

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      {/* Back link */}
      <button
        onClick={() => {
          const rolePath = user?.role?.toLowerCase() || 'family'
          navigate(`/${rolePath}/services`)
        }}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft size={16} /> Back to Services
      </button>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
        {/* Progress Indicator */}
        <div className="bg-gray-50 border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="font-bold text-gray-800 text-lg">Book Care Companion</h2>
          <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">
            Step {step + 1} of {STEPS.length}
          </span>
        </div>

        {/* Step Tabs header */}
        <div className="grid grid-cols-4 border-b border-gray-200 text-center text-xs">
          {STEPS.map((s, idx) => (
            <div
              key={idx}
              className={`py-3 border-r border-gray-100 last:border-r-0 font-medium ${
                step === idx
                  ? 'text-blue-600 border-b-2 border-b-blue-600 bg-blue-50/20'
                  : step > idx
                  ? 'text-green-600'
                  : 'text-gray-400'
              }`}
            >
              <div className="font-bold">{idx + 1}. {s.title}</div>
              <div className="text-[10px] text-gray-400 font-normal hidden sm:block mt-0.5">{s.desc}</div>
            </div>
          ))}
        </div>

        <div className="p-6">
          {bookingError && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
              {bookingError}
            </div>
          )}

          {/* STEP 0: SELECT PATIENT */}
          {step === 0 && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
                <User size={18} className="text-blue-500" /> Who is the patient?
              </h3>
              {patientsLoading ? (
                <p className="text-sm text-gray-500 py-4">Loading patients...</p>
              ) : patients?.length === 0 ? (
                <div className="text-center py-6 bg-gray-50 border rounded-xl space-y-2">
                  <p className="text-sm text-gray-500">No patient profiles found.</p>
                  <button
                    type="button"
                    onClick={() => {
                      const rolePath = user?.role?.toLowerCase() || 'family'
                      navigate(`/${rolePath}/patients`)
                    }}
                    className="px-4 py-2 bg-blue-600 text-white text-xs rounded-lg font-medium hover:bg-blue-700"
                  >
                    + Create Patient Profile
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {patients.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => setPatientId(p.id)}
                      className={`border rounded-xl p-4 cursor-pointer hover:border-blue-400 transition-all flex items-start gap-3 relative ${
                        patientId === p.id ? 'border-blue-600 bg-blue-50/20 ring-2 ring-blue-500/20' : 'border-gray-200'
                      }`}
                    >
                      <div className="bg-blue-50 text-blue-600 p-2 rounded-lg mt-0.5">
                        <User size={18} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-800 text-sm truncate">
                          {p.first_name} {p.last_name}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          Age: {p.date_of_birth ? new Date().getFullYear() - new Date(p.date_of_birth).getFullYear() : 'N/A'} | {p.gender}
                        </p>
                        <p className="text-xs text-gray-400 truncate mt-1">
                          🩸 Blood Group: {p.blood_group || 'Unknown'}
                        </p>
                      </div>
                      {patientId === p.id && (
                        <CheckCircle size={18} className="text-blue-600 absolute right-3 top-3 shrink-0" />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* STEP 1: CARE DETAILS */}
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
                <Clock size={18} className="text-blue-500" /> Select Care Services & Schedule
              </h3>
              
              <div className="space-y-3">
                <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Care Service
                </label>
                {servicesLoading ? (
                  <p className="text-sm text-gray-500 py-2">Loading services...</p>
                ) : (
                  <select
                    value={careServiceId}
                    onChange={(e) => setCareServiceId(e.target.value)}
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none bg-white"
                  >
                    <option value="">-- Choose a Care Service --</option>
                    {careServices.map((svc) => (
                      <option key={svc.id} value={svc.id}>
                        {svc.service_name} (₹{parseFloat(svc.base_price).toFixed(0)}) [{svc.category_name || 'Care'}]
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {selectedService && (
                <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-xl text-xs border border-gray-150">
                  <div>
                    <span className="text-gray-500 block">Service Mode</span>
                    <span className="font-semibold text-gray-800 capitalize">
                      {(selectedService.category_code || selectedService.service_category?.code || 'scheduled').toLowerCase().replace('_', ' ')}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 block">Estimated Base Price</span>
                    <span className="font-semibold text-gray-800">₹{parseFloat(selectedService.base_price).toFixed(0)}</span>
                  </div>
                </div>
              )}

              {/* Service Type Selection */}
              <div className="grid grid-cols-3 gap-2">
                {['SCHEDULED', 'INSTANT', 'EMERGENCY'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setBookingType(type)}
                    className={`py-2 rounded-lg border text-xs font-bold transition-all ${
                      bookingType === type
                        ? type === 'EMERGENCY'
                          ? 'bg-red-50 border-red-500 text-red-700 font-extrabold ring-1 ring-red-500'
                          : type === 'INSTANT'
                          ? 'bg-yellow-50 border-yellow-500 text-yellow-700 font-extrabold ring-1 ring-yellow-500'
                          : 'bg-blue-50 border-blue-500 text-blue-700 font-extrabold ring-1 ring-blue-500'
                        : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>

              {bookingType === 'EMERGENCY' && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-xs flex items-start gap-2">
                  <ShieldAlert size={16} className="shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Emergency Booking:</span> Highest priority. Nearest companion will be dispatched immediately. Scheduling validations are bypassed.
                  </div>
                </div>
              )}

              {/* Date & Time fields */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Date</label>
                  <input
                    type="date"
                    value={startDate}
                    disabled={bookingType === 'EMERGENCY' || bookingType === 'INSTANT'}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100 disabled:text-gray-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Start Time</label>
                  <input
                    type="time"
                    value={startTime}
                    disabled={bookingType === 'EMERGENCY' || bookingType === 'INSTANT'}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none disabled:bg-gray-100 disabled:text-gray-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Duration (Hours)</label>
                  <input
                    type="number"
                    min={1}
                    max={12}
                    value={hours}
                    onChange={(e) => setHours(Number(e.target.value))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: LOGISTICS */}
          {step === 2 && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
                <MapPin size={18} className="text-blue-500" /> Destination & Equipment
              </h3>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Pickup Address *</label>
                  <textarea
                    rows={2}
                    value={pickupAddress}
                    onChange={(e) => setPickupAddress(e.target.value)}
                    placeholder="Enter full home address or pickup location"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-500 mb-1">Hospital Name</label>
                    <input
                      type="text"
                      value={hospitalName}
                      onChange={(e) => setHospitalName(e.target.value)}
                      placeholder="e.g. Apollo Hospital"
                      className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-500 mb-1">Hospital Address</label>
                    <input
                      type="text"
                      value={hospitalAddress}
                      onChange={(e) => setHospitalAddress(e.target.value)}
                      placeholder="Enter hospital location"
                      className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="flex gap-4 pt-2">
                  <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={requiresWheelchair}
                      onChange={(e) => setRequiresWheelchair(e.target.checked)}
                      className="rounded text-blue-600 focus:ring-blue-400"
                    />
                    Requires Wheelchair
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={requiresOxygen}
                      onChange={(e) => setRequiresOxygen(e.target.checked)}
                      className="rounded text-blue-600 focus:ring-blue-400"
                    />
                    Requires Oxygen
                  </label>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1">Special Instructions / Companion Notes</label>
                  <textarea
                    rows={2}
                    value={specialInstructions}
                    onChange={(e) => setSpecialInstructions(e.target.value)}
                    placeholder="Any specific requests or companion requirements"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: REVIEW & BOOK */}
          {step === 3 && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
                <CheckCircle size={18} className="text-green-500" /> Review and Confirm Booking
              </h3>

              <div className="border border-gray-150 rounded-xl overflow-hidden text-sm bg-gray-50/30">
                <div className="px-4 py-3 bg-gray-100 border-b border-gray-200 font-semibold text-gray-700 text-xs uppercase tracking-wider">
                  Summary Details
                </div>
                <div className="p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Patient</span>
                    <span className="font-semibold text-gray-800">
                      {activePatient ? `${activePatient.first_name} ${activePatient.last_name}` : '—'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Care Service</span>
                    <span className="font-semibold text-gray-800">
                      {selectedService ? selectedService.service_name : '—'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Service Category</span>
                    <span className="font-semibold text-gray-800 capitalize">
                      {bookingType.toLowerCase()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Schedule</span>
                    <span className="font-semibold text-gray-800">
                      {startDate} at {startTime} ({hours} hours)
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Pickup Address</span>
                    <span className="font-semibold text-gray-800 text-right max-w-xs truncate">
                      {pickupAddress}
                    </span>
                  </div>
                  {hospitalName && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Hospital</span>
                      <span className="font-semibold text-gray-800">
                        {hospitalName}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-500">Logistics Needs</span>
                    <span className="font-semibold text-gray-800">
                      {[requiresWheelchair && 'Wheelchair', requiresOxygen && 'Oxygen'].filter(Boolean).join(', ') || 'Standard'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Price estimation display */}
              <div className="bg-blue-50 border border-blue-150 p-4 rounded-xl">
                {priceLoading ? (
                  <p className="text-xs text-blue-600">Calculating final invoice...</p>
                ) : estimatedPrice ? (
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold text-blue-600">Estimated Total Quote</span>
                      <span className="text-xl font-bold text-blue-700">₹{estimatedPrice.total?.toFixed(2) || estimatedPrice.total_price}</span>
                    </div>
                    {estimatedPrice.gst && (
                      <div className="text-[10px] text-gray-500 flex justify-between">
                        <span>Includes GST (18%)</span>
                        <span>₹{estimatedPrice.gst.toFixed(2)}</span>
                      </div>
                    )}
                    {estimatedPrice.emergency_surcharge > 0 && (
                      <div className="text-[10px] text-red-500 flex justify-between font-medium">
                        <span>Emergency Surcharge Included</span>
                        <span>+₹{estimatedPrice.emergency_surcharge.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>Pricing details</span>
                    <span>₹{selectedService ? parseFloat(selectedService.base_price).toFixed(0) : '—'} (Base)</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Buttons Footer */}
          <div className="mt-8 flex justify-between items-center pt-4 border-t border-gray-150">
            <button
              type="button"
              onClick={handleBack}
              disabled={step === 0}
              className="flex items-center gap-1 px-4 py-2 border border-gray-300 text-sm font-semibold rounded-xl text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition-colors"
            >
              Back
            </button>

            {step < STEPS.length - 1 ? (
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-1 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-sm font-semibold rounded-xl text-white transition-colors"
              >
                Next <ArrowRight size={16} />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={bookingLoading}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-sm font-semibold rounded-xl text-white transition-colors"
              >
                {bookingLoading ? 'Booking...' : 'Confirm & Request Booking'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
