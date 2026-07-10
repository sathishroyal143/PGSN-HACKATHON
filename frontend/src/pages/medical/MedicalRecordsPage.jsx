import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  fetchRecords, addRecord, removeRecord, fetchSummary, clearError,
} from '../../redux/slices/medicalRecordsSlice'
import { fetchPatient } from '../../redux/slices/patientSlice'

const RECORD_TYPES = [
  'CONSULTATION', 'LAB_REPORT', 'PRESCRIPTION',
  'IMAGING', 'DISCHARGE', 'VACCINATION', 'SURGERY', 'OTHER',
]

const TYPE_LABELS = {
  CONSULTATION: 'Consultation', LAB_REPORT: 'Lab Report', PRESCRIPTION: 'Prescription',
  IMAGING: 'Imaging', DISCHARGE: 'Discharge', VACCINATION: 'Vaccination',
  SURGERY: 'Surgery', OTHER: 'Other',
}

const TYPE_COLORS = {
  CONSULTATION: 'bg-blue-100 text-blue-700',
  LAB_REPORT: 'bg-purple-100 text-purple-700',
  PRESCRIPTION: 'bg-green-100 text-green-700',
  IMAGING: 'bg-yellow-100 text-yellow-700',
  DISCHARGE: 'bg-red-100 text-red-700',
  VACCINATION: 'bg-teal-100 text-teal-700',
  SURGERY: 'bg-orange-100 text-orange-700',
  OTHER: 'bg-gray-100 text-gray-600',
}

export default function MedicalRecordsPage() {
  const { patientId } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  
  const { records, summary, loading, error } = useSelector((s) => s.medicalRecords)
  const { current: patient } = useSelector((s) => s.patient)
  
  const [showForm, setShowForm] = useState(searchParams.get('action') === 'new')
  const [filterType, setFilterType] = useState('')
  const { register, handleSubmit, reset } = useForm()

  useEffect(() => {
    if (patientId) {
      dispatch(fetchPatient(patientId))
      dispatch(fetchRecords({ patientId, params: filterType ? { record_type: filterType } : {} }))
      dispatch(fetchSummary(patientId))
    }
  }, [patientId, filterType, dispatch])

  useEffect(() => {
    if (error) { toast.error(error); dispatch(clearError()) }
  }, [error, dispatch])

  const handleCreate = async (data) => {
    if (!patientId) return toast.error("Patient ID missing")
    const result = await dispatch(addRecord({ patientId, data }))
    if (addRecord.fulfilled.match(result)) {
      toast.success('Medical record created!')
      reset()
      setShowForm(false)
      searchParams.delete('action')
      setSearchParams(searchParams)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this medical record?')) return
    const result = await dispatch(removeRecord({ patientId, id }))
    if (removeRecord.fulfilled.match(result)) toast.success('Record deleted.')
  }

  if (!patientId) return <div className="p-6 text-center text-gray-500">No patient specified.</div>

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate(`/family/records`)} className="text-gray-400 hover:text-gray-700 text-sm">
          ← Hub
        </button>
        <button onClick={() => navigate(`/family/patients/${patientId}`)} className="text-gray-400 hover:text-gray-700 text-sm">
          ← Patient Profile
        </button>
        
        <h1 className="text-xl font-bold text-gray-900 flex-1 ml-2">
          {patient ? `${patient.first_name}'s Medical Records` : 'Medical Records'}
        </h1>
        <button
          onClick={() => {
            setShowForm(!showForm)
            if (showForm) {
              searchParams.delete('action')
              setSearchParams(searchParams)
            } else {
              setSearchParams({ action: 'new' })
            }
          }}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          {showForm ? 'Cancel' : '+ Add Record'}
        </button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-white border border-gray-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{summary.total_records}</p>
            <p className="text-xs text-gray-500 mt-1">Total Records</p>
          </div>
          <div className="bg-white border border-gray-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{summary.active_prescriptions}</p>
            <p className="text-xs text-gray-500 mt-1">Active Prescriptions</p>
          </div>
          <div className="bg-white border border-gray-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-gray-700">{summary.latest_record_date || '—'}</p>
            <p className="text-xs text-gray-500 mt-1">Latest Record</p>
          </div>
        </div>
      )}

      {/* Add Record Form */}
      {showForm && (
        <form onSubmit={handleSubmit(handleCreate)} className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3 mb-6">
          <h2 className="text-sm font-semibold text-gray-700">New Medical Record</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Record Type</label>
              <select {...register('record_type', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {RECORD_TYPES.map((t) => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Record Date *</label>
              <input type="date" {...register('record_date', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
              <input {...register('title', { required: true })} placeholder="e.g. Annual Checkup" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Hospital Name</label>
              <input {...register('hospital_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Doctor Name</label>
              <input {...register('doctor_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Specialization</label>
              <input {...register('doctor_specialization')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Follow-up Date</label>
              <input type="date" {...register('follow_up_date')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Diagnosis</label>
              <textarea {...register('diagnosis')} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Treatment Notes</label>
              <textarea {...register('treatment_notes')} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-50">
              {loading ? 'Saving…' : 'Save Record'}
            </button>
            <button type="button" onClick={() => { setShowForm(false); reset() }} className="text-sm text-gray-600 px-4 py-2 rounded-lg border border-gray-300">
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Filter */}
      <div className="flex gap-2 mb-4 flex-wrap">
        <button
          onClick={() => setFilterType('')}
          className={`text-xs px-3 py-1.5 rounded-full font-medium ${!filterType ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
        >
          All
        </button>
        {RECORD_TYPES.map((t) => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            className={`text-xs px-3 py-1.5 rounded-full font-medium ${filterType === t ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
          >
            {TYPE_LABELS[t]}
          </button>
        ))}
      </div>

      {/* Records List */}
      {loading && records.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-12">Loading…</p>
      ) : records.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-12">No medical records found.</p>
      ) : (
        <div className="space-y-2">
          {records.map((r) => (
            <div
              key={r.id}
              className="bg-white border border-gray-100 rounded-xl p-4 flex items-start justify-between hover:border-blue-200 transition-colors"
            >
              <div
                className="flex-1 cursor-pointer"
                onClick={() => navigate(`/patients/${patientId}/records/${r.id}`)}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${TYPE_COLORS[r.record_type]}`}>
                    {TYPE_LABELS[r.record_type]}
                  </span>
                  <span className="text-xs text-gray-400">{r.record_date}</span>
                </div>
                <p className="text-sm font-semibold text-gray-800">{r.title}</p>
                {r.hospital_name && <p className="text-xs text-gray-500 mt-0.5">{r.hospital_name}{r.doctor_name ? ` · Dr. ${r.doctor_name}` : ''}</p>}
              </div>
              <div className="flex gap-2 ml-4 shrink-0">
                <button
                  onClick={() => navigate(`/patients/${patientId}/records/${r.id}`)}
                  className="text-xs text-blue-600 hover:underline"
                >
                  View
                </button>
                <button
                  onClick={() => handleDelete(r.id)}
                  className="text-xs text-red-500 hover:underline"
                >
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
