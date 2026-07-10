import { NavLink, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logoutUser } from '../../redux/slices/authSlice'
import {
  LayoutDashboard, Users, HeartPulse, FileText,
  Stethoscope, CalendarCheck, MapPin, MessageSquare, Bell,
  CreditCard, Star, Brain, LogOut, ChevronDown, ChevronRight, Route, UserCircle
} from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { label: 'Dashboard', to: '/family/dashboard', icon: LayoutDashboard },
  { label: 'Family Profile', to: '/family/profile', icon: UserCircle },
  {
    label: 'People', icon: Users, children: [
      { label: 'Patients', to: '/family/patients', icon: Stethoscope },
      { label: 'Emergency Contacts', to: '/family/emergency-contacts', icon: HeartPulse },
    ],
  },
  {
    label: 'Care', icon: HeartPulse, children: [
      { label: 'Care Services', to: '/family/services', icon: Stethoscope },
      { label: 'Medical Records', to: '/family/records', icon: FileText },
      { label: 'New Booking', to: '/family/bookings/new', icon: CalendarCheck },
      { label: 'Bookings History', to: '/family/bookings', icon: CalendarCheck },
      { label: 'Care Journey', to: '/family/journeys', icon: Route },
    ],
  },
  { label: 'Messages', to: '/family/communication', icon: MessageSquare },
  { label: 'Notifications', to: '/family/notifications', icon: Bell },
  { label: 'Payments', to: '/family/payments', icon: CreditCard },
  { label: 'Reviews', to: '/family/reviews', icon: Star },
  { label: 'AI Insights', to: '/family/ai', icon: Brain },
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
          isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
        }`
      }
      style={{ paddingLeft: `${depth * 1.5 + 0.75}rem` }}
    >
      <Icon size={18} className="text-gray-400" />
      {item.label}
    </NavLink>
  )
}

export default function FamilySidebar({ onClose }) {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { user } = useSelector((s) => s.auth)

  const handleLogout = () => {
    dispatch(logoutUser())
    navigate('/login')
  }

  const getImageUrl = (url) => {
    if (!url) return ''
    if (url.startsWith('http')) return url
    return `http://127.0.0.1:8000${url}`
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-full shadow-sm">
      <div className="h-16 flex items-center px-6 border-b border-gray-100 shrink-0">
        <HeartPulse className="text-blue-600 mr-2" size={24} />
        <span className="text-xl font-bold text-gray-900 tracking-tight">CareBridge</span>
      </div>

      <div className="p-4 border-b border-gray-100 flex items-center gap-3 shrink-0">
        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold overflow-hidden">
          {user?.profile_picture ? (
            <img src={getImageUrl(user?.profile_picture)} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            user?.first_name?.[0] || 'F'
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="text-xs text-blue-600 font-medium">FAMILY</p>
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
