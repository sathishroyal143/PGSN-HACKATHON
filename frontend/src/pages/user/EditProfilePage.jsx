import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { fetchMe, updateMe } from '../../redux/slices/userSlice'
import toast from 'react-hot-toast'

export default function EditProfilePage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { profile, loading, error } = useSelector((s) => s.user)

  const { register, handleSubmit, reset } = useForm()

  useEffect(() => {
    if (!profile) dispatch(fetchMe())
  }, [dispatch, profile])

  useEffect(() => {
    if (profile) {
      reset({
        first_name: profile.first_name,
        last_name: profile.last_name,
        gender: profile.gender,
        date_of_birth: profile.date_of_birth,
        bio: profile.bio,
        address_line_1: profile.address_line_1,
        address_line_2: profile.address_line_2,
        city: profile.city,
        state: profile.state,
        postal_code: profile.postal_code,
        country: profile.country,
        phone_number: profile.phone_number,
      })
    }
  }, [profile, reset])

  useEffect(() => { if (error) toast.error(error) }, [error])

  const onSubmit = async (data) => {
    const result = await dispatch(updateMe({ id: profile.id, data }))
    if (updateMe.fulfilled.match(result)) {
      toast.success('Profile updated!')
      navigate('/profile')
    }
  }

  const Field = ({ name, label, type = 'text' }) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        {...register(name)}
        type={type}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
      />
    </div>
  )

  if (!profile) return <div className="p-8 text-gray-500">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Edit Profile</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Field name="first_name" label="First Name" />
          <Field name="last_name" label="Last Name" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
            <select {...register('gender')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="">Select</option>
              <option value="MALE">Male</option>
              <option value="FEMALE">Female</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
          <Field name="date_of_birth" label="Date of Birth" type="date" />
        </div>

        <Field name="phone_number" label="Phone Number" />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
          <textarea
            {...register('bio')}
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <Field name="address_line_1" label="Address Line 1" />
        <Field name="address_line_2" label="Address Line 2" />

        <div className="grid grid-cols-2 gap-4">
          <Field name="city" label="City" />
          <Field name="state" label="State" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Field name="postal_code" label="Postal Code" />
          <Field name="country" label="Country" />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-primary-600 hover:bg-primary-700 text-white font-medium px-6 py-2 rounded-lg text-sm transition disabled:opacity-50"
          >
            {loading ? 'Saving…' : 'Save Changes'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/profile')}
            className="text-sm text-gray-600 hover:text-gray-900 px-4 py-2 rounded-lg border border-gray-300"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
