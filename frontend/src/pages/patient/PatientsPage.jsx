import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  fetchPatients, createPatient, deletePatient, setPrimary, clearPatientError,
} from '../../redux/slices/patientSlice'

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'UNKNOWN']
const GENDERS = ['MALE', 'FEMALE', 'OTHER']
const MOBILITY = ['INDEPENDENT', 'ASSISTED', 'WHEELCHAIR', 'BEDRIDDEN']

function PatientForm({ onSave, onCancel, loading }) {
  const { register, handleSubmit, formState: { errors } } = useForm()
  return (
    <form onSubmit={handleSubmit(onSave)} className="bg-gray-50 border border-gray-200 rounded-xl p-5 space-y-4">
      <h3 className="font-semibold text-gray-800">New Patient</h3>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">First Name *</label>
          <input
            {...register('first_name', { required: 'Required' })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name.message}</p>}
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Last Name *</label>
          <input
            {...register('last_name', { required: 'Required' })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name.message}</p>}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Gender</label>
          <select {...register('gender')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select</option>
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
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Mobility Level</label>
          <select {...register('mobility_level')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            {MOBILITY.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Known Allergies</label>
          <input {...register('known_allergies')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Chronic Conditions</label>
        <input {...register('chronic_conditions')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="flex gap-4 pt-1">
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
      <div className="flex gap-2 pt-1">
        <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-50">
          {loading ? 'Saving…' : 'Add Patient'}
        </button>
        <button type="button" onClick={onCancel} className="text-sm text-gray-600 hover:text-gray-900 px-4 py-2 rounded-lg border border-gray-300">
          Cancel
        </button>
      </div>
    </form>
  )
}

const MOBILITY_BADGE = {
  INDEPENDENT: 'bg-green-100 text-green-700',
  ASSISTED: 'bg-yellow-100 text-yellow-700',
  WHEELCHAIR: 'bg-orange-100 text-orange-700',
  BEDRIDDEN: 'bg-red-100 text-red-700',
}

export default function PatientsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { list, loading, error } = useSelector((s) => s.patient)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => { dispatch(fetchPatients()) }, [dispatch])
  useEffect(() => {
    if (error) { toast.error(error); dispatch(clearPatientError()) }
  }, [error, dispatch])

  const handleCreate = async (data) => {
    const result = await dispatch(createPatient(data))
    if (createPatient.fulfilled.match(result)) {
      toast.success('Patient added!')
      setShowForm(false)
    }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete patient "${name}"?`)) return
    const result = await dispatch(deletePatient(id))
    if (deletePatient.fulfilled.match(result)) toast.success('Patient deleted.')
  }

  const handleSetPrimary = async (id) => {
    const result = await dispatch(setPrimary(id))
    if (setPrimary.fulfilled.match(result)) toast.success('Primary patient updated.')
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
          <p className="text-sm text-gray-500 mt-1">Manage patient profiles for your family</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          + Add Patient
        </button>
      </div>

      {showForm && (
        <div className="mb-6">
          <PatientForm onSave={handleCreate} onCancel={() => setShowForm(false)} loading={loading} />
        </div>
      )}

      {loading && list.length === 0 ? (
        <p className="text-gray-500 text-sm">Loading…</p>
      ) : list.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <p className="text-4xl mb-3">🏥</p>
          <p className="font-medium">No patients added yet.</p>
          <p className="text-sm mt-1">Add a patient to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map((p) => (
            <div key={p.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-center justify-between hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm">
                  {p.full_name?.[0] || '?'}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold text-gray-900">{p.full_name}</p>
                    {p.is_primary && (
                      <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">Primary</span>
                    )}
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${MOBILITY_BADGE[p.mobility_level] || 'bg-gray-100 text-gray-600'}`}>
                      {p.mobility_level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">
                    {p.blood_group} · {p.gender || 'Gender not set'} · {p.status}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {!p.is_primary && (
                  <button onClick={() => handleSetPrimary(p.id)} className="text-xs text-blue-600 hover:underline">
                    Set Primary
                  </button>
                )}
                <button
                  onClick={() => navigate(`/family/patients/${p.id}`)}
                  className="text-xs text-gray-600 hover:text-gray-900 border border-gray-200 px-3 py-1 rounded-lg"
                >
                  View
                </button>
                <button
                  onClick={() => navigate(`/family/patients/${p.id}/records`)}
                  className="text-xs text-blue-600 hover:text-blue-800 border border-blue-200 px-3 py-1 rounded-lg"
                >
                  Records
                </button>
                <button onClick={() => handleDelete(p.id, p.full_name)} className="text-xs text-red-500 hover:underline">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
