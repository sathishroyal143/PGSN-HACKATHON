import { useEffect, useState, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { Camera, Edit3, X, Save, AlertCircle, ShieldAlert, ChevronRight, User, Mail, Phone, MapPin, CheckCircle2, Car, Clock, BookOpen, Settings } from 'lucide-react'
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

  if (loading && !profile) return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  )
  if (!profile) return null

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-8 space-y-8 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">My Profile</h1>
          <p className="text-gray-500 mt-1 font-medium">Manage your personal information and preferences.</p>
        </div>
      </div>

      {profile?.role === 'COMPANION' && companionProfile?.status === 'PENDING_VERIFICATION' && (
        <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 p-6 rounded-2xl shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="bg-amber-100 p-3 rounded-full text-amber-600 mt-1">
              <ShieldAlert size={24} />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-lg">Action Required: Complete Verification</h3>
              <p className="text-gray-600 mt-1 font-medium">
                Please complete your mandatory document verification (Aadhar, PAN, Driving License) to get your profile approved and start accepting care journeys.
              </p>
            </div>
          </div>
          <Link to="/companion/verification" className="shrink-0 inline-flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 rounded-xl font-bold transition-colors shadow-sm">
            Go to Verification <ChevronRight size={18} />
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Avatar & Basic Info */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8 text-center relative overflow-hidden group">
            {/* Header background accent */}
            <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-primary-50 to-white -z-10" />
            
            <div className="relative inline-block mb-6">
              <div className="w-32 h-32 rounded-full bg-white border-4 border-white shadow-lg overflow-hidden flex items-center justify-center relative">
                {previewImageUrl || profile?.profile_picture ? (
                  <img src={previewImageUrl || getImageUrl(profile.profile_picture)} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-primary-600 text-5xl font-bold">
                    {profile?.first_name?.charAt(0) || profile?.email?.charAt(0)}
                  </span>
                )}
              </div>
              {isEditingUser && (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="absolute bottom-0 right-0 bg-primary-600 hover:bg-primary-700 text-white p-2.5 rounded-full shadow-lg transition-transform hover:scale-110"
                  title="Change Picture"
                >
                  <Camera size={18} />
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

            <h2 className="text-2xl font-bold text-gray-900">{profile.first_name} {profile.last_name}</h2>
            <p className="text-gray-500 font-medium uppercase tracking-wider text-xs mt-1 mb-4">{profile.role}</p>
            
            <div className="flex flex-col gap-3 text-sm text-gray-600 font-medium mt-6">
              <div className="flex items-center justify-center gap-2 bg-gray-50 py-2 px-4 rounded-xl">
                <Mail size={16} className="text-gray-400" /> <span className="truncate">{profile.email}</span>
              </div>
              {profile.phone_number && (
                <div className="flex items-center justify-center gap-2 bg-gray-50 py-2 px-4 rounded-xl">
                  <Phone size={16} className="text-gray-400" /> <span>{profile.phone_number}</span>
                </div>
              )}
              {(profile.city || profile.state) && (
                <div className="flex items-center justify-center gap-2 bg-gray-50 py-2 px-4 rounded-xl">
                  <MapPin size={16} className="text-gray-400" /> <span>{profile.city}, {profile.state}</span>
                </div>
              )}
            </div>
          </div>

          {!isEditingUser && profile.role !== 'COMPANION' && (
            <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center gap-2 mb-6 border-b border-gray-100 pb-4">
                <Settings size={20} className="text-primary-500" />
                <h2 className="text-lg font-bold text-gray-900">Notification Preferences</h2>
              </div>
              <div className="space-y-4">
                {[
                  ['notification_enabled', 'In-App Notifications'],
                  ['email_notification_enabled', 'Email Alerts'],
                  ['sms_notification_enabled', 'SMS Messages'],
                  ['push_notification_enabled', 'Push Notifications'],
                ].map(([key, label]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{label}</span>
                    <button
                      onClick={() => togglePref(key)}
                      disabled={loading}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 ${profile[key] ? 'bg-primary-600' : 'bg-gray-200'}`}
                    >
                      <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${profile[key] ? 'translate-x-6' : 'translate-x-1'}`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Edit Form & Companion Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="px-8 py-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <div className="flex items-center gap-3">
                <div className="bg-white p-2 rounded-lg border border-gray-200 shadow-sm">
                  <User size={20} className="text-gray-700" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Personal Details</h2>
              </div>
              {!isEditingUser && (
                <button
                  onClick={() => setIsEditingUser(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-bold text-gray-700 hover:border-primary-300 hover:text-primary-600 transition-colors shadow-sm"
                >
                  <Edit3 size={16} /> Edit Profile
                </button>
              )}
            </div>
            
            <div className="p-8">
              {isEditingUser ? (
                <form onSubmit={handleSubmit(onUserSubmit)} className="space-y-6 animate-in fade-in duration-300">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">First Name</label>
                      <input
                        {...register('first_name')}
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">Last Name</label>
                      <input
                        {...register('last_name')}
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">City</label>
                      <input
                        {...register('city')}
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">State</label>
                      <input
                        {...register('state')}
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">Phone Number</label>
                      <input
                        {...register('phone_number')}
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">Email Address</label>
                      <input
                        value={profile?.email || ''}
                        disabled
                        className="w-full bg-gray-100 border border-gray-200 text-gray-500 rounded-xl px-4 py-3 text-sm font-medium cursor-not-allowed"
                      />
                      <p className="text-xs font-semibold text-gray-400 mt-1.5 flex items-center gap-1">
                        <AlertCircle size={12} /> Contact support to change email.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex gap-3 justify-end pt-4 border-t border-gray-100">
                    <button
                      type="button"
                      onClick={handleCancelEdit}
                      className="flex items-center gap-2 px-6 py-3 text-sm font-bold text-gray-600 bg-white border border-gray-200 hover:bg-gray-50 rounded-xl transition-colors"
                    >
                      <X size={16} /> Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex items-center gap-2 px-8 py-3 text-sm font-bold text-white bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 rounded-xl transition-all shadow-md hover:shadow-lg"
                    >
                      <Save size={16} /> Save Changes
                    </button>
                  </div>
                </form>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-y-8 gap-x-12">
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Full Name</p>
                    <p className="text-base font-semibold text-gray-900">{profile?.first_name} {profile?.last_name}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Email Address</p>
                    <p className="text-base font-semibold text-gray-900">{profile.email}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Phone Number</p>
                    <p className="text-base font-semibold text-gray-900">{profile.phone_number || 'Not provided'}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Location</p>
                    <p className="text-base font-semibold text-gray-900">
                      {profile.city || profile.state ? `${profile.city || ''}, ${profile.state || ''}`.replace(/^, /, '').replace(/, $/, '') : 'Not provided'}
                    </p>
                  </div>
                  {profile.bio && (
                    <div className="md:col-span-2">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Bio</p>
                      <p className="text-base font-medium text-gray-700 bg-gray-50 p-4 rounded-xl border border-gray-100">{profile.bio}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Companion Specific Sections */}
          {profile.role === 'COMPANION' && companionProfile && (
            <div className="space-y-6">
              
              {/* Skills */}
              {companionProfile.skills?.length > 0 && (
                <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
                  <div className="px-8 py-5 border-b border-gray-100 flex items-center gap-3 bg-gray-50/50">
                     <div className="bg-white p-2 rounded-lg border border-gray-200 shadow-sm">
                      <BookOpen size={18} className="text-primary-600" />
                    </div>
                    <h2 className="text-lg font-bold text-gray-900">Verified Skills</h2>
                  </div>
                  <div className="p-8">
                    <div className="flex flex-wrap gap-3">
                      {companionProfile.skills.map((s) => (
                        <div
                          key={s.id}
                          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold border ${s.verified ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-gray-50 border-gray-200 text-gray-600'}`}
                        >
                          <span className="capitalize">{s.skill.replace(/_/g, ' ')}</span>
                          {s.verified && <CheckCircle2 size={14} className="text-emerald-500" />}
                          <span className="ml-1 px-1.5 py-0.5 bg-white/60 rounded-md text-[10px] uppercase tracking-wider opacity-80">
                            L{s.proficiency_level}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Languages & Certifications */}
              {(companionProfile.languages_spoken?.length > 0 || companionProfile.certifications?.length > 0) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {companionProfile.languages_spoken?.length > 0 && (
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
                      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                        <h2 className="text-base font-bold text-gray-900">Languages</h2>
                      </div>
                      <div className="p-6">
                        <div className="flex flex-wrap gap-2">
                          {companionProfile.languages_spoken.map((l) => (
                            <span key={l} className="px-3 py-1.5 bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-lg text-sm font-bold">{l}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {companionProfile.certifications?.length > 0 && (
                    <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
                      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
                        <h2 className="text-base font-bold text-gray-900">Certifications</h2>
                      </div>
                      <div className="p-6">
                        <ul className="space-y-3">
                          {companionProfile.certifications.map((c, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm font-medium text-gray-700">
                              <CheckCircle2 size={16} className="text-primary-500 shrink-0 mt-0.5" />
                              {c}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Weekly Availability & Vehicle Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {companionProfile.availability_slots?.length > 0 && (
                  <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-2 bg-gray-50/50">
                      <Clock size={18} className="text-primary-600" />
                      <h2 className="text-base font-bold text-gray-900">Availability</h2>
                    </div>
                    <div className="p-6">
                      <div className="space-y-3">
                        {companionProfile.availability_slots.filter((s) => s.is_active).map((slot) => (
                          <div key={slot.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                            <span className="font-bold text-gray-700 uppercase tracking-wide text-xs">
                              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][slot.day_of_week]}
                            </span>
                            <span className="text-sm font-bold text-gray-900">{slot.start_time} – {slot.end_time}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {companionProfile.vehicle_type && companionProfile.vehicle_type !== 'NONE' && (
                  <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden h-fit">
                    <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-2 bg-gray-50/50">
                      <Car size={18} className="text-primary-600" />
                      <h2 className="text-base font-bold text-gray-900">Vehicle</h2>
                    </div>
                    <div className="p-6">
                      <div className="bg-gray-50 p-4 rounded-2xl flex flex-col items-center justify-center text-center">
                        <Car size={32} className="text-gray-400 mb-2" />
                        <span className="text-lg font-bold text-gray-900 capitalize">{companionProfile.vehicle_type.replace('_', ' ')}</span>
                        {companionProfile.vehicle_number && (
                          <span className="mt-2 px-3 py-1 bg-white border border-gray-200 text-gray-700 font-bold font-mono text-sm rounded-lg shadow-sm">
                            {companionProfile.vehicle_number}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
              </div>
              
              {/* Notification Preferences (Companion) */}
              {!isEditingUser && (
                <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8">
                  <div className="flex items-center gap-3 mb-6 border-b border-gray-100 pb-4">
                    <div className="bg-gray-50 p-2 rounded-lg border border-gray-200 shadow-sm">
                      <Settings size={20} className="text-gray-700" />
                    </div>
                    <h2 className="text-xl font-bold text-gray-900">Notification Preferences</h2>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {[
                      ['notification_enabled', 'In-App Notifications', 'Receive updates inside the portal'],
                      ['email_notification_enabled', 'Email Alerts', 'Get important updates via email'],
                      ['sms_notification_enabled', 'SMS Messages', 'Receive text alerts for bookings'],
                      ['push_notification_enabled', 'Push Notifications', 'Real-time alerts on your device'],
                    ].map(([key, label, desc]) => (
                      <div key={key} className="flex items-start justify-between bg-gray-50 p-4 rounded-2xl">
                        <div>
                          <span className="block text-sm font-bold text-gray-900">{label}</span>
                          <span className="text-xs font-medium text-gray-500 mt-0.5">{desc}</span>
                        </div>
                        <button
                          onClick={() => togglePref(key)}
                          disabled={loading}
                          className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 mt-1 ${profile[key] ? 'bg-primary-600' : 'bg-gray-300'}`}
                        >
                          <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm ${profile[key] ? 'translate-x-6' : 'translate-x-1'}`} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}

        </div>
      </div>
    </div>
  )
}
