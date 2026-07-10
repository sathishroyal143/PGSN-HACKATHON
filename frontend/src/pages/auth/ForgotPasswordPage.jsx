import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { requestPasswordReset, confirmPasswordReset, clearError, clearResetState } from '../../redux/slices/authSlice'
import toast from 'react-hot-toast'

const emailSchema = z.object({
  email: z.string().email('Invalid email'),
})

const resetSchema = z.object({
  token: z.string().min(1, 'Token is required'),
  new_password: z.string().min(8, 'Min 8 characters'),
  password_confirmation: z.string(),
}).refine((d) => d.new_password === d.password_confirmation, {
  message: 'Passwords do not match',
  path: ['password_confirmation'],
})

export default function ForgotPasswordPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { loading, error, resetEmailSent, passwordReset } = useSelector((s) => s.auth)
  const [step, setStep] = useState('request') // 'request' | 'reset'

  const emailForm = useForm({ resolver: zodResolver(emailSchema) })
  const resetForm = useForm({ resolver: zodResolver(resetSchema) })

  useEffect(() => {
    if (error) { toast.error(error); dispatch(clearError()) }
  }, [error, dispatch])

  useEffect(() => {
    if (resetEmailSent && step === 'request') {
      toast.success('Reset email sent! Check your inbox.')
      setStep('reset')
    }
  }, [resetEmailSent])

  useEffect(() => {
    if (passwordReset) {
      toast.success('Password reset successfully!')
      dispatch(clearResetState())
      navigate('/login')
    }
  }, [passwordReset, navigate, dispatch])

  const onRequestSubmit = (data) => dispatch(requestPasswordReset(data))
  const onResetSubmit = (data) => dispatch(confirmPasswordReset(data))

  if (step === 'reset') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Set new password</h1>
          <p className="text-gray-500 text-sm mb-6">Enter the token from your email and your new password</p>

          <form onSubmit={resetForm.handleSubmit(onResetSubmit)} className="space-y-4">
            {[
              { name: 'token', label: 'Reset Token', type: 'text', placeholder: 'Paste token from email' },
              { name: 'new_password', label: 'New Password', type: 'password', placeholder: '••••••••' },
              { name: 'password_confirmation', label: 'Confirm Password', type: 'password', placeholder: '••••••••' },
            ].map(({ name, label, type, placeholder }) => (
              <div key={name}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input
                  {...resetForm.register(name)}
                  type={type}
                  placeholder={placeholder}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {resetForm.formState.errors[name] && (
                  <p className="text-red-500 text-xs mt-1">{resetForm.formState.errors[name].message}</p>
                )}
              </div>
            ))}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 rounded-lg text-sm transition disabled:opacity-50"
            >
              {loading ? 'Resetting…' : 'Reset Password'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Forgot password?</h1>
        <p className="text-gray-500 text-sm mb-6">Enter your email and we'll send a reset link</p>

        <form onSubmit={emailForm.handleSubmit(onRequestSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              {...emailForm.register('email')}
              type="email"
              placeholder="you@example.com"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            {emailForm.formState.errors.email && (
              <p className="text-red-500 text-xs mt-1">{emailForm.formState.errors.email.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 rounded-lg text-sm transition disabled:opacity-50"
          >
            {loading ? 'Sending…' : 'Send Reset Email'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          <Link to="/login" className="text-primary-600 hover:underline">Back to login</Link>
        </p>
      </div>
    </div>
  )
}
