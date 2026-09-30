import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { CreditCard, Wallet, ArrowUpRight, ArrowDownLeft, Building, Receipt, HandCoins, ExternalLink } from 'lucide-react'
import { fetchWalletTransactions, fetchWallet, withdrawWallet } from '../../redux/slices/paymentsSlice'

const STATUS_COLORS = {
  success: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  pending: 'bg-amber-100 text-amber-800 border-amber-200',
  failed: 'bg-rose-100 text-rose-800 border-rose-200',
  refunded: 'bg-blue-100 text-blue-800 border-blue-200',
  cancelled: 'bg-gray-100 text-gray-600 border-gray-200',
  credit: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  debit: 'bg-rose-100 text-rose-800 border-rose-200'
}

function fmt(dt) {
  return dt ? new Date(dt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
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

  if (loading && !walletTransactions.length) return (
    <div className="flex items-center justify-center h-[50vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Earnings & Payments</h1>
          <p className="text-gray-500 mt-1 font-medium">Track your income, view transactions, and withdraw funds.</p>
        </div>
        <button 
          onClick={() => navigate('/companion/history')}
          className="flex items-center gap-2 bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 px-4 py-2.5 rounded-xl font-bold text-sm transition-all shadow-sm"
        >
          <Receipt size={18} /> View Invoices
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-center font-semibold">
          {error}
        </div>
      )}

      {/* Wallet / Earnings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Wallet Card */}
        {wallet && (
          <div className="lg:col-span-2 bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-700 rounded-3xl p-8 text-white shadow-xl shadow-teal-900/20 relative overflow-hidden group">
            <div className="absolute -right-20 -top-20 w-64 h-64 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700" />
            <div className="absolute -left-10 -bottom-10 w-40 h-40 bg-teal-400/20 rounded-full blur-2xl" />
            
            <div className="relative z-10 flex flex-col h-full justify-between">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <p className="text-emerald-100 font-semibold tracking-wide uppercase text-sm mb-1">Available Balance</p>
                  <h2 className="text-5xl font-extrabold tracking-tight">₹{parseFloat(wallet.balance).toFixed(2)}</h2>
                </div>
                <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm border border-white/10">
                  <Wallet size={36} className="text-white" />
                </div>
              </div>
              
              <div className="flex items-center gap-4 mt-auto">
                <button 
                  onClick={() => setIsWithdrawModalOpen(true)}
                  className="bg-white text-teal-800 hover:bg-emerald-50 px-6 py-3 rounded-xl font-bold transition-all shadow-lg hover:shadow-xl hover:scale-[1.02] flex items-center gap-2"
                >
                  <Building size={20} />
                  Withdraw to Bank
                </button>
                <p className="text-sm text-teal-100 font-medium">Transfers usually take 1-3 business days.</p>
              </div>
            </div>
          </div>
        )}

        {/* Quick Stats side card */}
        <div className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm flex flex-col justify-center space-y-6">
          <div className="flex items-start gap-4">
            <div className="bg-blue-50 p-3 rounded-xl border border-blue-100 text-blue-600">
              <HandCoins size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-semibold">Total Earned (All time)</p>
              <p className="text-2xl font-bold text-gray-900 mt-0.5">₹{walletTransactions.filter(t => t.txn_type === 'credit').reduce((sum, t) => sum + parseFloat(t.amount), 0).toFixed(2)}</p>
            </div>
          </div>
          <div className="w-full h-px bg-gray-100" />
          <div className="flex items-start gap-4">
            <div className="bg-purple-50 p-3 rounded-xl border border-purple-100 text-purple-600">
              <CreditCard size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 font-semibold">Last Withdrawal</p>
              <p className="text-lg font-bold text-gray-900 mt-0.5">
                {walletTransactions.find(t => t.txn_type === 'debit') ? `₹${parseFloat(walletTransactions.find(t => t.txn_type === 'debit').amount).toFixed(2)}` : 'None'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-100 rounded-3xl shadow-sm overflow-hidden mt-8">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-xl font-bold text-gray-900">Transaction History</h2>
          <button className="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1 transition-colors">
            Download Statement <ExternalLink size={16} />
          </button>
        </div>

        {walletTransactions.length === 0 && !loading ? (
          <div className="text-center py-24 bg-gray-50/50">
            <div className="bg-white p-6 rounded-full inline-block shadow-sm mb-4 border border-gray-100">
              <CreditCard size={40} className="text-gray-300" />
            </div>
            <h3 className="font-bold text-gray-900 text-lg">No Transactions Yet</h3>
            <p className="text-gray-500 mt-1 max-w-sm mx-auto">Your earnings and withdrawals will appear here once you complete care assignments.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50/80">
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Transaction</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Date & Time</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {walletTransactions.map((txn) => (
                  <tr key={txn.id} className="hover:bg-gray-50/80 transition-colors group">
                    <td className="px-6 py-5">
                      <div className="flex items-center gap-4">
                        <div className={`p-2.5 rounded-xl border ${txn.txn_type === 'credit' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' : 'bg-gray-50 border-gray-200 text-gray-600'}`}>
                          {txn.txn_type === 'credit' ? <ArrowDownLeft size={20} /> : <ArrowUpRight size={20} />}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900 truncate max-w-xs">{txn.description}</p>
                          <p className="text-xs text-gray-500 font-medium">Txn ID: {txn.id.substring(0, 8)}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <span className="text-sm font-medium text-gray-700">{fmt(txn.created_at)}</span>
                    </td>
                    <td className="px-6 py-5">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border capitalize ${STATUS_COLORS[txn.txn_type]}`}>
                        {txn.txn_type}
                      </span>
                    </td>
                    <td className="px-6 py-5 text-right">
                      <span className={`text-base font-bold ${txn.txn_type === 'credit' ? 'text-emerald-600' : 'text-gray-900'}`}>
                        {txn.txn_type === 'credit' ? '+' : '-'}₹{parseFloat(txn.amount).toFixed(2)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Withdraw Modal */}
      {isWithdrawModalOpen && (
        <div className="fixed inset-0 bg-gray-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl max-w-md w-full p-8 shadow-2xl scale-100 animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Withdraw Funds</h2>
                <p className="text-sm font-medium text-gray-500 mt-1">Available: ₹{parseFloat(wallet?.balance || 0).toFixed(2)}</p>
              </div>
              <div className="bg-teal-50 p-3 rounded-2xl text-teal-600">
                <Building size={24} />
              </div>
            </div>
            
            <form onSubmit={handleWithdraw} className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Amount to Withdraw (₹)</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="text-gray-500 font-bold text-lg">₹</span>
                  </div>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    max={wallet?.balance}
                    value={withdrawAmount}
                    onChange={(e) => setWithdrawAmount(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 rounded-2xl pl-10 pr-4 py-3.5 text-lg font-bold text-gray-900 outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10 transition-all"
                    placeholder="0.00"
                    required
                  />
                </div>
              </div>
              
              {withdrawError && (
                <div className="text-rose-600 text-sm font-semibold bg-rose-50 border border-rose-100 p-3 rounded-xl">{withdrawError}</div>
              )}

              <div className="flex gap-3 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setIsWithdrawModalOpen(false)}
                  className="px-6 py-3 text-sm font-bold text-gray-700 bg-white border border-gray-200 hover:bg-gray-50 hover:text-gray-900 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isWithdrawing}
                  className="px-6 py-3 text-sm font-bold text-white bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 rounded-xl transition-all shadow-md shadow-teal-500/20 disabled:opacity-50 flex items-center gap-2"
                >
                  {isWithdrawing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/40 border-t-white"></div>
                      Processing...
                    </>
                  ) : 'Confirm Withdrawal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
