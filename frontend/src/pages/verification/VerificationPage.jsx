import { useEffect, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { ShieldCheck, Upload, FileText, CheckCircle, XCircle, Clock, AlertCircle, ShieldAlert, CheckCircle2, ChevronRight, UploadCloud } from 'lucide-react'
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
  pending: 'bg-amber-100 text-amber-800 border-amber-200',
  under_review: 'bg-blue-100 text-blue-800 border-blue-200',
  approved: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  rejected: 'bg-rose-100 text-rose-800 border-rose-200',
  expired: 'bg-gray-100 text-gray-600 border-gray-200',
}

const STATUS_ICON = {
  approved: <CheckCircle2 size={16} className="text-emerald-600" />,
  rejected: <XCircle size={16} className="text-rose-500" />,
  pending: <Clock size={16} className="text-amber-500" />,
  under_review: <Clock size={16} className="text-blue-500" />,
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
      <div className="bg-emerald-50/50 border border-emerald-200 rounded-3xl p-6 shadow-sm flex items-center justify-between group transition-all hover:bg-emerald-50">
        <div className="flex items-center gap-4">
          <div className="bg-emerald-100 p-3 rounded-2xl text-emerald-600">
            <CheckCircle2 size={24} />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-lg">{title}</h3>
            <p className="text-sm font-semibold text-gray-500 mt-0.5">Uploaded on {fmt(uploadedDoc.created_at)}</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider border ${STATUS_COLORS[uploadedDoc.status] || STATUS_COLORS.pending}`}>
          {uploadedDoc.status?.replace('_', ' ')}
        </span>
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-sm hover:shadow-md transition-all">
      <div className="flex items-center gap-3 mb-6">
        <div className={`p-3 rounded-2xl ${isMandatory ? 'bg-rose-50 text-rose-600' : 'bg-blue-50 text-blue-600'}`}>
          {isMandatory ? <ShieldAlert size={24} /> : <FileText size={24} />}
        </div>
        <div>
          <h3 className="font-bold text-gray-900 text-lg flex items-center gap-2">
            {title}
            {!isMandatory && <span className="text-xs font-bold bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full uppercase tracking-wide">Optional</span>}
          </h3>
          <p className="text-sm text-gray-500 font-medium">{isMandatory ? 'Required for verification' : 'Helps build trust with families'}</p>
        </div>
      </div>
      
      <form onSubmit={handleUpload} className="space-y-5">
        {isOther && (
          <select
            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
            value={form.doc_type}
            onChange={(e) => setForm({ ...form, doc_type: e.target.value })}
          >
            {OTHER_DOCS.map((d) => <option key={d.value} value={d.value}>{d.label}</option>)}
          </select>
        )}
        
        <input
          className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
          placeholder={`${title} number (optional)`}
          value={form.document_number}
          onChange={(e) => setForm({ ...form, document_number: e.target.value })}
        />
        
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/50 transition-all group"
        >
          {file ? (
            <div className="flex flex-col items-center gap-2">
              <div className="bg-primary-100 p-3 rounded-full text-primary-600">
                <CheckCircle2 size={24} />
              </div>
              <p className="text-sm font-bold text-gray-900">{file.name}</p>
              <p className="text-xs font-medium text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB • Click to replace</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div className="bg-gray-50 p-4 rounded-full text-gray-400 group-hover:text-primary-500 group-hover:bg-primary-100 transition-colors">
                <UploadCloud size={32} />
              </div>
              <p className="text-sm font-bold text-gray-700 mt-2">Click to select or drag and drop</p>
              <p className="text-xs font-medium text-gray-500">JPG, PNG (Max 5MB)</p>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept=".jpg,.jpeg,.png"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
        </div>
        
        {uploadError && (
          <div className="bg-rose-50 text-rose-700 p-3 rounded-xl text-sm font-medium flex items-start gap-2">
            <AlertCircle size={18} className="shrink-0 mt-0.5" />
            {uploadError}
          </div>
        )}
        
        <button
          type="submit"
          disabled={submitting || verifying || !file}
          className="w-full py-3.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 text-white rounded-xl font-bold transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:shadow-none"
        >
          {verifying ? 'Running AI Verification...' : submitting ? 'Uploading securely…' : 'Submit Document'}
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
    <div className="max-w-7xl mx-auto p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
      <div className="max-w-3xl mx-auto space-y-8">
        
        <div className="text-center space-y-4 mb-10">
          <div className="inline-flex items-center justify-center bg-primary-50 p-4 rounded-full mb-2">
            <ShieldCheck size={48} className="text-primary-600" />
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Identity Verification</h1>
          <p className="text-gray-500 font-medium text-lg max-w-xl mx-auto">
            Upload your documents to complete KYC. Verified companions receive 3x more care requests.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-center font-semibold">
            {error}
          </div>
        )}

        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="h-8 w-1 bg-primary-600 rounded-full" />
            <h2 className="text-xl font-bold text-gray-900">Mandatory Documents</h2>
          </div>
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

        <div className="space-y-6 pt-8">
          <div className="flex items-center gap-3">
            <div className="h-8 w-1 bg-gray-300 rounded-full" />
            <h2 className="text-xl font-bold text-gray-900">Additional Certifications</h2>
          </div>
          
          <DocumentUploadCard 
            title="Upload Additional Document" 
            defaultDocType="passport" 
            isOther={true} 
            existingDocs={documents} 
            isMandatory={false}
          />
          
          {otherUploadedDocs.length > 0 && (
            <div className="mt-8 space-y-4">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider px-2">Uploaded Additional Documents</h3>
              <div className="grid grid-cols-1 gap-4">
                {otherUploadedDocs.map((doc) => (
                  <div key={doc.id} className="bg-white border border-gray-200 rounded-2xl p-5 flex items-center justify-between hover:border-primary-300 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                        {STATUS_ICON[doc.status] || <Clock size={20} className="text-gray-400" />}
                      </div>
                      <div>
                        <p className="font-bold text-gray-900 capitalize">
                          {DOC_TYPES.find((d) => d.value === doc.doc_type)?.label || doc.doc_type}
                        </p>
                        {doc.document_number && (
                          <p className="text-xs font-semibold text-gray-500 mt-0.5">ID: {doc.document_number}</p>
                        )}
                        <p className="text-xs text-gray-400 font-medium mt-0.5">Uploaded {fmt(doc.created_at)}</p>
                      </div>
                    </div>
                    <span className={`text-xs font-bold px-3 py-1.5 rounded-full capitalize border ${STATUS_COLORS[doc.status] || STATUS_COLORS.pending}`}>
                      {doc.status?.replace('_', ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
      </div>
    </div>
  )
}
