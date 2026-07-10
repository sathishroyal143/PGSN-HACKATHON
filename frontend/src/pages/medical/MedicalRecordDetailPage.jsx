import { useEffect, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  fetchRecord, editRecord, clearCurrentRecord, clearError,
  fetchPrescriptions, addPrescription, removePrescription,
  fetchLabReports, addLabReport, removeLabReport,
  fetchDocuments, addDocument, removeDocument,
} from '../../redux/slices/medicalRecordsSlice'

function Field({ label, value }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value || '—'}</p>
    </div>
  )
}

// ── Overview Tab ──────────────────────────────────────────────────────────────
const RECORD_TYPES = [
  'CONSULTATION', 'LAB_REPORT', 'PRESCRIPTION',
  'IMAGING', 'DISCHARGE', 'VACCINATION', 'SURGERY', 'OTHER',
]

function OverviewTab({ record, patientId, loading, dispatch }) {
  const [editing, setEditing] = useState(false)
  const { register, handleSubmit, reset } = useForm({ defaultValues: record })

  useEffect(() => { reset(record) }, [record])

  const handleSave = async (data) => {
    const result = await dispatch(editRecord({ patientId, id: record.id, data }))
    if (editRecord.fulfilled.match(result)) {
      toast.success('Record updated!')
      setEditing(false)
    }
  }

  if (editing) {
    return (
      <form onSubmit={handleSubmit(handleSave)} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Record Type</label>
            <select {...register('record_type')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {RECORD_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Record Date</label>
            <input type="date" {...register('record_date')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-medium text-gray-600 mb-1">Title</label>
            <input {...register('title')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
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
          <div className="col-span-2">
            <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
            <textarea {...register('description')} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
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
    <div className="space-y-5">
      <div className="flex justify-end">
        <button onClick={() => setEditing(true)} className="text-sm text-blue-600 hover:underline">Edit</button>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Record Type" value={record.record_type} />
        <Field label="Record Date" value={record.record_date} />
        <Field label="Hospital" value={record.hospital_name} />
        <Field label="Doctor" value={record.doctor_name} />
        <Field label="Specialization" value={record.doctor_specialization} />
        <Field label="Follow-up Date" value={record.follow_up_date} />
      </div>
      {record.diagnosis && (
        <div>
          <p className="text-xs text-gray-500 mb-1">Diagnosis</p>
          <p className="text-sm text-gray-800 bg-gray-50 rounded-lg p-3">{record.diagnosis}</p>
        </div>
      )}
      {record.treatment_notes && (
        <div>
          <p className="text-xs text-gray-500 mb-1">Treatment Notes</p>
          <p className="text-sm text-gray-800 bg-gray-50 rounded-lg p-3">{record.treatment_notes}</p>
        </div>
      )}
      {record.description && (
        <div>
          <p className="text-xs text-gray-500 mb-1">Description</p>
          <p className="text-sm text-gray-800 bg-gray-50 rounded-lg p-3">{record.description}</p>
        </div>
      )}
      {record.ai_summary && (
        <div>
          <p className="text-xs text-gray-500 mb-1">AI Summary</p>
          <p className="text-sm text-gray-800 bg-blue-50 border border-blue-100 rounded-lg p-3">{record.ai_summary}</p>
        </div>
      )}
    </div>
  )
}

// ── Prescriptions Tab ─────────────────────────────────────────────────────────
const FREQUENCIES = ['ONCE_DAILY', 'TWICE_DAILY', 'THRICE_DAILY', 'FOUR_TIMES', 'AS_NEEDED', 'WEEKLY', 'OTHER']
const RX_STATUSES = ['ACTIVE', 'COMPLETED', 'CANCELLED']

function PrescriptionsTab({ recordId, prescriptions, loading, dispatch }) {
  const [showForm, setShowForm] = useState(false)
  const { register, handleSubmit, reset } = useForm()

  useEffect(() => { dispatch(fetchPrescriptions(recordId)) }, [recordId])

  const handleAdd = async (data) => {
    const result = await dispatch(addPrescription({ recordId, data }))
    if (addPrescription.fulfilled.match(result)) {
      toast.success('Prescription added!')
      reset()
      setShowForm(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this prescription?')) return
    const result = await dispatch(removePrescription({ recordId, id }))
    if (removePrescription.fulfilled.match(result)) toast.success('Prescription deleted.')
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">Prescriptions for this record</p>
        <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
          + Add Prescription
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit(handleAdd)} className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Medicine Name *</label>
              <input {...register('medicine_name', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Dosage *</label>
              <input {...register('dosage', { required: true })} placeholder="e.g. 500mg" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Frequency</label>
              <select {...register('frequency')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {FREQUENCIES.map((f) => <option key={f} value={f}>{f.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Duration (days)</label>
              <input type="number" {...register('duration_days')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Prescribed Date *</label>
              <input type="date" {...register('prescribed_date', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">End Date</label>
              <input type="date" {...register('end_date')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
              <select {...register('status')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {RX_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Instructions</label>
              <input {...register('instructions')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50">
              {loading ? 'Saving…' : 'Save'}
            </button>
            <button type="button" onClick={() => { setShowForm(false); reset() }} className="text-sm text-gray-600 px-4 py-2 rounded-lg border border-gray-300">Cancel</button>
          </div>
        </form>
      )}

      {!prescriptions || prescriptions.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">No prescriptions added yet.</p>
      ) : (
        <div className="space-y-2">
          {prescriptions.map((p) => (
            <div key={p.id} className="bg-white border border-gray-100 rounded-xl p-4 flex items-start justify-between">
              <div className="grid grid-cols-3 gap-x-6 gap-y-1 flex-1">
                <Field label="Medicine" value={p.medicine_name} />
                <Field label="Dosage" value={p.dosage} />
                <Field label="Frequency" value={p.frequency?.replace(/_/g, ' ')} />
                <Field label="Duration" value={p.duration_days ? `${p.duration_days} days` : null} />
                <Field label="Prescribed" value={p.prescribed_date} />
                <div>
                  <p className="text-xs text-gray-500">Status</p>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${p.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : p.status === 'CANCELLED' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'}`}>
                    {p.status}
                  </span>
                </div>
                {p.instructions && <Field label="Instructions" value={p.instructions} />}
              </div>
              <button onClick={() => handleDelete(p.id)} className="text-xs text-red-500 hover:underline ml-4 shrink-0">Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Lab Reports Tab ───────────────────────────────────────────────────────────
const LAB_STATUSES = ['PENDING', 'COMPLETED', 'ABNORMAL']

function LabReportsTab({ recordId, labReports, loading, dispatch }) {
  const [showForm, setShowForm] = useState(false)
  const { register, handleSubmit, reset } = useForm()

  useEffect(() => { dispatch(fetchLabReports(recordId)) }, [recordId])

  const handleAdd = async (data) => {
    const result = await dispatch(addLabReport({ recordId, data }))
    if (addLabReport.fulfilled.match(result)) {
      toast.success('Lab report added!')
      reset()
      setShowForm(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this lab report?')) return
    const result = await dispatch(removeLabReport({ recordId, id }))
    if (removeLabReport.fulfilled.match(result)) toast.success('Lab report deleted.')
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">Lab reports for this record</p>
        <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
          + Add Lab Report
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit(handleAdd)} className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Test Name *</label>
              <input {...register('test_name', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Lab Name</label>
              <input {...register('lab_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Test Date *</label>
              <input type="date" {...register('test_date', { required: true })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Result Value</label>
              <input {...register('result_value')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Reference Range</label>
              <input {...register('reference_range')} placeholder="e.g. 70–100" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Unit</label>
              <input {...register('unit')} placeholder="e.g. mg/dL" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
              <select {...register('status')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {LAB_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
              <input {...register('notes')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50">
              {loading ? 'Saving…' : 'Save'}
            </button>
            <button type="button" onClick={() => { setShowForm(false); reset() }} className="text-sm text-gray-600 px-4 py-2 rounded-lg border border-gray-300">Cancel</button>
          </div>
        </form>
      )}

      {!labReports || labReports.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">No lab reports added yet.</p>
      ) : (
        <div className="space-y-2">
          {labReports.map((r) => (
            <div key={r.id} className="bg-white border border-gray-100 rounded-xl p-4 flex items-start justify-between">
              <div className="grid grid-cols-3 gap-x-6 gap-y-1 flex-1">
                <Field label="Test" value={r.test_name} />
                <Field label="Lab" value={r.lab_name} />
                <Field label="Date" value={r.test_date} />
                <Field label="Result" value={r.result_value ? `${r.result_value} ${r.unit || ''}`.trim() : null} />
                <Field label="Reference" value={r.reference_range} />
                <div>
                  <p className="text-xs text-gray-500">Status</p>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${r.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : r.status === 'ABNORMAL' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {r.status}
                  </span>
                </div>
                {r.notes && <Field label="Notes" value={r.notes} />}
              </div>
              <button onClick={() => handleDelete(r.id)} className="text-xs text-red-500 hover:underline ml-4 shrink-0">Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Documents Tab ─────────────────────────────────────────────────────────────
function DocumentsTab({ recordId, documents, loading, dispatch }) {
  const fileRef = useRef()

  useEffect(() => { dispatch(fetchDocuments(recordId)) }, [recordId])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    const result = await dispatch(addDocument({ recordId, formData }))
    if (addDocument.fulfilled.match(result)) toast.success('Document uploaded!')
    e.target.value = ''
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this document?')) return
    const result = await dispatch(removeDocument({ recordId, id }))
    if (removeDocument.fulfilled.match(result)) toast.success('Document deleted.')
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">Attached documents (max 10, 20MB each)</p>
        <button
          onClick={() => fileRef.current?.click()}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {loading ? 'Uploading…' : '+ Upload Document'}
        </button>
        <input ref={fileRef} type="file" className="hidden" onChange={handleUpload} accept=".pdf,.jpg,.jpeg,.png,.gif,.webp" />
      </div>

      {!documents || documents.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">No documents uploaded yet.</p>
      ) : (
        <div className="space-y-2">
          {documents.map((d) => (
            <div key={d.id} className="bg-white border border-gray-100 rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${d.document_type === 'PDF' ? 'bg-red-100 text-red-700' : d.document_type === 'IMAGE' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>
                  {d.document_type === 'PDF' ? 'PDF' : d.document_type === 'IMAGE' ? 'IMG' : 'DOC'}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800">{d.original_filename}</p>
                  <p className="text-xs text-gray-400">{d.file_size_kb} KB · {d.uploaded_by || 'Unknown'} · {new Date(d.created_at).toLocaleDateString()}</p>
                </div>
              </div>
              <div className="flex gap-3">
                <a href={d.file} target="_blank" rel="noreferrer" className="text-xs text-blue-600 hover:underline">View</a>
                <button onClick={() => handleDelete(d.id)} className="text-xs text-red-500 hover:underline">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
const TABS = ['Overview', 'Prescriptions', 'Lab Reports', 'Documents']

export default function MedicalRecordDetailPage() {
  const { patientId, recordId } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { currentRecord, prescriptions, labReports, documents, loading, error } = useSelector((s) => s.medicalRecords)
  const [tab, setTab] = useState('Overview')

  useEffect(() => {
    dispatch(fetchRecord({ patientId, id: recordId }))
    return () => dispatch(clearCurrentRecord())
  }, [recordId, patientId, dispatch])

  useEffect(() => {
    if (error) { toast.error(error); dispatch(clearError()) }
  }, [error, dispatch])

  if (loading && !currentRecord) return <p className="p-6 text-gray-500">Loading…</p>
  if (!currentRecord) return <p className="p-6 text-gray-500">Record not found.</p>

  return (
    <div className="max-w-3xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate(`/patients/${patientId}/records`)} className="text-gray-400 hover:text-gray-700 text-sm">
          ← Back to Records
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-gray-900">{currentRecord.title}</h1>
          <p className="text-sm text-gray-500">{currentRecord.patient_name} · {currentRecord.record_date}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${tab === t ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'Overview' && (
        <OverviewTab record={currentRecord} patientId={patientId} loading={loading} dispatch={dispatch} />
      )}
      {tab === 'Prescriptions' && (
        <PrescriptionsTab recordId={recordId} prescriptions={prescriptions} loading={loading} dispatch={dispatch} />
      )}
      {tab === 'Lab Reports' && (
        <LabReportsTab recordId={recordId} labReports={labReports} loading={loading} dispatch={dispatch} />
      )}
      {tab === 'Documents' && (
        <DocumentsTab recordId={recordId} documents={documents} loading={loading} dispatch={dispatch} />
      )}
    </div>
  )
}
