import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  fetchCompanionMatches, fetchTrustScore,
  fetchPriority, fetchMedicalSummary,
  fetchAIHistory, clearResults,
} from '../../redux/slices/aiSlice'
import { fetchPatients } from '../../redux/slices/patientSlice'
import { fetchCompanions } from '../../redux/slices/companionsSlice'

const TABS = ['Companion Match', 'Trust Score', 'Priority', 'Medical Summary', 'History']

const PRIORITY_COLOR = {
  low:       'bg-green-100 text-green-800',
  medium:    'bg-yellow-100 text-yellow-800',
  high:      'bg-orange-100 text-orange-800',
  emergency: 'bg-red-100 text-red-800',
}

const STATUS_COLOR = {
  completed:  'bg-green-100 text-green-800',
  failed:     'bg-red-100 text-red-800',
  processing: 'bg-blue-100 text-blue-800',
  pending:    'bg-gray-100 text-gray-600',
}

export default function AIPage() {
  const dispatch = useDispatch()
  const { matches, trustScore, priority, medicalSummary, history, loading, error } = useSelector((s) => s.ai)
  const { list: patients } = useSelector((s) => s.patient)
  const { companions } = useSelector((s) => s.companions)
  const [tab, setTab] = useState(0)

  // Form states
  const [matchForm, setMatchForm]     = useState({ patient_id: '', required_skills: '', top_n: 10 })
  const [trustForm, setTrustForm]     = useState({ companion_id: '' })
  const [priorityForm, setPriorityForm] = useState({ patient_id: '', is_emergency: false })
  const [summaryForm, setSummaryForm] = useState({ patient_id: '' })

  useEffect(() => {
    dispatch(fetchPatients())
    dispatch(fetchCompanions())
  }, [dispatch])

  useEffect(() => {
    if (tab === 4) dispatch(fetchAIHistory())
  }, [tab, dispatch])

  const handleMatch = (e) => {
    e.preventDefault()
    dispatch(fetchCompanionMatches({
      patient_id: matchForm.patient_id,
      required_skills: matchForm.required_skills ? matchForm.required_skills.split(',').map(s => s.trim()) : [],
      top_n: Number(matchForm.top_n),
    }))
  }

  const handleTrust = (e) => {
    e.preventDefault()
    dispatch(fetchTrustScore({ companion_id: trustForm.companion_id }))
  }

  const handlePriority = (e) => {
    e.preventDefault()
    dispatch(fetchPriority({ patient_id: priorityForm.patient_id, is_emergency: priorityForm.is_emergency }))
  }

  const handleSummary = (e) => {
    e.preventDefault()
    dispatch(fetchMedicalSummary({ patient_id: summaryForm.patient_id }))
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">AI Engine</h1>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200 mb-6 overflow-x-auto">
        {TABS.map((t, i) => (
          <button
            key={t}
            onClick={() => { setTab(i); dispatch(clearResults()) }}
            className={`px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors
              ${tab === i ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            {t}
          </button>
        ))}
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {/* Tab 0 — Companion Match */}
      {tab === 0 && (
        <div className="space-y-5">
          <form onSubmit={handleMatch} className="bg-white border border-gray-200 rounded-lg p-5 space-y-3">
            <h2 className="font-semibold text-gray-800">Find Best Companions for a Patient</h2>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Patient</label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={matchForm.patient_id}
                onChange={e => setMatchForm(f => ({ ...f, patient_id: e.target.value }))}
                required
              >
                <option value="">Select a patient...</option>
                {patients.map(p => (
                  <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                ))}
              </select>
            </div>
            <Field label="Required Skills (comma-separated)" value={matchForm.required_skills}
              onChange={v => setMatchForm(f => ({ ...f, required_skills: v }))} placeholder="e.g. FIRST_AID, NURSING" />
            <Field label="Top N results" type="number" value={matchForm.top_n}
              onChange={v => setMatchForm(f => ({ ...f, top_n: v }))} />
            <SubmitBtn loading={loading} label="Find Matches" />
          </form>

          {matches.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-800">Results ({matches.length} companions)</h3>
              {matches.map((m) => (
                <div key={m.companion_id} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="font-semibold text-gray-900">#{m.rank} {m.companion_name}</span>
                    </div>
                    <span className="text-lg font-bold text-blue-600">{m.total_score}</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-gray-600">
                    <ScorePill label="Rating"       value={m.rating_score} />
                    <ScorePill label="Skills"       value={m.skills_score} />
                    <ScorePill label="Experience"   value={formatExperience(m.experience_years)} />
                    <ScorePill label="Trust"        value={m.trust_score} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 1 — Trust Score */}
      {tab === 1 && (
        <div className="space-y-5">
          <form onSubmit={handleTrust} className="bg-white border border-gray-200 rounded-lg p-5 space-y-3">
            <h2 className="font-semibold text-gray-800">Compute Companion Trust Score</h2>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Companion</label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={trustForm.companion_id}
                onChange={e => setTrustForm({ companion_id: e.target.value })}
                required
              >
                <option value="">Select a companion...</option>
                {companions?.map(c => (
                  <option key={c.id} value={c.id}>{c.full_name}</option>
                ))}
              </select>
            </div>
            <SubmitBtn loading={loading} label="Compute Score" />
          </form>

          {trustScore && (
            <div className="bg-white border border-gray-200 rounded-lg p-5 text-center">
              <p className="text-sm text-gray-500 mb-1">Trust Score</p>
              <p className="text-5xl font-bold text-blue-600">{trustScore.trust_score}</p>
              <p className="text-xs text-gray-400 mt-1">out of 100</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 2 — Priority */}
      {tab === 2 && (
        <div className="space-y-5">
          <form onSubmit={handlePriority} className="bg-white border border-gray-200 rounded-lg p-5 space-y-3">
            <h2 className="font-semibold text-gray-800">Assess Care Priority</h2>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Patient</label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={priorityForm.patient_id}
                onChange={e => setPriorityForm(f => ({ ...f, patient_id: e.target.value }))}
                required
              >
                <option value="">Select a patient...</option>
                {patients.map(p => (
                  <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                ))}
              </select>
            </div>
            <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
              <input type="checkbox" checked={priorityForm.is_emergency}
                onChange={e => setPriorityForm(f => ({ ...f, is_emergency: e.target.checked }))}
                className="rounded" />
              Emergency case
            </label>
            <SubmitBtn loading={loading} label="Assess Priority" />
          </form>

          {priority && (
            <div className="bg-white border border-gray-200 rounded-lg p-5 text-center">
              <p className="text-sm text-gray-500 mb-2">Priority Level</p>
              <span className={`px-4 py-2 rounded-full text-lg font-bold uppercase ${PRIORITY_COLOR[priority.priority_level] || 'bg-gray-100 text-gray-600'}`}>
                {priority.priority_level}
              </span>
              <p className="text-sm text-gray-500 mt-3">Score: <span className="font-semibold text-gray-800">{priority.priority_score}</span></p>
            </div>
          )}
        </div>
      )}

      {/* Tab 3 — Medical Summary */}
      {tab === 3 && (
        <div className="space-y-5">
          <form onSubmit={handleSummary} className="bg-white border border-gray-200 rounded-lg p-5 space-y-3">
            <h2 className="font-semibold text-gray-800">Generate Medical Summary</h2>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Patient Name</label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={summaryForm.patient_id || ''}
                onChange={e => setSummaryForm({ patient_id: e.target.value })}
                required
              >
                <option value="">Select a patient...</option>
                {patients.map(p => (
                  <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                ))}
              </select>
            </div>
            <SubmitBtn loading={loading} label="Generate Summary" />
          </form>

          {medicalSummary && (
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <h3 className="font-semibold text-gray-800 mb-3">Generated Summary</h3>
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed bg-gray-50 rounded p-3">
                {medicalSummary.summary}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Tab 4 — History */}
      {tab === 4 && (
        <div className="space-y-3">
          {loading && <p className="text-center text-gray-500 py-8">Loading…</p>}
          {!loading && history.length === 0 && (
            <p className="text-center text-gray-500 py-12">No AI requests yet.</p>
          )}
          {history.map((req) => (
            <div key={req.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-medium text-gray-900 capitalize">{req.request_type.replace(/_/g, ' ')}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{new Date(req.created_at).toLocaleString('en-IN')}</p>
                </div>
                <div className="flex items-center gap-2">
                  {req.processing_time_ms && (
                    <span className="text-xs text-gray-400">{req.processing_time_ms}ms</span>
                  )}
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOR[req.status] || 'bg-gray-100 text-gray-600'}`}>
                    {req.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function formatExperience(years) {
  if (!years) return '0 days'
  const y = Number(years)
  if (y < 1 / 12) return `${Math.round(y * 365.25)} days`
  if (y < 1) return `${Math.round(y * 12)} months`
  return `${y.toFixed(1).replace(/\.0$/, '')} years`
}

function Field({ label, value, onChange, type = 'text', required = false, placeholder = '' }) {
  return (
    <div>
      <label className="block text-sm text-gray-600 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        required={required}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  )
}

function SubmitBtn({ loading, label }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
    >
      {loading ? 'Processing…' : label}
    </button>
  )
}

function ScorePill({ label, value }) {
  return (
    <div className="bg-gray-50 rounded p-1.5 text-center">
      <p className="text-gray-400 text-xs">{label}</p>
      <p className="font-semibold text-gray-700">{value}</p>
    </div>
  )
}
