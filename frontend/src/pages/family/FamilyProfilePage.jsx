import { useEffect, useState, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchProfile } from '../../redux/slices/familySlice'
import { updateMe, updateUserProfilePicture } from '../../redux/slices/userSlice'
import { fetchCurrentUser } from '../../redux/slices/authSlice'
import toast from 'react-hot-toast'
import { fetchWallet, fetchWalletTransactions } from '../../redux/slices/paymentsSlice'
import paymentsApi from '../../api/paymentsApi'

export default function FamilyProfilePage() {
  const dispatch = useDispatch()
  const { profile, loading } = useSelector((s) => s.family)
  const user = useSelector((s) => s.auth.user || s.user.profile)
  const { wallet, walletTransactions, loading: paymentsLoading } = useSelector((s) => s.payments)
  const fileInputRef = useRef(null)

  const [isEditingUser, setIsEditingUser] = useState(false)
  const [selectedImageFile, setSelectedImageFile] = useState(null)
  const [previewImageUrl, setPreviewImageUrl] = useState(null)
  const [rechargeAmount, setRechargeAmount] = useState('1000')
  const [isRecharging, setIsRecharging] = useState(false)
  
  const { register, handleSubmit, reset } = useForm()

  useEffect(() => {
    if (user?.role === 'FAMILY') {
      dispatch(fetchProfile())
      dispatch(fetchWallet())
      dispatch(fetchWalletTransactions())
    }
  }, [dispatch, user])

  useEffect(() => {
    if (user) {
      reset({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone_number: user.phone_number || '',
      })
    }
  }, [user, reset])

  const handleRecharge = async () => {
    if (!rechargeAmount || isNaN(rechargeAmount) || Number(rechargeAmount) <= 0) {
      toast.error('Enter a valid amount')
      return
    }
    setIsRecharging(true)
    try {
      await paymentsApi.rechargeWallet({ amount: Number(rechargeAmount) })
      toast.success(`Successfully recharged ₹${rechargeAmount}`)
      dispatch(fetchWallet())
      dispatch(fetchWalletTransactions())
      setRechargeAmount('')
    } catch (err) {
      toast.error('Recharge failed')
    } finally {
      setIsRecharging(false)
    }
  }

  const handleCancelEdit = () => {
    setIsEditingUser(false)
    setSelectedImageFile(null)
    if (previewImageUrl) {
      URL.revokeObjectURL(previewImageUrl)
      setPreviewImageUrl(null)
    }
    reset()
  }

  const onUserSubmit = async (data) => {
    let pictureSuccess = true
    if (selectedImageFile) {
      const formData = new FormData()
      formData.append('profile_picture', selectedImageFile)
      const picResult = await dispatch(updateUserProfilePicture({ id: user.id, formData }))
      if (!updateUserProfilePicture.fulfilled.match(picResult)) {
        pictureSuccess = false
        toast.error(picResult.payload || 'Failed to update profile picture.')
      }
    }

    const result = await dispatch(updateMe({ id: user.id, data }))
    
    if (updateMe.fulfilled.match(result)) {
      if (pictureSuccess) {
        toast.success(selectedImageFile ? 'Profile updated successfully!' : 'User details updated!')
      } else {
        toast.success('User details updated, but picture update failed.')
      }
      setIsEditingUser(false)
      setSelectedImageFile(null)
      if (previewImageUrl) {
        URL.revokeObjectURL(previewImageUrl)
        setPreviewImageUrl(null)
      }
      await dispatch(fetchProfile()) // Refresh profile to get updated full name
      await dispatch(fetchCurrentUser()) // Refresh auth user
    } else {
      toast.error(result.payload || 'Failed to update user details.')
    }
  }

  const handleProfilePictureChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setSelectedImageFile(file)
    setPreviewImageUrl(URL.createObjectURL(file))
  }

  const getImageUrl = (url) => {
    if (!url) return ''
    if (url.startsWith('http')) return url
    return `http://127.0.0.1:8000${url}`
  }

  if (user && user.role !== 'FAMILY') {

    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6 text-center">
          <p className="text-yellow-800 font-medium">Family Profile is only available for Family role users.</p>
          <p className="text-yellow-600 text-sm mt-1">Your current role is <span className="font-semibold">{user.role}</span>.</p>
        </div>
      </div>
    )
  }

  if (loading && !profile) return <div className="p-8 text-gray-500">Loading profile…</div>

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Family Profile</h1>
      </div>

      {/* Table 1: Family User Details */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-800">User Details</h2>
          {!isEditingUser && (
            <button
              onClick={() => setIsEditingUser(true)}
              className="text-sm text-primary-600 font-medium hover:underline"
            >
              Edit
            </button>
          )}
        </div>
        <div className="p-6 flex flex-col md:flex-row gap-6">
          <div className="flex flex-col items-center gap-3">
            <div className="w-24 h-24 rounded-full bg-gray-100 border-2 border-gray-200 overflow-hidden flex items-center justify-center">
              {previewImageUrl || user?.profile_picture ? (
                <img src={previewImageUrl || getImageUrl(user.profile_picture)} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <span className="text-gray-400 text-2xl font-semibold">
                  {user?.first_name?.charAt(0) || user?.email?.charAt(0)}
                </span>
              )}
            </div>
            {isEditingUser && (
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-xs text-primary-600 font-medium hover:underline bg-primary-50 px-3 py-1 rounded-full"
              >
                Change Pic
              </button>
            )}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleProfilePictureChange}
              className="hidden"
              accept="image/*"
            />
          </div>

          <div className="flex-1">
            {isEditingUser ? (
              <form onSubmit={handleSubmit(onUserSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                    <input
                      {...register('first_name')}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                    <input
                      {...register('last_name')}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                  <input
                    {...register('phone_number')}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    value={user?.email || ''}
                    disabled
                    className="w-full border border-gray-200 bg-gray-50 text-gray-500 rounded-lg px-3 py-2 text-sm"
                  />
                  <p className="text-xs text-gray-400 mt-1">Email cannot be changed here.</p>
                </div>
                <div className="flex gap-3 justify-end">
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition"
                  >
                    Save
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4 text-sm">
                <div className="grid grid-cols-3 py-2 border-b border-gray-50">
                  <span className="text-gray-500 font-medium col-span-1">Name</span>
                  <span className="text-gray-900 col-span-2 font-medium">{profile?.user_full_name || `${user?.first_name} ${user?.last_name}`}</span>
                </div>
                <div className="grid grid-cols-3 py-2 border-b border-gray-50">
                  <span className="text-gray-500 font-medium col-span-1">Email</span>
                  <span className="text-gray-900 col-span-2">{profile?.user_email || user?.email}</span>
                </div>
                <div className="grid grid-cols-3 py-2">
                  <span className="text-gray-500 font-medium col-span-1">Phone</span>
                  <span className="text-gray-900 col-span-2">{user?.phone_number || <span className="text-gray-400 italic">Not provided</span>}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Table 2: Family Overview */}
      {profile && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-800">Family Overview</h2>
          </div>
          <div className="p-0">
            <table className="w-full text-sm text-left">
              <tbody className="divide-y divide-gray-100">
                <tr>
                  <th className="px-6 py-4 font-medium text-gray-500 w-1/3 bg-white">Members</th>
                  <td className="px-6 py-4 text-gray-900 font-medium">
                    {profile.members?.length ?? 0}
                  </td>
                </tr>
                <tr>
                  <th className="px-6 py-4 font-medium text-gray-500 bg-gray-50">Emergency Contacts</th>
                  <td className="px-6 py-4 text-gray-900 font-medium bg-gray-50">
                    {profile.emergency_contacts?.length ?? 0}
                  </td>
                </tr>
                <tr>
                  <th className="px-6 py-4 font-medium text-gray-500 bg-white">Plan</th>
                  <td className="px-6 py-4 text-gray-900 font-medium bg-white">
                    {profile.is_premium ? '⭐ Premium' : 'Free'}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Wallet & Top Up */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-800">Wallet</h2>
        </div>
        <div className="p-6 space-y-6">
          {paymentsLoading && !wallet ? (
            <p className="text-gray-500">Loading wallet...</p>
          ) : (
            <div className="flex flex-col md:flex-row gap-6">
              {/* Balance Card */}
              <div className="flex-1 bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl p-5 text-white flex flex-col justify-between shadow-md">
                <div>
                  <p className="text-sm opacity-80 font-medium">Available Balance</p>
                  <p className="text-3xl font-bold mt-1">₹{parseFloat(wallet?.balance || 0).toFixed(2)}</p>
                </div>
                <p className="text-xs opacity-70 mt-4">Required to request a Care Journey</p>
              </div>
              
              {/* Recharge form */}
              <div className="flex-1 bg-gray-50 rounded-xl p-5 border border-gray-200">
                <h3 className="text-sm font-semibold text-gray-800 mb-3">Recharge Wallet</h3>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 font-medium">₹</span>
                    <input
                      type="number"
                      value={rechargeAmount}
                      onChange={(e) => setRechargeAmount(e.target.value)}
                      className="w-full pl-7 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                      placeholder="Amount"
                    />
                  </div>
                  <button
                    onClick={handleRecharge}
                    disabled={isRecharging}
                    className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition disabled:opacity-50"
                  >
                    {isRecharging ? 'Processing...' : 'Top Up'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Transactions List */}
          <div>
            <h3 className="text-sm font-semibold text-gray-800 mb-3">Recent Transactions</h3>
            {walletTransactions && walletTransactions.length > 0 ? (
              <div className="space-y-2">
                {walletTransactions.slice(0, 5).map((txn) => (
                  <div key={txn.id} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900 truncate max-w-[200px]" title={txn.description}>{txn.description}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {new Date(txn.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </p>
                    </div>
                    <div className={`text-sm font-medium ${txn.txn_type === 'credit' ? 'text-green-600' : 'text-red-600'}`}>
                      {txn.txn_type === 'credit' ? '+' : '-'}₹{parseFloat(txn.amount).toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 italic">No transactions yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
