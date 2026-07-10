import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { registerUser, clearError } from '../../redux/slices/authSlice'
import toast from 'react-hot-toast'

const schema = z.object({
  first_name: z.string().min(2, 'Min 2 characters'),
  last_name: z.string().min(2, 'Min 2 characters'),
  email: z.string().email('Invalid email'),
  phone_number: z.string().min(10, 'Invalid phone number'),
  password: z.string().min(8, 'Min 8 characters'),
  password_confirmation: z.string(),
  role: z.enum(['FAMILY', 'COMPANION']),
}).refine((d) => d.password === d.password_confirmation, {
  message: 'Passwords do not match',
  path: ['password_confirmation'],
})

export default function RegisterPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { loading, error } = useSelector((s) => s.auth)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { role: 'FAMILY' },
  })

  useEffect(() => {
    if (error) { toast.error(error); dispatch(clearError()) }
  }, [error, dispatch])

  const onSubmit = async (data) => {
    const result = await dispatch(registerUser(data))
    if (registerUser.fulfilled.match(result)) {
      toast.success('Account created! Please verify your email.')
      navigate('/verify-otp', { state: { otp_type: 'EMAIL_VERIFICATION' } })
    }
  }

  const Field = ({ name, label, type = 'text', placeholder }) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        {...register(name)}
        type={type}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
      />
      {errors[name] && <p className="text-red-500 text-xs mt-1">{errors[name].message}</p>}
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-8">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Create account</h1>
        <p className="text-gray-500 text-sm mb-6">Join CareBridge AI today</p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Field name="first_name" label="First Name" placeholder="John" />
            <Field name="last_name" label="Last Name" placeholder="Doe" />
          </div>
          <Field name="email" label="Email" type="email" placeholder="you@example.com" />
          <Field name="phone_number" label="Phone" placeholder="+91XXXXXXXXXX" />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select
              {...register('role')}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="FAMILY">Family Member</option>
              <option value="COMPANION">Care Companion</option>
            </select>
          </div>

          <Field name="password" label="Password" type="password" placeholder="••••••••" />
          <Field name="password_confirmation" label="Confirm Password" type="password" placeholder="••••••••" />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 rounded-lg text-sm transition disabled:opacity-50"
          >
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-600 hover:underline font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
