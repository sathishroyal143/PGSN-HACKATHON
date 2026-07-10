import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { FileText } from 'lucide-react'
import { fetchInvoices } from '../../redux/slices/paymentsSlice'

const STATUS_COLORS = {
  paid: 'bg-green-100 text-green-700',
  issued: 'bg-blue-100 text-blue-700',
  draft: 'bg-gray-100 text-gray-500',
  overdue: 'bg-red-100 text-red-700',
  cancelled: 'bg-gray-100 text-gray-400',
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}

export default function InvoicePage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { invoices, loading } = useSelector((s) => s.payments)

  useEffect(() => { dispatch(fetchInvoices()) }, [dispatch])

  if (loading && !invoices.length) return <div className="p-6 text-center text-gray-500">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Invoices</h1>
        <button onClick={() => navigate('/payments')} className="text-sm text-blue-600 hover:underline">← Payments</button>
      </div>

      {invoices.length === 0 && !loading ? (
        <div className="text-center py-16 text-gray-400">
          <FileText size={40} className="mx-auto mb-3 opacity-40" />
          <p>No invoices yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {invoices.map((inv) => (
            <div key={inv.id} className="bg-white border border-gray-200 rounded-lg p-4 space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-gray-900">{inv.invoice_number}</p>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${STATUS_COLORS[inv.status] || STATUS_COLORS.draft}`}>
                  {inv.status}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Issued: {fmt(inv.issued_at)}</span>
                <span className="font-semibold text-gray-800 text-sm">₹{parseFloat(inv.total_amount).toFixed(2)}</span>
              </div>
              <div className="text-xs text-gray-400 flex gap-4">
                <span>Subtotal: ₹{parseFloat(inv.subtotal).toFixed(2)}</span>
                <span>Tax: ₹{parseFloat(inv.tax_amount).toFixed(2)}</span>
                {parseFloat(inv.discount_amount) > 0 && <span>Discount: -₹{parseFloat(inv.discount_amount).toFixed(2)}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
