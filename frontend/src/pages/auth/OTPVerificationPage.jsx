import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import { sendVerificationOtp, verifyOtp, clearError, clearOtpState } from '../../redux/slices/authSlice'
import toast from 'react-hot-toast'

const schema = z.object({
  otp_code: z.string().length(6, 'OTP must be 6 digits'),
})

export default function OTPVerificationPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  const { loading, error, otpVerified } = useSelector((s) => s.auth)
  const otp_type = location.state?.otp_type || 'EMAIL_VERIFICATION'
  const [resendCooldown, setResendCooldown] = useState(0)

  const { register, handleSubmit, formState: { errors } } = useForm({ resolver: zodResolver(schema) })

  useEffect(() => {
    dispatch(sendVerificationOtp({ otp_type }))
  }, [])

  useEffect(() => {
    if (error) { toast.error(error); dispatch(clearError()) }
  }, [error, dispatch])

  useEffect(() => {
    if (otpVerified) {
      toast.success('Verified successfully!')
      dispatch(clearOtpState())
      navigate('/dashboard')
    }
  }, [otpVerified, navigate, dispatch])

  useEffect(() => {
    if (resendCooldown > 0) {
      const t = setTimeout(() => setResendCooldown((c) => c - 1), 1000)
      return () => clearTimeout(t)
    }
  }, [resendCooldown])

  const onSubmit = (data) => dispatch(verifyOtp({ ...data, otp_type }))

  const handleResend = () => {
    dispatch(sendVerificationOtp({ otp_type }))
    setResendCooldown(60)
    toast.success('OTP resent!')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-md p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Verify your account</h1>
        <p className="text-gray-500 text-sm mb-6">
          Enter the 6-digit code sent to your {otp_type === 'EMAIL_VERIFICATION' ? 'email' : 'phone'}
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">OTP Code</label>
            <input
              {...register('otp_code')}
              type="text"
              maxLength={6}
              placeholder="123456"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-center tracking-widest text-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            {errors.otp_code && <p className="text-red-500 text-xs mt-1">{errors.otp_code.message}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 rounded-lg text-sm transition disabled:opacity-50"
          >
            {loading ? 'Verifying…' : 'Verify'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Didn't receive it?{' '}
          <button
            onClick={handleResend}
            disabled={resendCooldown > 0}
            className="text-primary-600 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP'}
          </button>
        </p>
      </div>
    </div>
  )
}
