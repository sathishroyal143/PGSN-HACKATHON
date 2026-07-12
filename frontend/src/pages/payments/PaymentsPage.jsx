import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { CreditCard, Wallet, ArrowUpRight, ArrowDownLeft } from 'lucide-react'
import { fetchWalletTransactions, fetchWallet, withdrawWallet } from '../../redux/slices/paymentsSlice'

const STATUS_COLORS = {
  success: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  failed: 'bg-red-100 text-red-700',
  refunded: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-gray-100 text-gray-500',
  credit: 'bg-green-100 text-green-700',
  debit: 'bg-red-100 text-red-700'
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}

export default function PaymentsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { walletTransactions, wallet, loading, error } = useSelector((s) => s.payments)

  const [isWithdrawModalOpen, setIsWithdrawModalOpen] = useState(false)
  const [withdrawAmount, setWithdrawAmount] = useState('')
  const [withdrawError, setWithdrawError] = useState(null)
  const [isWithdrawing, setIsWithdrawing] = useState(false)

  useEffect(() => {
    dispatch(fetchWalletTransactions())
    dispatch(fetchWallet())
  }, [dispatch])

  const handleWithdraw = async (e) => {
    e.preventDefault()
    setWithdrawError(null)
    const amount = parseFloat(withdrawAmount)
    if (!amount || amount <= 0) {
      setWithdrawError('Please enter a valid amount')
      return
    }
    setIsWithdrawing(true)
    try {
      await dispatch(withdrawWallet({ amount })).unwrap()
      setIsWithdrawModalOpen(false)
      setWithdrawAmount('')
      dispatch(fetchWalletTransactions()) // Refresh transactions
    } catch (err) {
      setWithdrawError(err || 'Failed to withdraw.')
    } finally {
      setIsWithdrawing(false)
    }
  }

  if (loading && !walletTransactions.length) return <div className="p-6 text-center text-gray-500">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Payments</h1>

      {/* Wallet card */}
      {wallet && (
        <div
          className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl p-4 text-white flex items-center justify-between"
        >
          <div>
            <p className="text-xs opacity-80">Wallet Balance</p>
            <p className="text-2xl font-bold mt-0.5">₹{parseFloat(wallet.balance).toFixed(2)}</p>
            <button 
              onClick={() => setIsWithdrawModalOpen(true)}
              className="mt-3 bg-white/20 hover:bg-white/30 transition text-sm font-medium px-4 py-1.5 rounded-full"
            >
              Withdraw Funds
            </button>
          </div>
          <Wallet size={32} className="opacity-70" />
        </div>
      )}

      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">{error}</div>}

      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-700">Transaction History</p>
      </div>

      {walletTransactions.length === 0 && !loading ? (
        <div className="text-center py-16 text-gray-400">
          <CreditCard size={40} className="mx-auto mb-3 opacity-40" />
          <p>No transactions yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {walletTransactions.map((txn) => (
            <div key={txn.id} className="bg-white border border-gray-200 rounded-lg p-3 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-full ${txn.txn_type === 'credit' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                  {txn.txn_type === 'credit' ? <ArrowDownLeft size={18} /> : <ArrowUpRight size={18} />}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {txn.txn_type === 'credit' ? '+' : '-'}₹{parseFloat(txn.amount).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">{fmt(txn.created_at)}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 truncate max-w-[120px] sm:max-w-[200px]" title={txn.description}>
                  {txn.description}
                </p>
                <span className={`inline-block mt-1 text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${STATUS_COLORS[txn.txn_type]}`}>
                  {txn.txn_type}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {isWithdrawModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-sm w-full p-6 space-y-4 shadow-xl">
            <h2 className="text-lg font-bold text-gray-900">Withdraw Funds</h2>
            <p className="text-sm text-gray-500">Available Balance: ₹{parseFloat(wallet?.balance || 0).toFixed(2)}</p>
            
            <form onSubmit={handleWithdraw} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  max={wallet?.balance}
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-2.5 outline-none focus:border-blue-500"
                  placeholder="0.00"
                  required
                />
              </div>
              
              {withdrawError && (
                <div className="text-red-600 text-sm bg-red-50 p-2 rounded">{withdrawError}</div>
              )}

              <div className="flex gap-3 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setIsWithdrawModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isWithdrawing}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
                >
                  {isWithdrawing ? 'Processing...' : 'Withdraw'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
