import { useEffect, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { ShieldCheck, Upload, FileText, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react'
import Tesseract from 'tesseract.js'
import { fetchDocuments, uploadDocument, fetchKYC } from '../../redux/slices/verificationSlice'

const MANDATORY_DOCS = [
  { value: 'aadhar', label: 'Aadhar Card' },
  { value: 'pan', label: 'PAN Card' },
  { value: 'driving_license', label: 'Driving License' },
]

const OTHER_DOCS = [
  { value: 'passport', label: 'Passport' },
  { value: 'voter_id', label: 'Voter ID' },
  { value: 'police_clearance', label: 'Police Clearance' },
  { value: 'medical_cert', label: 'Medical Certificate' },
  { value: 'training_cert', label: 'Training Certificate' },
  { value: 'other', label: 'Other' },
]

const DOC_TYPES = [...MANDATORY_DOCS, ...OTHER_DOCS]

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-700',
  under_review: 'bg-blue-100 text-blue-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  expired: 'bg-gray-100 text-gray-500',
}

const STATUS_ICON = {
  approved: <CheckCircle size={14} className="text-green-600" />,
  rejected: <XCircle size={14} className="text-red-500" />,
  pending: <Clock size={14} className="text-yellow-500" />,
  under_review: <Clock size={14} className="text-blue-500" />,
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}

function DocumentUploadCard({ title, defaultDocType, isMandatory = false, isOther = false, existingDocs = [] }) {
  const dispatch = useDispatch()
  const fileRef = useRef()
  const [form, setForm] = useState({ doc_type: defaultDocType, document_number: '' })
  const [file, setFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const uploadedDoc = isOther ? null : existingDocs.find(d => d.doc_type === defaultDocType)

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) { setUploadError('Please select a file.'); return }

    if (form.doc_type !== 'other') {
      if (!file.type.startsWith('image/')) {
        setUploadError('For automatic verification, please upload an Image (JPG, PNG). PDFs are not supported for this check.')
        return
      }

      setUploadError('')
      setVerifying(true)
      try {
        const fileUrl = URL.createObjectURL(file)
        const result = await Tesseract.recognize(fileUrl, 'eng')
        const text = result.data.text.toLowerCase()
        URL.revokeObjectURL(fileUrl)

        const docTypeKeywords = {
          aadhar: ['aadhar', 'uidai', 'government of india'],
          pan: ['pan', 'income tax department', 'permanent account number', 'govt. of india'],
          driving_license: ['driving licence', 'driving license', 'dl', 'transport department', 'union of india'],
          passport: ['passport', 'republic of india'],
          voter_id: ['election commission', 'epic', 'voter', 'elector'],
          police_clearance: ['police clearance', 'pcc', 'clearance certificate', 'police'],
          medical_cert: ['medical certificate', 'fitness certificate', 'health certificate', 'medical'],
          training_cert: ['training certificate', 'certificate of completion', 'certified', 'training'],
        }

        const keywords = docTypeKeywords[form.doc_type] || []
        if (keywords.length > 0 && !keywords.some(k => text.includes(k.toLowerCase()))) {
          const docLabel = DOC_TYPES.find(d => d.value === form.doc_type)?.label || form.doc_type
          setUploadError(`Verification failed. The uploaded document does not appear to be a valid ${docLabel}.`)
          setVerifying(false)
          return
        }
      } catch (err) {
        setUploadError('Failed to process image for verification.')
        setVerifying(false)
        return
      }
      setVerifying(false)
    }

    setSubmitting(true)
    const fd = new FormData()
    fd.append('doc_type', form.doc_type)
    fd.append('file', file)
    if (form.document_number) fd.append('document_number', form.document_number)
    
    const result = await dispatch(uploadDocument(fd))
    setSubmitting(false)
    if (!result.error) {
      setFile(null)
      setForm({ doc_type: defaultDocType, document_number: '' })
      dispatch(fetchDocuments())
      dispatch(fetchKYC())
    } else {
      setUploadError(result.payload || 'Upload failed.')
    }
  }

  if (uploadedDoc && !isOther) {
    return (
      <div className="bg-white border border-green-200 rounded-xl p-4 space-y-2 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle size={18} className="text-green-600" />
            <h3 className="font-semibold text-gray-800">{title}</h3>
          </div>
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${STATUS_COLORS[uploadedDoc.status] || STATUS_COLORS.pending}`}>
            {uploadedDoc.status?.replace('_', ' ')}
          </span>
        </div>
        <p className="text-xs text-gray-500">Uploaded on {fmt(uploadedDoc.created_at)}</p>
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-3 shadow-sm">
      <div className="flex items-center gap-2">
        {isMandatory ? <AlertCircle size={18} className="text-red-500" /> : <FileText size={18} className="text-blue-500" />}
        <h3 className="font-semibold text-gray-800">{title} {isMandatory ? '' : <span className="text-gray-400 font-normal text-sm">(Optional)</span>}</h3>
      </div>
      <form onSubmit={handleUpload} className="space-y-3">
        {isOther && (
          <select
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={form.doc_type}
            onChange={(e) => setForm({ ...form, doc_type: e.target.value })}
          >
            {OTHER_DOCS.map((d) => <option key={d.value} value={d.value}>{d.label}</option>)}
          </select>
        )}
        <input
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          placeholder="Document number (optional)"
          value={form.document_number}
          onChange={(e) => setForm({ ...form, document_number: e.target.value })}
        />
        
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-blue-400 transition-colors"
        >
          {file ? (
            <p className="text-sm text-blue-600 font-medium">{file.name}</p>
          ) : (
            <p className="text-sm text-gray-400">Click to select file (JPG, PNG)</p>
          )}
          <input
            ref={fileRef}
            type="file"
            accept=".jpg,.jpeg,.png"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
        </div>
        {uploadError && <p className="text-xs text-red-600">{uploadError}</p>}
        <button
          type="submit"
          disabled={submitting || verifying || !file}
          className="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {verifying ? 'Verifying...' : submitting ? 'Uploading…' : 'Upload'}
        </button>
      </form>
    </div>
  )
}

export default function VerificationPage() {
  const dispatch = useDispatch()
  const { documents, error } = useSelector((s) => s.verification)

  useEffect(() => {
    dispatch(fetchDocuments())
    dispatch(fetchKYC())
  }, [dispatch])

  const otherUploadedDocs = documents.filter(doc => OTHER_DOCS.some(od => od.value === doc.doc_type))

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Document Verification</h1>

      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>}

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800 border-b pb-2">Mandatory Documents</h2>
        {MANDATORY_DOCS.map(doc => (
          <DocumentUploadCard 
            key={doc.value} 
            title={doc.label} 
            defaultDocType={doc.value} 
            existingDocs={documents} 
            isMandatory={true}
          />
        ))}
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800 border-b pb-2 mt-8">Other Documents (Optional)</h2>
        <DocumentUploadCard 
          title="Upload Additional Document" 
          defaultDocType="passport" 
          isOther={true} 
          existingDocs={documents} 
          isMandatory={false}
        />
        
        {otherUploadedDocs.length > 0 && (
          <div className="mt-4 space-y-2">
            <h3 className="text-sm font-semibold text-gray-700">Uploaded Additional Documents</h3>
            {otherUploadedDocs.map((doc) => (
              <div key={doc.id} className="bg-white border border-gray-200 rounded-lg p-3 space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {STATUS_ICON[doc.status] || <Clock size={14} className="text-gray-400" />}
                    <p className="text-sm font-medium text-gray-900 capitalize">
                      {DOC_TYPES.find((d) => d.value === doc.doc_type)?.label || doc.doc_type}
                    </p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${STATUS_COLORS[doc.status] || STATUS_COLORS.pending}`}>
                    {doc.status?.replace('_', ' ')}
                  </span>
                </div>
                {doc.document_number && (
                  <p className="text-xs text-gray-400">No: {doc.document_number}</p>
                )}
                <p className="text-xs text-gray-300">Uploaded {fmt(doc.created_at)}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
