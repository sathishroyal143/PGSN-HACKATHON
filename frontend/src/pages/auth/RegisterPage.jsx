import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { registerUser, clearError } from '../../redux/slices/authSlice'
import toast from 'react-hot-toast'
import loginBg from '../../assets/login-bg.png'

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
    <div className="relative group">
      <input
        {...register(name)}
        type={type}
        id={name}
        placeholder=" "
        className={`peer w-full bg-transparent border rounded-xl px-4 py-3.5 text-sm text-white transition-all duration-300 outline-none
          ${errors[name] ? 'border-red-500 focus:border-red-500 shadow-[0_0_10px_rgba(239,68,68,0.2)]' : 'border-gray-700 hover:border-gray-500 focus:border-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.0)] focus:shadow-[0_0_15px_rgba(6,182,212,0.15)]'}
        `}
      />
      <label htmlFor={name} className="absolute left-4 top-3.5 text-sm text-gray-500 transition-all duration-200 z-10 pointer-events-none peer-focus:-top-2.5 peer-focus:text-xs peer-focus:text-cyan-400 peer-focus:bg-[#0d131a] peer-focus:px-1 peer-[:not(:placeholder-shown)]:-top-2.5 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:bg-[#0d131a] peer-[:not(:placeholder-shown)]:px-1 peer-[:not(:placeholder-shown)]:text-gray-300">
        {label}
      </label>
      {errors[name] && <p className="text-red-400 text-xs mt-1 absolute -bottom-5 left-1">{errors[name].message}</p>}
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0f16] overflow-hidden relative selection:bg-cyan-500/30 p-4">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-cyan-600/20 rounded-full blur-[120px] pointer-events-none animate-pulse duration-10000" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none animate-pulse duration-7000" />
      
      <div className="w-full max-w-6xl h-auto min-h-[750px] flex rounded-3xl overflow-hidden shadow-2xl shadow-cyan-900/20 border border-white/5 relative z-10 backdrop-blur-xl">
        
        {/* Left Side: Image & Glassmorphism Overlay */}
        <div className="hidden lg:flex lg:w-5/12 relative bg-gray-900">
          <img src={loginBg} alt="CareBridge AI Technology" className="absolute inset-0 w-full h-full object-cover opacity-80" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0a0f16] via-[#0a0f16]/40 to-transparent opacity-90" />
          <div className="absolute inset-0 bg-cyan-900/10 mix-blend-overlay" />
          
          <div className="relative z-10 flex flex-col justify-end p-12 w-full h-full text-white">
            <div className="backdrop-blur-md bg-white/5 border border-white/10 p-8 rounded-2xl transform transition-transform duration-700 hover:-translate-y-2 hover:bg-white/10 shadow-xl shadow-black/50 group">
              <h2 className="text-4xl font-extrabold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent drop-shadow-lg">
                Join CareBridge
              </h2>
              <p className="text-gray-300 text-lg leading-relaxed font-light">
                Sign up today and experience the future of personalized, AI-driven healthcare support for you and your loved ones.
              </p>
              <div className="mt-8 flex items-center gap-4 opacity-80 group-hover:opacity-100 transition-opacity">
                <div className="flex -space-x-4">
                  <div className="w-10 h-10 rounded-full border-2 border-[#0a0f16] bg-gradient-to-br from-cyan-400 to-blue-600" />
                  <div className="w-10 h-10 rounded-full border-2 border-[#0a0f16] bg-gradient-to-br from-blue-400 to-indigo-600" />
                  <div className="w-10 h-10 rounded-full border-2 border-[#0a0f16] bg-gradient-to-br from-indigo-400 to-purple-600" />
                </div>
                <span className="text-sm text-cyan-300 font-medium tracking-wide">Trusted by 10,000+ caregivers</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Registration Form */}
        <div className="w-full lg:w-7/12 flex flex-col justify-center p-8 sm:p-12 lg:p-16 bg-[#0d131a] relative">
          <div className="absolute top-8 right-8">
            <span className="text-xs font-semibold tracking-widest text-cyan-500/80 uppercase">Secure Portal</span>
          </div>
          
          <div className="w-full max-w-lg mx-auto space-y-8">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white tracking-tight">Create account</h1>
              <p className="text-gray-400 text-sm">Fill in the details below to join CareBridge AI today.</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              
              <div className="grid grid-cols-2 gap-4">
                <Field name="first_name" label="First Name" />
                <Field name="last_name" label="Last Name" />
              </div>

              <Field name="email" label="Email Address" type="email" />
              <Field name="phone_number" label="Phone Number" />

              <div className="relative group pt-1 pb-1">
                <select
                  {...register('role')}
                  className="w-full bg-[#0d131a] text-white border border-gray-700 hover:border-gray-500 focus:border-cyan-500 rounded-xl px-4 py-3.5 text-sm transition-all duration-300 outline-none shadow-[0_0_15px_rgba(6,182,212,0.0)] focus:shadow-[0_0_15px_rgba(6,182,212,0.15)] appearance-none"
                >
                  <option value="FAMILY">Family Member</option>
                  <option value="COMPANION">Care Companion</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-400">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
                <label className="absolute left-4 -top-2.5 text-xs text-cyan-400 bg-[#0d131a] px-1 z-10 pointer-events-none font-medium">
                  Select Role
                </label>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Field name="password" label="Password" type="password" />
                <Field name="password_confirmation" label="Confirm Password" type="password" />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="relative w-full h-12 rounded-xl text-white font-semibold text-sm overflow-hidden group disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-[0_0_20px_rgba(8,145,178,0.3)] hover:shadow-[0_0_25px_rgba(8,145,178,0.5)]"
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
                        Creating account...
                      </>
                    ) : 'Create Account'}
                  </div>
                </button>
              </div>
            </form>

            <div className="pt-6 text-center border-t border-gray-800/60">
              <p className="text-sm text-gray-400">
                Already have an account?{' '}
                <Link to="/login" className="text-white hover:text-cyan-400 font-semibold transition-colors">
                  Sign in instead
                </Link>
              </p>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  )
}
