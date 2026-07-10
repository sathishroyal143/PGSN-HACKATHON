import { NavLink, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logoutUser } from '../redux/slices/authSlice'
import {
  LayoutDashboard, Users, UserCircle, HeartPulse, FileText,
  Stethoscope, CalendarCheck, MapPin, MessageSquare, Bell,
  CreditCard, Star, LifeBuoy, ShieldCheck, Brain, BarChart2,
  KeyRound, LogOut, ChevronDown, ChevronRight, Route, UserCog,
} from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  {
    label: 'People', icon: Users, children: [
      { label: 'My Profile', to: '/profile', icon: UserCircle },
      { label: 'Family', to: '/family/profile', icon: Users },
      { label: 'Members', to: '/family/members', icon: Users },
      { label: 'Emergency Contacts', to: '/family/emergency-contacts', icon: HeartPulse },
      { label: 'Patients', to: '/patients', icon: Stethoscope },
      { label: 'Companions', to: '/companions', icon: UserCog },
    ],
  },
  {
    label: 'Care', icon: HeartPulse, children: [
      { label: 'Medical Records', to: '/patients', icon: FileText },
      { label: 'Care Journey', to: '/journeys', icon: Route },
      { label: 'Services', to: '/services', icon: Stethoscope },
      { label: 'Bookings', to: '/bookings', icon: CalendarCheck },
      { label: 'New Booking', to: '/bookings/new', icon: CalendarCheck, roles: ['FAMILY', 'ADMIN'] },
      { label: 'Pending Requests', to: '/bookings/requests', icon: Bell, roles: ['COMPANION', 'ADMIN'] },
      { label: 'Live Tracking', to: '/tracking', icon: MapPin },
    ],
  },
  {
    label: 'Communication', icon: MessageSquare, children: [
      { label: 'Messages', to: '/communication', icon: MessageSquare },
      { label: 'Notifications', to: '/notifications', icon: Bell },
    ],
  },
  {
    label: 'Finance', icon: CreditCard, children: [
      { label: 'Payments', to: '/payments', icon: CreditCard },
      { label: 'Invoices', to: '/payments/invoices', icon: FileText },
    ],
  },
  { label: 'Reviews', to: '/reviews', icon: Star },
  { label: 'Support', to: '/support', icon: LifeBuoy },
  { label: 'Verification', to: '/verification', icon: ShieldCheck },
  {
    label: 'Intelligence', icon: Brain, children: [
      { label: 'AI Engine', to: '/ai', icon: Brain },
      { label: 'Analytics', to: '/analytics', icon: BarChart2 },
    ],
  },
  { label: 'API Gateway', to: '/api-gateway', icon: KeyRound },
]

function NavItem({ item, depth = 0, userRole }) {
  const [open, setOpen] = useState(false)
  const Icon = item.icon

  // Filter by roles if specified
  if (item.roles && userRole && !item.roles.includes(userRole)) return null

  if (item.children) {
    // Filter children by roles
    const visibleChildren = item.children.filter(
      (c) => !c.roles || !userRole || c.roles.includes(userRole)
    )
    if (visibleChildren.length === 0) return null

    return (
      <div>
        <button
          onClick={() => setOpen((o) => !o)}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
        >
          <Icon size={16} className="shrink-0" />
          <span className="flex-1 text-left font-medium">{item.label}</span>
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        {open && (
          <div className="ml-4 mt-0.5 space-y-0.5 border-l border-gray-200 pl-2">
            {visibleChildren.map((child) => (
              <NavItem key={child.to} item={child} depth={depth + 1} userRole={userRole} />
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
        `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
          isActive
            ? 'bg-blue-50 text-blue-700 font-semibold'
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
        }`
      }
    >
      <Icon size={16} className="shrink-0" />
      <span>{item.label}</span>
    </NavLink>
  )
}

export default function Sidebar({ onClose }) {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const user = useSelector((s) => s.auth.user || s.user.profile)

  const handleLogout = async () => {
    await dispatch(logoutUser())
    navigate('/login')
  }

  const getImageUrl = (url) => {
    if (!url) return ''
    if (url.startsWith('http')) return url
    return `http://127.0.0.1:8000${url}`
  }

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200 w-64">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-gray-100">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <HeartPulse size={18} className="text-white" />
        </div>
        <span className="font-bold text-gray-900 text-base">CareBridge</span>
        {onClose && (
          <button onClick={onClose} className="ml-auto text-gray-400 hover:text-gray-600 lg:hidden">✕</button>
        )}
      </div>

      {/* User pill */}
      {user && (
        <div className="px-4 py-3 border-b border-gray-100">
          <NavLink to="/profile" className="flex items-center gap-2 hover:opacity-80">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm shrink-0 overflow-hidden">
              {user.profile_picture ? (
                <img src={getImageUrl(user.profile_picture)} alt="avatar" className="w-full h-full object-cover" />
              ) : (
                <>{user.first_name?.[0]}{user.last_name?.[0]}</>
              )}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user.first_name} {user.last_name}</p>
              <p className="text-xs text-gray-400 capitalize truncate">{user.role}</p>
            </div>
          </NavLink>
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-0.5">
        {NAV.map((item) => (
          <NavItem key={item.label} item={item} userRole={user?.role} />
        ))}
      </nav>

      {/* Logout */}
      <div className="px-3 py-3 border-t border-gray-100">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-red-500 hover:bg-red-50 transition-colors"
        >
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  )
}
