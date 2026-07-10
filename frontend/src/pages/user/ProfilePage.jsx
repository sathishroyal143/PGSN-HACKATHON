import { useEffect, useState, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchMe, updateNotificationPrefs, updateMe, updateUserProfilePicture } from '../../redux/slices/userSlice'
import { fetchMyProfile as fetchCompanionProfile } from '../../redux/slices/companionsSlice'
import { fetchCurrentUser } from '../../redux/slices/authSlice'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const dispatch = useDispatch()
  const { profile, loading, error } = useSelector((s) => s.user)
  const { myProfile: companionProfile, loading: companionLoading } = useSelector((s) => s.companions)

  const [isEditingUser, setIsEditingUser] = useState(false)
  const [selectedImageFile, setSelectedImageFile] = useState(null)
  const [previewImageUrl, setPreviewImageUrl] = useState(null)
  const fileInputRef = useRef(null)

  const { register, handleSubmit, reset } = useForm({
    defaultValues: {
      first_name: '',
      last_name: '',
      phone_number: '',
      city: '',
      state: '',
    }
  })

  // Set default values when profile loads
  useEffect(() => {
    if (profile) {
      reset({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        phone_number: profile.phone_number || '',
        city: profile.city || '',
        state: profile.state || '',
      })
    }
  }, [profile, reset])

  useEffect(() => { dispatch(fetchMe()) }, [dispatch])
  useEffect(() => { if (error) toast.error(error) }, [error])
  
  useEffect(() => {
    if (profile?.role === 'COMPANION') {
      dispatch(fetchCompanionProfile())
    }
  }, [dispatch, profile?.role])

  const togglePref = async (key) => {
    if (!profile) return
    const result = await dispatch(updateNotificationPrefs({
      id: profile.id,
      data: { [key]: !profile[key] },
    }))
    if (updateNotificationPrefs.fulfilled.match(result)) toast.success('Preference updated.')
  }

  const handleCancelEdit = () => {
    setIsEditingUser(false)
    reset()
    setSelectedImageFile(null)
    if (previewImageUrl) {
      URL.revokeObjectURL(previewImageUrl)
      setPreviewImageUrl(null)
    }
  }

  const onUserSubmit = async (data) => {
    if (!profile) return

    let pictureSuccess = true
    if (selectedImageFile) {
      const formData = new FormData()
      formData.append('profile_picture', selectedImageFile)
      const picResult = await dispatch(updateUserProfilePicture({ id: profile.id, formData }))
      if (!updateUserProfilePicture.fulfilled.match(picResult)) {
        pictureSuccess = false
        toast.error(picResult.payload || 'Failed to update profile picture.')
      }
    }

    const result = await dispatch(updateMe({ id: profile.id, data }))
    
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
      await dispatch(fetchMe())
      await dispatch(fetchCurrentUser())
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

  if (loading && !profile) return <div className="p-8 text-gray-500">Loading…</div>
  if (!profile) return null

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
      </div>

      {profile?.role === 'COMPANION' && companionProfile?.status === 'PENDING_VERIFICATION' && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md shadow-sm">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Verification Pending</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  Please complete your mandatory document verification (Aadhar, PAN, Driving License) to get your profile approved and start accepting care journeys.
                </p>
              </div>
              <div className="mt-4">
                <div className="-mx-2 -my-1.5 flex">
                  <Link to="/companion/verification" className="rounded-md bg-yellow-50 px-2 py-1.5 text-sm font-medium text-yellow-800 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 focus:ring-offset-yellow-50 transition-colors">
                    Go to Verification Status
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

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
              {previewImageUrl || profile?.profile_picture ? (
                <img src={previewImageUrl || getImageUrl(profile.profile_picture)} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <span className="text-gray-400 text-2xl font-semibold">
                  {profile?.first_name?.charAt(0) || profile?.email?.charAt(0)}
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
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                    <input
                      {...register('city')}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                    <input
                      {...register('state')}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
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
                      value={profile?.email || ''}
                      disabled
                      className="w-full border border-gray-200 bg-gray-50 text-gray-500 rounded-lg px-3 py-2 text-sm"
                    />
                    <p className="text-xs text-gray-400 mt-1">Email cannot be changed here.</p>
                  </div>
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
              <div className="space-y-0 text-sm">
                <div className="grid grid-cols-3 py-2 border-b border-gray-50 items-center">
                  <span className="text-gray-500 font-medium col-span-1">Name</span>
                  <span className="text-gray-900 col-span-2 font-medium">{profile?.first_name} {profile?.last_name}</span>
                </div>
                <div className="grid grid-cols-3 py-2 border-b border-gray-50 items-center">
                  <span className="text-gray-500 font-medium col-span-1">Email</span>
                  <span className="text-gray-900 col-span-2 font-medium">{profile.email}</span>
                </div>
                <div className="grid grid-cols-3 py-2 items-center">
                  <span className="text-gray-500 font-medium col-span-1">Phone</span>
                  <span className="text-gray-900 col-span-2 font-medium">{profile.phone_number || '—'}</span>
                </div>
                
                {profile.bio && (
                  <div className="grid grid-cols-3 py-2 items-start">
                    <span className="text-gray-500 font-medium col-span-1 mt-1">Bio</span>
                    <span className="text-gray-900 col-span-2">{profile.bio}</span>
                  </div>
                )}
                
                <div className="grid grid-cols-3 py-2 items-center">
                  <span className="text-gray-500 font-medium col-span-1">Location</span>
                  <span className="text-gray-900 col-span-2">{profile.city || '—'}, {profile.state || '—'}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

        {profile.role === 'COMPANION' ? (
          companionProfile && (
            <div className="space-y-6">
              {/* Skills */}
              {companionProfile.skills?.length > 0 && (
                <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6">
                  <h2 className="font-semibold text-gray-800 mb-3">Skills</h2>
                  <div className="flex flex-wrap gap-2">
                    {companionProfile.skills.map((s) => (
                      <span
                        key={s.id}
                        className={`px-3 py-1 rounded-full text-sm border ${s.verified ? 'bg-green-50 border-green-300 text-green-800' : 'bg-gray-50 border-gray-200 text-gray-600'}`}
                      >
                        {s.skill.replace(/_/g, ' ')}
                        {s.verified && ' ✓'}
                        <span className="ml-1 text-xs opacity-60">L{s.proficiency_level}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Languages & Certifications */}
              {(companionProfile.languages_spoken?.length > 0 || companionProfile.certifications?.length > 0) && (
                <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6 grid grid-cols-2 gap-4">
                  {companionProfile.languages_spoken?.length > 0 && (
                    <div>
                      <h2 className="font-semibold text-gray-800 mb-2 text-sm">Languages</h2>
                      <div className="flex flex-wrap gap-1">
                        {companionProfile.languages_spoken.map((l) => (
                          <span key={l} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{l}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {companionProfile.certifications?.length > 0 && (
                    <div>
                      <h2 className="font-semibold text-gray-800 mb-2 text-sm">Certifications</h2>
                      <ul className="space-y-0.5">
                        {companionProfile.certifications.map((c, i) => (
                          <li key={i} className="text-sm text-gray-700">• {c}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Availability Slots */}
              {companionProfile.availability_slots?.length > 0 && (
                <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6">
                  <h2 className="font-semibold text-gray-800 mb-3">Weekly Availability</h2>
                  <div className="space-y-2">
                    {companionProfile.availability_slots.filter((s) => s.is_active).map((slot) => (
                      <div key={slot.id} className="flex items-center gap-3 text-sm">
                        <span className="w-10 font-medium text-gray-600">
                          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][slot.day_of_week]}
                        </span>
                        <span className="text-gray-800">{slot.start_time} – {slot.end_time}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Vehicle */}
              {companionProfile.vehicle_type && companionProfile.vehicle_type !== 'NONE' && (
                <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6">
                  <h2 className="font-semibold text-gray-800 mb-1">Vehicle</h2>
                  <p className="text-sm text-gray-700">
                    {companionProfile.vehicle_type}
                    {companionProfile.vehicle_number && ` — ${companionProfile.vehicle_number}`}
                  </p>
                </div>
              )}
            </div>
          )
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Notification Preferences</h2>
            <div className="space-y-3">
              {[
                ['notification_enabled', 'All Notifications'],
                ['email_notification_enabled', 'Email Notifications'],
                ['sms_notification_enabled', 'SMS Notifications'],
                ['push_notification_enabled', 'Push Notifications'],
              ].map(([key, label]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{label}</span>
                  <button
                    onClick={() => togglePref(key)}
                    disabled={loading}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-50 ${profile[key] ? 'bg-primary-600' : 'bg-gray-200'}`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${profile[key] ? 'translate-x-6' : 'translate-x-1'}`} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
    </div>
  )
}
