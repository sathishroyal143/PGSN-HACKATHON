import { NavLink, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logoutUser } from '../../redux/slices/authSlice'
import {
  LayoutDashboard, Users, HeartPulse, FileText,
  Stethoscope, CalendarCheck, MapPin, MessageSquare, Bell,
  CreditCard, Star, LifeBuoy, ShieldCheck, Brain, BarChart2,
  KeyRound, LogOut, ChevronDown, ChevronRight, UserCog
} from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { label: 'Dashboard', to: '/admin/dashboard', icon: LayoutDashboard },
  {
    label: 'User Management', icon: Users, children: [
      { label: 'Families', to: '/admin/families', icon: Users },
      { label: 'Patients', to: '/admin/patients', icon: HeartPulse },
      { label: 'Companions', to: '/admin/companions', icon: UserCog },
    ],
  },
  { label: 'Companion Verification', to: '/admin/verification', icon: ShieldCheck },
  { label: 'Service Management', to: '/admin/services', icon: Stethoscope },
  { label: 'Booking Management', to: '/admin/bookings', icon: CalendarCheck },
  { label: 'Payment Management', to: '/admin/payments', icon: CreditCard },
  {
    label: 'Reports & Support', icon: FileText, children: [
      { label: 'Support Tickets', to: '/admin/support', icon: LifeBuoy },
      { label: 'Complaints', to: '/admin/complaints', icon: MessageSquare },
      { label: 'Reviews', to: '/admin/reviews', icon: Star },
    ],
  },
  {
    label: 'Intelligence', icon: Brain, children: [
      { label: 'Analytics', to: '/admin/analytics', icon: BarChart2 },
      { label: 'AI Insights', to: '/admin/ai', icon: Brain },
    ],
  },
  { label: 'API Gateway', to: '/admin/api-gateway', icon: KeyRound },
  { label: 'System Settings', to: '/admin/settings', icon: Bell },
]

function NavItem({ item, depth = 0 }) {
  const [open, setOpen] = useState(false)
  const Icon = item.icon

  if (item.children) {
    return (
      <div className="mb-1">
        <button
          onClick={() => setOpen(!open)}
          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-gray-100 text-gray-700`}
          style={{ paddingLeft: `${depth * 1.5 + 0.75}rem` }}
        >
          <div className="flex items-center gap-3">
            <Icon size={18} className="text-gray-400" />
            {item.label}
          </div>
          {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>
        {open && (
          <div className="mt-1 space-y-1">
            {item.children.map((child, idx) => (
              <NavItem key={idx} item={child} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <NavLink
      to={item.to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors mb-1 ${
          isActive ? 'bg-purple-50 text-purple-700' : 'text-gray-700 hover:bg-gray-100'
        }`
      }
      style={{ paddingLeft: `${depth * 1.5 + 0.75}rem` }}
    >
      <Icon size={18} className="text-gray-400" />
      {item.label}
    </NavLink>
  )
}

export default function AdminSidebar({ onClose }) {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { user } = useSelector((s) => s.auth)

  const handleLogout = () => {
    dispatch(logoutUser())
    navigate('/login')
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-full shadow-sm">
      <div className="h-16 flex items-center px-6 border-b border-gray-100 shrink-0">
        <ShieldCheck className="text-purple-600 mr-2" size={24} />
        <span className="text-xl font-bold text-gray-900 tracking-tight">CareBridge</span>
      </div>

      <div className="p-4 border-b border-gray-100 flex items-center gap-3 shrink-0">
        <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center text-purple-700 font-bold">
          {user?.first_name?.[0] || 'A'}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="text-xs text-purple-600 font-medium">ADMINISTRATOR</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 custom-scrollbar">
        {NAV.map((item, idx) => (
          <NavItem key={idx} item={item} />
        ))}
      </div>

      <div className="p-4 border-t border-gray-100 shrink-0">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  )
}
