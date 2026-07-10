import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Activity, Copy, KeyRound, Plus, Shield, ToggleLeft, ToggleRight } from 'lucide-react'
import {
  addAPIKey,
  addRateLimit,
  clearCreatedSecret,
  fetchAPIKeys,
  fetchAuditLogs,
  fetchGatewayStatistics,
  fetchRateLimits,
  revokeKey,
  toggleRateLimit,
} from '../../redux/slices/gatewaySlice'

const dateTime = (value) => value
  ? new Date(value).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
  : 'Never'

export default function APIGatewayPage() {
  const dispatch = useDispatch()
  const { keys, rateLimits, auditLogs, statistics, createdSecret, loading, error } =
    useSelector((state) => state.gateway)
  const user = useSelector((state) => state.auth.user)
  const [tab, setTab] = useState('keys')
  const [keyForm, setKeyForm] = useState({
    name: '', scopes: ['read'], rate_limit_per_minute: 60,
  })
  const [limitForm, setLimitForm] = useState({
    name: '', path_pattern: '/api/v1/', methods: [], requests_per_minute: 60,
  })
  const isAdmin = !user || user.is_staff || user.role?.toUpperCase() === 'ADMIN'

  useEffect(() => {
    if (!isAdmin) return
    dispatch(fetchAPIKeys())
    dispatch(fetchRateLimits())
    dispatch(fetchAuditLogs())
    dispatch(fetchGatewayStatistics())
  }, [dispatch, isAdmin])

  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-lg p-8 text-center">
        <Shield size={44} className="mx-auto mb-3 text-gray-300" />
        <h1 className="text-xl font-bold">Admin access required</h1>
        <p className="mt-2 text-sm text-gray-500">Gateway controls are restricted to administrators.</p>
      </div>
    )
  }

  const createKey = async (event) => {
    event.preventDefault()
    const result = await dispatch(addAPIKey(keyForm))
    if (addAPIKey.fulfilled.match(result)) {
      setKeyForm({ name: '', scopes: ['read'], rate_limit_per_minute: 60 })
    }
  }

  const createLimit = async (event) => {
    event.preventDefault()
    const result = await dispatch(addRateLimit(limitForm))
    if (addRateLimit.fulfilled.match(result)) {
      setLimitForm({
        name: '', path_pattern: '/api/v1/', methods: [], requests_per_minute: 60,
      })
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-5 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">API Gateway</h1>
        <p className="text-sm text-gray-500">Manage machine credentials, traffic policies, and audit logs.</p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border bg-white p-4">
          <KeyRound size={18} className="text-blue-600" />
          <p className="mt-2 text-2xl font-bold">{keys.filter((key) => key.status === 'active').length}</p>
          <p className="text-xs text-gray-500">Active keys</p>
        </div>
        <div className="rounded-xl border bg-white p-4">
          <Activity size={18} className="text-purple-600" />
          <p className="mt-2 text-2xl font-bold">{statistics?.total_requests || 0}</p>
          <p className="text-xs text-gray-500">Audited requests</p>
        </div>
        <div className="rounded-xl border bg-white p-4">
          <Shield size={18} className="text-red-500" />
          <p className="mt-2 text-2xl font-bold">{statistics?.error_requests || 0}</p>
          <p className="text-xs text-gray-500">Error responses</p>
        </div>
      </div>

      <div className="flex gap-1 border-b">
        {[
          ['keys', 'API Keys'],
          ['limits', 'Rate Limits'],
          ['audit', 'Audit Log'],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`border-b-2 px-4 py-2 text-sm font-medium ${
              tab === key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      {createdSecret && (
        <div className="rounded-xl border border-amber-300 bg-amber-50 p-4">
          <p className="font-semibold text-amber-900">Copy this key now — it will not be shown again.</p>
          <div className="mt-2 flex items-center gap-2">
            <code className="min-w-0 flex-1 overflow-auto rounded bg-white p-2 text-sm">{createdSecret}</code>
            <button
              onClick={() => navigator.clipboard.writeText(createdSecret)}
              className="rounded-lg border bg-white p-2 text-amber-800"
              title="Copy key"
            >
              <Copy size={17} />
            </button>
            <button
              onClick={() => dispatch(clearCreatedSecret())}
              className="text-sm text-amber-800 underline"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {tab === 'keys' && (
        <div className="grid gap-5 lg:grid-cols-3">
          <form onSubmit={createKey} className="h-fit space-y-3 rounded-xl border bg-white p-4">
            <h2 className="font-semibold">Create API key</h2>
            <input
              required
              placeholder="Integration name"
              value={keyForm.name}
              onChange={(e) => setKeyForm({ ...keyForm, name: e.target.value })}
              className="w-full rounded-lg border px-3 py-2 text-sm"
            />
            <select
              value={keyForm.scopes[0]}
              onChange={(e) => setKeyForm({ ...keyForm, scopes: [e.target.value] })}
              className="w-full rounded-lg border px-3 py-2 text-sm"
            >
              <option value="read">Read</option>
              <option value="write">Write</option>
              <option value="admin">Admin</option>
            </select>
            <input
              type="number"
              min="1"
              max="10000"
              value={keyForm.rate_limit_per_minute}
              onChange={(e) => setKeyForm({
                ...keyForm, rate_limit_per_minute: Number(e.target.value),
              })}
              className="w-full rounded-lg border px-3 py-2 text-sm"
            />
            <button disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-2 text-sm font-medium text-white disabled:opacity-50">
              <Plus size={15} /> Create key
            </button>
          </form>

          <div className="space-y-3 lg:col-span-2">
            {keys.map((apiKey) => (
              <div key={apiKey.id} className="rounded-xl border bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">{apiKey.name}</p>
                    <code className="text-xs text-gray-500">{apiKey.prefix}••••••••</code>
                    <p className="mt-2 text-xs text-gray-400">
                      {apiKey.rate_limit_per_minute}/min · Last used {dateTime(apiKey.last_used_at)}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                      apiKey.status === 'active'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-500'
                    }`}>{apiKey.status}</span>
                    {apiKey.status === 'active' && (
                      <button
                        onClick={() => dispatch(revokeKey(apiKey.id))}
                        className="mt-3 block text-xs text-red-600 hover:underline"
                      >
                        Revoke
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'limits' && (
        <div className="grid gap-5 lg:grid-cols-3">
          <form onSubmit={createLimit} className="h-fit space-y-3 rounded-xl border bg-white p-4">
            <h2 className="font-semibold">New traffic policy</h2>
            <input
              required
              placeholder="Policy name"
              value={limitForm.name}
              onChange={(e) => setLimitForm({ ...limitForm, name: e.target.value })}
              className="w-full rounded-lg border px-3 py-2 text-sm"
            />
            <input
              required
              placeholder="/api/v1/"
              value={limitForm.path_pattern}
              onChange={(e) => setLimitForm({ ...limitForm, path_pattern: e.target.value })}
              className="w-full rounded-lg border px-3 py-2 text-sm"
            />
            <input
              type="number"
              min="1"
              value={limitForm.requests_per_minute}
              onChange={(e) => setLimitForm({
                ...limitForm, requests_per_minute: Number(e.target.value),
              })}
              className="w-full rounded-lg border px-3 py-2 text-sm"
            />
            <button disabled={loading} className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white disabled:opacity-50">
              Create policy
            </button>
          </form>
          <div className="space-y-3 lg:col-span-2">
            {rateLimits.map((policy) => (
              <div key={policy.id} className="flex items-center justify-between rounded-xl border bg-white p-4">
                <div>
                  <p className="font-semibold">{policy.name}</p>
                  <code className="text-xs text-gray-500">{policy.path_pattern}</code>
                  <p className="mt-1 text-xs text-gray-400">{policy.requests_per_minute} requests/minute</p>
                </div>
                <button
                  onClick={() => dispatch(toggleRateLimit({
                    id: policy.id, is_active: !policy.is_active,
                  }))}
                  className={policy.is_active ? 'text-green-600' : 'text-gray-400'}
                  title={policy.is_active ? 'Disable policy' : 'Enable policy'}
                >
                  {policy.is_active ? <ToggleRight size={30} /> : <ToggleLeft size={30} />}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'audit' && (
        <div className="overflow-x-auto rounded-xl border bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-3 py-2">Time</th>
                <th className="px-3 py-2">Method</th>
                <th className="px-3 py-2">Path</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td className="whitespace-nowrap px-3 py-2 text-xs text-gray-500">{dateTime(log.created_at)}</td>
                  <td className="px-3 py-2 font-medium">{log.method}</td>
                  <td className="max-w-md truncate px-3 py-2 font-mono text-xs">{log.path}</td>
                  <td className={`px-3 py-2 font-medium ${log.status_code >= 400 ? 'text-red-600' : 'text-green-600'}`}>
                    {log.status_code}
                  </td>
                  <td className="px-3 py-2 text-gray-500">{log.duration_ms} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!auditLogs.length && <p className="p-12 text-center text-gray-400">No API requests audited yet.</p>}
        </div>
      )}
    </div>
  )
}
