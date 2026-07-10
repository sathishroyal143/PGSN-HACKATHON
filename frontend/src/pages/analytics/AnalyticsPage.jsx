import { useEffect, useMemo, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  Activity, BarChart3, CalendarDays, IndianRupee,
  Lightbulb, RefreshCw, Users,
} from 'lucide-react'
import {
  fetchAnalyticsDashboard,
  fetchInsights,
  fetchReports,
  generateReport,
  regenerateInsights,
} from '../../redux/slices/analyticsSlice'

const today = new Date().toISOString().slice(0, 10)
const thirtyDaysAgo = new Date(Date.now() - 29 * 86400000).toISOString().slice(0, 10)

const money = (value) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', maximumFractionDigits: 0,
  }).format(Number(value || 0))

const dateLabel = (value) =>
  value ? new Date(value).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  }) : '—'

const severityStyle = {
  info: 'border-blue-200 bg-blue-50 text-blue-800',
  warning: 'border-amber-200 bg-amber-50 text-amber-800',
  critical: 'border-red-200 bg-red-50 text-red-800',
}

function StatCard({ icon: Icon, label, value, tone = 'text-blue-600' }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
        <Icon size={18} className={tone} />
      </div>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )
}

function TrendChart({ trend }) {
  const visible = trend?.slice(-14) || []
  const max = Math.max(...visible.map((item) => item.bookings), 1)
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <h2 className="text-sm font-semibold text-gray-800">Bookings — last 14 days</h2>
      <div className="mt-4 flex h-44 items-end gap-2">
        {visible.map((item) => (
          <div key={item.date} className="group flex min-w-0 flex-1 flex-col items-center">
            <span className="mb-1 text-[10px] text-gray-500 opacity-0 group-hover:opacity-100">
              {item.bookings}
            </span>
            <div
              className="w-full min-h-1 rounded-t bg-blue-500 transition-colors group-hover:bg-blue-700"
              style={{ height: `${Math.max(item.bookings * 100 / max, 3)}%` }}
              title={`${dateLabel(item.date)}: ${item.bookings} bookings`}
            />
            <span className="mt-1 hidden text-[9px] text-gray-400 sm:block">
              {new Date(item.date).getDate()}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function AnalyticsPage() {
  const dispatch = useDispatch()
  const {
    dashboard, reports, insights, loading,
    reportLoading, insightLoading, error,
  } = useSelector((state) => state.analytics)
  const user = useSelector((state) => state.auth.user)
  const [tab, setTab] = useState('overview')
  const [range, setRange] = useState({ date_from: thirtyDaysAgo, date_to: today })
  const [reportForm, setReportForm] = useState({
    title: 'Monthly bookings report',
    report_type: 'bookings',
    date_from: thirtyDaysAgo,
    date_to: today,
  })

  const isAdmin = !user || user.is_staff || user.role?.toUpperCase() === 'ADMIN'

  useEffect(() => {
    if (!isAdmin) return
    dispatch(fetchAnalyticsDashboard(range))
    dispatch(fetchReports())
    dispatch(fetchInsights())
  }, [dispatch, isAdmin])

  const maxStatus = useMemo(
    () => Math.max(...(dashboard?.booking_statuses || []).map((item) => item.count), 1),
    [dashboard],
  )

  const applyRange = (event) => {
    event.preventDefault()
    dispatch(fetchAnalyticsDashboard(range))
  }

  const submitReport = async (event) => {
    event.preventDefault()
    const result = await dispatch(generateReport(reportForm))
    if (generateReport.fulfilled.match(result)) setTab('reports')
  }

  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-lg p-6 text-center">
        <BarChart3 size={42} className="mx-auto mb-3 text-gray-300" />
        <h1 className="text-xl font-bold text-gray-900">Admin access required</h1>
        <p className="mt-2 text-sm text-gray-500">
          Analytics contains platform-wide operational and financial information.
        </p>
      </div>
    )
  }

  const totals = dashboard?.totals

  return (
    <div className="mx-auto max-w-6xl space-y-5 p-4 sm:p-6">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Platform Analytics</h1>
          <p className="text-sm text-gray-500">Operational health, revenue, and reports.</p>
        </div>
        <form onSubmit={applyRange} className="flex flex-wrap items-center gap-2">
          <input
            type="date"
            value={range.date_from}
            max={range.date_to}
            onChange={(e) => setRange({ ...range, date_from: e.target.value })}
            className="rounded-lg border border-gray-300 px-2 py-1.5 text-sm"
          />
          <span className="text-gray-400">to</span>
          <input
            type="date"
            value={range.date_to}
            min={range.date_from}
            onChange={(e) => setRange({ ...range, date_to: e.target.value })}
            className="rounded-lg border border-gray-300 px-2 py-1.5 text-sm"
          />
          <button className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700">
            Apply
          </button>
        </form>
      </div>

      <div className="flex gap-1 border-b border-gray-200">
        {[
          ['overview', 'Overview'],
          ['reports', `Reports (${reports.length})`],
          ['insights', `Insights (${insights.length})`],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`border-b-2 px-4 py-2 text-sm font-medium ${
              tab === key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {tab === 'overview' && (
        loading && !dashboard ? (
          <p className="py-16 text-center text-gray-400">Loading analytics…</p>
        ) : (
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <StatCard icon={Users} label="New users" value={totals?.new_users || 0} />
              <StatCard icon={CalendarDays} label="Bookings" value={totals?.bookings || 0} tone="text-purple-600" />
              <StatCard icon={Activity} label="Completion" value={`${totals?.completion_rate || 0}%`} tone="text-emerald-600" />
              <StatCard icon={IndianRupee} label="Revenue" value={money(totals?.revenue)} tone="text-green-600" />
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2"><TrendChart trend={dashboard?.trend} /></div>
              <div className="rounded-xl border border-gray-200 bg-white p-4">
                <h2 className="text-sm font-semibold text-gray-800">Booking status</h2>
                <div className="mt-4 space-y-3">
                  {(dashboard?.booking_statuses || []).map((item) => (
                    <div key={item.status}>
                      <div className="mb-1 flex justify-between text-xs">
                        <span className="capitalize text-gray-600">
                          {item.status.toLowerCase().replaceAll('_', ' ')}
                        </span>
                        <span className="font-medium">{item.count}</span>
                      </div>
                      <div className="h-2 rounded bg-gray-100">
                        <div
                          className="h-2 rounded bg-purple-500"
                          style={{ width: `${item.count * 100 / maxStatus}%` }}
                        />
                      </div>
                    </div>
                  ))}
                  {!dashboard?.booking_statuses?.length && (
                    <p className="py-10 text-center text-sm text-gray-400">No bookings in this range.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )
      )}

      {tab === 'reports' && (
        <div className="grid gap-5 lg:grid-cols-3">
          <form onSubmit={submitReport} className="h-fit space-y-3 rounded-xl border border-gray-200 bg-white p-4">
            <h2 className="font-semibold text-gray-900">Generate report</h2>
            <input
              required
              value={reportForm.title}
              onChange={(e) => setReportForm({ ...reportForm, title: e.target.value })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              placeholder="Report title"
            />
            <select
              value={reportForm.report_type}
              onChange={(e) => setReportForm({ ...reportForm, report_type: e.target.value })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="bookings">Bookings</option>
              <option value="revenue">Revenue</option>
              <option value="user_growth">User growth</option>
              <option value="companion_performance">Companion performance</option>
            </select>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="date"
                required
                value={reportForm.date_from}
                onChange={(e) => setReportForm({ ...reportForm, date_from: e.target.value })}
                className="rounded-lg border border-gray-300 px-2 py-2 text-sm"
              />
              <input
                type="date"
                required
                value={reportForm.date_to}
                onChange={(e) => setReportForm({ ...reportForm, date_to: e.target.value })}
                className="rounded-lg border border-gray-300 px-2 py-2 text-sm"
              />
            </div>
            <button
              disabled={reportLoading}
              className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {reportLoading ? 'Generating…' : 'Generate report'}
            </button>
          </form>

          <div className="space-y-3 lg:col-span-2">
            {reports.map((report) => (
              <details key={report.id} className="rounded-xl border border-gray-200 bg-white p-4">
                <summary className="cursor-pointer list-none">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-gray-900">{report.title}</p>
                      <p className="mt-1 text-xs text-gray-400">
                        {dateLabel(report.date_from)} – {dateLabel(report.date_to)}
                      </p>
                    </div>
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                      report.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : report.status === 'failed'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-amber-100 text-amber-700'
                    }`}>
                      {report.status}
                    </span>
                  </div>
                </summary>
                <pre className="mt-3 overflow-auto rounded-lg bg-gray-900 p-3 text-xs text-gray-100">
                  {JSON.stringify(report.data, null, 2)}
                </pre>
              </details>
            ))}
            {!reports.length && !reportLoading && (
              <p className="py-16 text-center text-gray-400">No reports generated yet.</p>
            )}
          </div>
        </div>
      )}

      {tab === 'insights' && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <button
              onClick={() => dispatch(regenerateInsights(range))}
              disabled={insightLoading}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw size={15} className={insightLoading ? 'animate-spin' : ''} />
              Refresh insights
            </button>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {insights.map((insight) => (
              <div
                key={insight.id}
                className={`rounded-xl border p-4 ${severityStyle[insight.severity] || severityStyle.info}`}
              >
                <div className="flex items-start gap-3">
                  <Lightbulb size={19} className="mt-0.5 shrink-0" />
                  <div>
                    <p className="font-semibold">{insight.title}</p>
                    <p className="mt-1 text-sm opacity-90">{insight.description}</p>
                    <p className="mt-2 text-xs uppercase tracking-wide opacity-60">
                      {insight.category}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {!insights.length && !insightLoading && (
            <p className="py-16 text-center text-gray-400">
              No active insights. Generate a fresh analysis for this date range.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
