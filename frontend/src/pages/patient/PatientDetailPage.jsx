import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  fetchPatient, updatePatient, clearPatientError,
  fetchVitals, recordVital, deleteVital,
  fetchInsurance, addInsurance, updateInsurance, deleteInsurance,
} from '../../redux/slices/patientSlice'

// ── Shared ────────────────────────────────────────────────────────────────────
function Field({ label, value }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value || '—'}</p>
    </div>
  )
}

// ── Overview Tab ──────────────────────────────────────────────────────────────
const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'UNKNOWN']
const GENDERS = ['MALE', 'FEMALE', 'OTHER']
const MOBILITY = ['INDEPENDENT', 'ASSISTED', 'WHEELCHAIR', 'BEDRIDDEN']
const STATUSES = ['ACTIVE', 'INACTIVE', 'DECEASED']

function OverviewTab({ patient, loading, onSave }) {
  const [editing, setEditing] = useState(false)
  const { register, handleSubmit, reset } = useForm({ defaultValues: patient })

  useEffect(() => { reset(patient) }, [patient])

  const handleSave = async (data) => {
    await onSave(data)
    setEditing(false)
  }

  if (editing) {
    return (
      <form onSubmit={handleSubmit(handleSave)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">First Name</label>
            <input {...register('first_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Last Name</label>
            <input {...register('last_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Gender</label>
            <select {...register('gender')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {GENDERS.map((g) => <option key={g} value={g}>{g}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Blood Group</label>
            <select {...register('blood_group')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {BLOOD_GROUPS.map((b) => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Date of Birth</label>
            <input type="date" {...register('date_of_birth')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Mobility Level</label>
            <select {...register('mobility_level')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {MOBILITY.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
            <select {...register('status')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Known Allergies</label>
          <input {...register('known_allergies')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Chronic Conditions</label>
          <input {...register('chronic_conditions')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Current Medications</label>
          <input {...register('current_medications')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Special Needs</label>
          <input {...register('special_needs')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Emergency Notes</label>
          <textarea {...register('emergency_notes')} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="flex gap-3 pt-1">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" {...register('requires_wheelchair')} className="rounded" /> Wheelchair
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" {...register('requires_oxygen')} className="rounded" /> Oxygen
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" {...register('requires_stretcher')} className="rounded" /> Stretcher
          </label>
        </div>
        <div className="flex gap-2">
          <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-50">
            {loading ? 'Saving…' : 'Save Changes'}
          </button>
          <button type="button" onClick={() => setEditing(false)} className="text-sm text-gray-600 px-4 py-2 rounded-lg border border-gray-300">
            Cancel
          </button>
        </div>
      </form>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <button onClick={() => setEditing(true)} className="text-sm text-blue-600 hover:underline">Edit</button>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Blood Group" value={patient.blood_group} />
        <Field label="Gender" value={patient.gender} />
        <Field label="Date of Birth" value={patient.date_of_birth} />
        <Field label="Mobility Level" value={patient.mobility_level} />
        <Field label="Status" value={patient.status} />
        <Field label="BMI" value={patient.bmi} />
      </div>
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Wheelchair', val: patient.requires_wheelchair },
          { label: 'Oxygen', val: patient.requires_oxygen },
          { label: 'Stretcher', val: patient.requires_stretcher },
        ].map(({ label, val }) => (
          <div key={label} className={`rounded-lg p-3 text-center text-sm font-medium ${val ? 'bg-orange-50 text-orange-700' : 'bg-gray-50 text-gray-400'}`}>
            {label}: {val ? 'Yes' : 'No'}
          </div>
        ))}
      </div>
      <div className="space-y-3">
        <Field label="Known Allergies" value={patient.known_allergies} />
        <Field label="Chronic Conditions" value={patient.chronic_conditions} />
        <Field label="Current Medications" value={patient.current_medications} />
        <Field label="Special Needs" value={patient.special_needs} />
        <Field label="Dietary Restrictions" value={patient.dietary_restrictions} />
        <Field label="Emergency Notes" value={patient.emergency_notes} />
      </div>
    </div>
  )
}

// ── Vitals Tab ────────────────────────────────────────────────────────────────
function VitalsTab({ patientId, vitals, loading, dispatch }) {
  const [showForm, setShowForm] = useState(false)
  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  useEffect(() => { dispatch(fetchVitals(patientId)) }, [patientId])

  const handleRecord = async (data) => {
    // Convert empty strings to undefined so backend ignores them
    const cleaned = Object.fromEntries(
      Object.entries(data).filter(([, v]) => v !== '' && v !== null)
    )
    const result = await dispatch(recordVital({ patientId, data: cleaned }))
    if (recordVital.fulfilled.match(result)) {
      toast.success('Vital recorded!')
      reset()
      setShowForm(false)
    }
  }

  const handleDelete = async (vitalId) => {
    if (!window.confirm('Delete this vital record?')) return
    const result = await dispatch(deleteVital({ patientId, vitalId }))
    if (deleteVital.fulfilled.match(result)) toast.success('Vital deleted.')
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">Last 20 vital recordings</p>
        <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
          + Record Vital
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit(handleRecord)} className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
          <div className="grid grid-cols-3 gap-3">
            {[
              { name: 'heart_rate', label: 'Heart Rate (bpm)', type: 'number' },
              { name: 'blood_pressure_systolic', label: 'BP Systolic (mmHg)', type: 'number' },
              { name: 'blood_pressure_diastolic', label: 'BP Diastolic (mmHg)', type: 'number' },
              { name: 'oxygen_saturation', label: 'SpO2 (%)', type: 'number' },
              { name: 'temperature', label: 'Temp (°C)', type: 'number', step: '0.1' },
              { name: 'blood_glucose', label: 'Glucose (mg/dL)', type: 'number', step: '0.1' },
              { name: 'weight', label: 'Weight (kg)', type: 'number', step: '0.01' },
              { name: 'height', label: 'Height (cm)', type: 'number', step: '0.01' },
            ].map(({ name, label, type, step }) => (
              <div key={name}>
                <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                <input
                  type={type}
                  step={step || '1'}
                  {...register(name)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
            <input {...register('notes')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50">
              {loading ? 'Saving…' : 'Save'}
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="text-sm text-gray-600 px-4 py-2 rounded-lg border border-gray-300">Cancel</button>
          </div>
        </form>
      )}

      {!vitals || vitals.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">No vitals recorded yet.</p>
      ) : (
        <div className="space-y-2">
          {vitals.map((v) => (
            <div key={v.id} className="bg-white border border-gray-100 rounded-xl p-4 flex items-start justify-between">
              <div className="grid grid-cols-4 gap-x-6 gap-y-1 flex-1">
                {v.heart_rate && <Field label="Heart Rate" value={`${v.heart_rate} bpm`} />}
                {v.blood_pressure_systolic && <Field label="Blood Pressure" value={`${v.blood_pressure_systolic}/${v.blood_pressure_diastolic} mmHg`} />}
                {v.oxygen_saturation && <Field label="SpO2" value={`${v.oxygen_saturation}%`} />}
                {v.temperature && <Field label="Temp" value={`${v.temperature}°C`} />}
                {v.blood_glucose && <Field label="Glucose" value={`${v.blood_glucose} mg/dL`} />}
                {v.weight && <Field label="Weight" value={`${v.weight} kg`} />}
                {v.height && <Field label="Height" value={`${v.height} cm`} />}
                {v.bmi && <Field label="BMI" value={v.bmi} />}
                <Field label="Recorded" value={new Date(v.recorded_at).toLocaleString()} />
                {v.notes && <Field label="Notes" value={v.notes} />}
              </div>
              <button onClick={() => handleDelete(v.id)} className="text-xs text-red-500 hover:underline ml-4 shrink-0">Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Insurance Tab ─────────────────────────────────────────────────────────────
const INSURANCE_TYPES = ['GOVERNMENT', 'PRIVATE', 'CORPORATE', 'NONE']

function InsuranceTab({ patientId, records, loading, dispatch }) {
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const { register, handleSubmit, reset } = useForm()

  useEffect(() => { dispatch(fetchInsurance(patientId)) }, [patientId])
  useEffect(() => { reset(editing || {}) }, [editing])

  const handleAdd = async (data) => {
    const result = await dispatch(addInsurance({ patientId, data }))
    if (addInsurance.fulfilled.match(result)) {
      toast.success('Insurance added!')
      reset()
      setShowForm(false)
    }
  }

  const handleUpdate = async (data) => {
    const result = await dispatch(updateInsurance({ patientId, insuranceId: editing.id, data }))
    if (updateInsurance.fulfilled.match(result)) {
      toast.success('Insurance updated!')
      setEditing(null)
    }
  }

  const handleDeactivate = async (insuranceId) => {
    if (!window.confirm('Deactivate this insurance record?')) return
    const result = await dispatch(deleteInsurance({ patientId, insuranceId }))
    if (deleteInsurance.fulfilled.match(result)) toast.success('Insurance deactivated.')
  }

  const InsuranceForm = ({ onSubmit, onCancel }) => (
    <form onSubmit={handleSubmit(onSubmit)} className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Insurance Type</label>
          <select {...register('insurance_type')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            {INSURANCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Provider Name</label>
          <input {...register('provider_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Policy Number</label>
          <input {...register('policy_number')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Policy Holder Name</label>
          <input {...register('policy_holder_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Coverage Amount (₹)</label>
          <input type="number" {...register('coverage_amount')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Valid From</label>
          <input type="date" {...register('valid_from')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Valid Until</label>
          <input type="date" {...register('valid_until')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
        <input {...register('notes')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="flex gap-2">
        <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50">
          {loading ? 'Saving…' : 'Save'}
        </button>
        <button type="button" onClick={onCancel} className="text-sm text-gray-600 px-4 py-2 rounded-lg border border-gray-300">Cancel</button>
      </div>
    </form>
  )

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">Insurance records</p>
        {!showForm && !editing && (
          <button onClick={() => setShowForm(true)} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
            + Add Insurance
          </button>
        )}
      </div>

      {showForm && <InsuranceForm onSubmit={handleAdd} onCancel={() => setShowForm(false)} />}
      {editing && <InsuranceForm onSubmit={handleUpdate} onCancel={() => setEditing(null)} />}

      {!records || records.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">No insurance records found.</p>
      ) : (
        <div className="space-y-2">
          {records.map((r) => (
            <div key={r.id} className={`bg-white border rounded-xl p-4 flex items-start justify-between ${r.is_active ? 'border-green-200' : 'border-gray-100 opacity-60'}`}>
              <div className="grid grid-cols-3 gap-x-6 gap-y-1 flex-1">
                <Field label="Type" value={r.insurance_type} />
                <Field label="Provider" value={r.provider_name} />
                <Field label="Policy No." value={r.policy_number} />
                <Field label="Holder" value={r.policy_holder_name} />
                <Field label="Coverage" value={r.coverage_amount ? `₹${Number(r.coverage_amount).toLocaleString()}` : null} />
                <Field label="Valid" value={r.valid_from && r.valid_until ? `${r.valid_from} → ${r.valid_until}` : null} />
                <div>
                  <p className="text-xs text-gray-500">Status</p>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${r.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {r.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
              {r.is_active && (
                <div className="flex gap-2 ml-4 shrink-0">
                  <button onClick={() => { setEditing(r); setShowForm(false) }} className="text-xs text-blue-600 hover:underline">Edit</button>
                  <button onClick={() => handleDeactivate(r.id)} className="text-xs text-red-500 hover:underline">Deactivate</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
const TABS = ['Overview', 'Vitals', 'Insurance']

export default function PatientDetailPage() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { current, vitals, insurance, loading, error } = useSelector((s) => s.patient)
  const [tab, setTab] = useState('Overview')

  useEffect(() => { dispatch(fetchPatient(id)) }, [id, dispatch])
  useEffect(() => {
    if (error) { toast.error(error); dispatch(clearPatientError()) }
  }, [error, dispatch])

  const handleUpdate = async (data) => {
    const result = await dispatch(updatePatient({ id, data }))
    if (updatePatient.fulfilled.match(result)) toast.success('Patient updated.')
  }

  if (loading && !current) return <p className="p-6 text-gray-500">Loading…</p>
  if (!current) return <p className="p-6 text-gray-500">Patient not found.</p>

  return (
    <div className="max-w-3xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate('/family/patients')} className="text-gray-400 hover:text-gray-700 text-sm">← Back</button>
        <div className="flex-1 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">
              {current.full_name?.[0] || '?'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-gray-900">{current.full_name}</h1>
                {current.is_primary && (
                  <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">Primary</span>
                )}
              </div>
              <p className="text-sm text-gray-500">{current.blood_group} · {current.gender || 'Gender not set'}</p>
            </div>
          </div>
          <Link
            to={`/family/patients/${id}/records`}
            className="text-sm text-blue-600 hover:underline font-medium shrink-0"
          >
            Medical Records →
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'Overview' && (
        <OverviewTab patient={current} loading={loading} onSave={handleUpdate} />
      )}
      {tab === 'Vitals' && (
        <VitalsTab
          patientId={id}
          vitals={vitals[id]}
          loading={loading}
          dispatch={dispatch}
        />
      )}
      {tab === 'Insurance' && (
        <InsuranceTab
          patientId={id}
          records={insurance[id]}
          loading={loading}
          dispatch={dispatch}
        />
      )}
    </div>
  )
}
