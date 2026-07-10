import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useForm } from 'react-hook-form'
import { fetchPreferences, updatePreferences } from '../../redux/slices/notificationsSlice'

function Toggle({ label, name, register }) {
  return (
    <label className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0 cursor-pointer">
      <span className="text-sm text-gray-700">{label}</span>
      <input type="checkbox" {...register(name)} className="w-4 h-4 accent-blue-600" />
    </label>
  )
}

export default function NotificationPreferencesPage() {
  const dispatch = useDispatch()
  const { preferences, loading } = useSelector((s) => s.notifications)
  const { register, handleSubmit, reset } = useForm()

  useEffect(() => { dispatch(fetchPreferences()) }, [dispatch])
  useEffect(() => { if (preferences) reset(preferences) }, [preferences, reset])

  const onSubmit = (data) => dispatch(updatePreferences(data))

  if (loading && !preferences) {
    return <div className="p-6 text-center text-gray-500">Loading…</div>
  }

  return (
    <div className="max-w-md mx-auto p-4 space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Notification Preferences</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white border border-gray-200 rounded-lg p-4 space-y-1">
        <Toggle label="In-App Notifications" name="in_app_enabled" register={register} />
        <Toggle label="Email Notifications" name="email_enabled" register={register} />
        <Toggle label="SMS Notifications" name="sms_enabled" register={register} />
        <Toggle label="Push Notifications" name="push_enabled" register={register} />
        <button
          type="submit"
          className="mt-4 w-full py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          Save Preferences
        </button>
      </form>
    </div>
  )
}
