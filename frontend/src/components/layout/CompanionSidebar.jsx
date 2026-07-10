import { NavLink, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logoutUser } from '../../redux/slices/authSlice'
import {
  LayoutDashboard, UserCircle, Bell, Clock,
  MapPin, MessageSquare, CreditCard, Star, CheckCircle, ShieldCheck,
  LogOut, ChevronDown, ChevronRight, Route
} from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { label: 'Dashboard', to: '/companion/dashboard', icon: LayoutDashboard },
  { label: 'My Profile', to: '/companion/profile', icon: UserCircle },
  {
    label: 'Trip Requests', icon: Bell, children: [
      { label: 'Pending Requests', to: '/companion/requests/pending', icon: Clock },
      { label: 'Accepted Trips', to: '/companion/requests/accepted', icon: CheckCircle },
      { label: 'Today\'s Trips', to: '/companion/requests/today', icon: MapPin },
    ],
  },
  {
    label: 'Active Journey', icon: Route, children: [
      { label: 'Journey Workflow', to: '/companion/journey', icon: Route },
    ],
  },
  { label: 'Messages', to: '/companion/communication', icon: MessageSquare },
  { label: 'Notifications', to: '/companion/notifications', icon: Bell },
  { label: 'Earnings', to: '/companion/earnings', icon: CreditCard },
  { label: 'Trip History', to: '/companion/history', icon: Clock },
  { label: 'Ratings & Reviews', to: '/companion/reviews', icon: Star },
  { label: 'Verification Status', to: '/companion/verification', icon: ShieldCheck },
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
          isActive ? 'bg-green-50 text-green-700' : 'text-gray-700 hover:bg-gray-100'
        }`
      }
      style={{ paddingLeft: `${depth * 1.5 + 0.75}rem` }}
    >
      <Icon size={18} className="text-gray-400" />
      {item.label}
    </NavLink>
  )
}

export default function CompanionSidebar({ onClose }) {
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
        <MapPin className="text-green-600 mr-2" size={24} />
        <span className="text-xl font-bold text-gray-900 tracking-tight">CareBridge</span>
      </div>

      <div className="p-4 border-b border-gray-100 flex items-center gap-3 shrink-0">
        {user?.profile_picture ? (
          <img src={getImageUrl(user.profile_picture)} alt="" className="w-10 h-10 rounded-full object-cover" />
        ) : (
          <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold">
            {user?.first_name?.[0] || 'C'}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-900 truncate">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="text-xs text-green-600 font-medium">COMPANION</p>
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
