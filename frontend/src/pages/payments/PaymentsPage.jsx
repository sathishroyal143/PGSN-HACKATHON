import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { CreditCard, Wallet } from 'lucide-react'
import { fetchPayments, fetchWallet } from '../../redux/slices/paymentsSlice'

const STATUS_COLORS = {
  success: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  failed: 'bg-red-100 text-red-700',
  refunded: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-gray-100 text-gray-500',
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}

export default function PaymentsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { payments, wallet, loading, error } = useSelector((s) => s.payments)

  useEffect(() => {
    dispatch(fetchPayments())
    dispatch(fetchWallet())
  }, [dispatch])

  if (loading && !payments.length) return <div className="p-6 text-center text-gray-500">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Payments</h1>

      {/* Wallet card */}
      {wallet && (
        <div
          className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl p-4 text-white flex items-center justify-between cursor-pointer"
          onClick={() => navigate('/payments/invoices')}
        >
          <div>
            <p className="text-xs opacity-80">Wallet Balance</p>
            <p className="text-2xl font-bold mt-0.5">₹{parseFloat(wallet.balance).toFixed(2)}</p>
          </div>
          <Wallet size={32} className="opacity-70" />
        </div>
      )}

      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>}

      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-700">Transaction History</p>
        <button onClick={() => navigate('/payments/invoices')} className="text-xs text-blue-600 hover:underline">
          View Invoices →
        </button>
      </div>

      {payments.length === 0 && !loading ? (
        <div className="text-center py-16 text-gray-400">
          <CreditCard size={40} className="mx-auto mb-3 opacity-40" />
          <p>No payments yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {payments.map((p) => (
            <div key={p.id} className="bg-white border border-gray-200 rounded-lg p-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">₹{parseFloat(p.amount).toFixed(2)}</p>
                <p className="text-xs text-gray-400 mt-0.5">{fmt(p.paid_at || p.created_at)} · {p.method || 'N/A'}</p>
              </div>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${STATUS_COLORS[p.status] || STATUS_COLORS.pending}`}>
                {p.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
