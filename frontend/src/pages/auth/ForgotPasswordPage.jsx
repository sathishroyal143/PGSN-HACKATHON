import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { requestPasswordReset, confirmPasswordReset, clearError, clearResetState } from '../../redux/slices/authSlice'
import toast from 'react-hot-toast'
import loginBg from '../../assets/login-bg.png'

const emailSchema = z.object({
  email: z.string().email('Invalid email address'),
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

  const Field = ({ name, label, type = 'text', form }) => (
    <div className="relative group">
      <input
        {...form.register(name)}
        type={type}
        id={name}
        placeholder=" "
        className={`peer w-full bg-transparent border rounded-xl px-4 py-3.5 text-sm text-white transition-all duration-300 outline-none
          ${form.formState.errors[name] ? 'border-red-500 focus:border-red-500 shadow-[0_0_10px_rgba(239,68,68,0.2)]' : 'border-gray-700 hover:border-gray-500 focus:border-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.0)] focus:shadow-[0_0_15px_rgba(6,182,212,0.15)]'}
        `}
      />
      <label htmlFor={name} className="absolute left-4 top-3.5 text-sm text-gray-500 transition-all duration-200 z-10 pointer-events-none peer-focus:-top-2.5 peer-focus:text-xs peer-focus:text-cyan-400 peer-focus:bg-[#0d131a] peer-focus:px-1 peer-[:not(:placeholder-shown)]:-top-2.5 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:bg-[#0d131a] peer-[:not(:placeholder-shown)]:px-1 peer-[:not(:placeholder-shown)]:text-gray-300">
        {label}
      </label>
      {form.formState.errors[name] && <p className="text-red-400 text-xs mt-1 absolute -bottom-5 left-1">{form.formState.errors[name].message}</p>}
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0f16] overflow-hidden relative selection:bg-cyan-500/30 p-4">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-cyan-600/20 rounded-full blur-[120px] pointer-events-none animate-pulse duration-10000" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none animate-pulse duration-7000" />
      
      <div className="w-full max-w-6xl h-[85vh] min-h-[600px] flex rounded-3xl overflow-hidden shadow-2xl shadow-cyan-900/20 border border-white/5 relative z-10 backdrop-blur-xl">
        
        {/* Left Side: Image & Glassmorphism Overlay */}
        <div className="hidden lg:flex lg:w-1/2 relative bg-gray-900">
          <img src={loginBg} alt="CareBridge AI Technology" className="absolute inset-0 w-full h-full object-cover opacity-80" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0a0f16] via-[#0a0f16]/40 to-transparent opacity-90" />
          <div className="absolute inset-0 bg-cyan-900/10 mix-blend-overlay" />
          
          <div className="relative z-10 flex flex-col justify-end p-12 w-full h-full text-white">
            <div className="backdrop-blur-md bg-white/5 border border-white/10 p-8 rounded-2xl transform transition-transform duration-700 hover:-translate-y-2 hover:bg-white/10 shadow-xl shadow-black/50 group">
              <h2 className="text-4xl font-extrabold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent drop-shadow-lg">
                Account Recovery
              </h2>
              <p className="text-gray-300 text-lg leading-relaxed font-light">
                Don't worry, getting back into your CareBridge AI dashboard is quick and secure.
              </p>
            </div>
          </div>
        </div>

        {/* Right Side: Recovery Form */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center p-8 sm:p-12 lg:p-16 bg-[#0d131a] relative">
          <div className="absolute top-8 right-8">
            <span className="text-xs font-semibold tracking-widest text-cyan-500/80 uppercase">Secure Portal</span>
          </div>
          
          <div className="w-full max-w-sm mx-auto space-y-8">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white tracking-tight">
                {step === 'request' ? 'Forgot Password' : 'Set New Password'}
              </h1>
              <p className="text-gray-400 text-sm">
                {step === 'request' 
                  ? "Enter your email and we'll send you a secure reset link."
                  : "Enter the token from your email along with your new password."}
              </p>
            </div>

            {step === 'request' ? (
              <form onSubmit={emailForm.handleSubmit(onRequestSubmit)} className="space-y-7">
                <div className="space-y-6">
                  <Field name="email" label="Email Address" type="email" form={emailForm} />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="relative w-full h-12 rounded-xl text-white font-semibold text-sm overflow-hidden group disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-[0_0_20px_rgba(8,145,178,0.3)] hover:shadow-[0_0_25px_rgba(8,145,178,0.5)] mt-4"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-blue-600 transition-transform duration-500 group-hover:scale-105" />
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-20 bg-white transition-opacity duration-300" />
                  <div className="relative flex items-center justify-center gap-2 h-full">
                    {loading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Sending...
                      </>
                    ) : 'Send Reset Link'}
                  </div>
                </button>
              </form>
            ) : (
              <form onSubmit={resetForm.handleSubmit(onResetSubmit)} className="space-y-7">
                <div className="space-y-6">
                  <Field name="token" label="Reset Token (from email)" type="text" form={resetForm} />
                  <Field name="new_password" label="New Password" type="password" form={resetForm} />
                  <Field name="password_confirmation" label="Confirm Password" type="password" form={resetForm} />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="relative w-full h-12 rounded-xl text-white font-semibold text-sm overflow-hidden group disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-[0_0_20px_rgba(8,145,178,0.3)] hover:shadow-[0_0_25px_rgba(8,145,178,0.5)] mt-4"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-blue-600 transition-transform duration-500 group-hover:scale-105" />
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-20 bg-white transition-opacity duration-300" />
                  <div className="relative flex items-center justify-center gap-2 h-full">
                    {loading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Resetting...
                      </>
                    ) : 'Reset Password'}
                  </div>
                </button>
              </form>
            )}

            <div className="pt-6 text-center border-t border-gray-800/60">
              <Link to="/login" className="text-sm text-cyan-400 hover:text-cyan-300 font-semibold transition-colors hover:underline underline-offset-4">
                &larr; Back to Login
              </Link>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  )
}
