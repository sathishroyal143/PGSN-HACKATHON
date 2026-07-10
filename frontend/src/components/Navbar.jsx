import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import { Bell, Menu, Settings } from 'lucide-react'
import { useEffect } from 'react'
import { fetchNotifications } from '../redux/slices/notificationsSlice'

const ROUTE_LABELS = {
  '/family/dashboard': 'Dashboard',
  '/companion/dashboard': 'Dashboard',
  '/admin/dashboard': 'Dashboard',
  '/profile': 'My Profile',
  '/profile/edit': 'Edit Profile',
  '/family/profile': 'Family Profile',
  '/family/members': 'Family Members',
  '/family/emergency-contacts': 'Emergency Contacts',
  '/family/patients': 'Patients',
  '/family/records': 'Medical Records',
  '/family/bookings': 'Bookings',
  '/family/tracking': 'Journey Tracking',
  '/communication': 'Messages',
  '/notifications': 'Notifications',
  '/notifications/preferences': 'Notification Preferences',
  '/payments': 'Payments',
  '/reviews': 'Reviews',
  '/support': 'Support',
  '/verification': 'Verification',
  '/ai': 'AI Engine',
  '/analytics': 'Analytics',
  '/api-gateway': 'API Gateway',
}

export default function Navbar({ onMenuClick }) {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  const unreadCount = useSelector((s) => s.notifications.unreadCount)

  useEffect(() => { dispatch(fetchNotifications()) }, [dispatch])

  // Try to find a nice title matching the route
  const path = location.pathname
  let label = 'CareBridge'
  for (const [route, name] of Object.entries(ROUTE_LABELS)) {
    if (path.startsWith(route)) label = name
  }

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center px-4 gap-3 shrink-0">
      <button
        onClick={onMenuClick}
        className="lg:hidden text-gray-500 hover:text-gray-700"
      >
        <Menu size={20} />
      </button>

      <h2 className="text-base font-semibold text-gray-800 flex-1 truncate">{label}</h2>

      {/* Notifications */}
      <button
        onClick={() => {
          const basePath = location.pathname.startsWith('/admin') ? '/admin' 
                         : location.pathname.startsWith('/companion') ? '/companion' 
                         : '/family';
          navigate(`${basePath}/notifications`);
        }}
        className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors shrink-0"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Settings */}
      <button
        onClick={() => {
          const basePath = location.pathname.startsWith('/admin') ? '/admin' 
                         : location.pathname.startsWith('/companion') ? '/companion' 
                         : '/family';
          navigate(location.pathname.startsWith('/admin') ? '/admin/settings' : `${basePath}/profile`);
        }}
        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors shrink-0"
      >
        <Settings size={18} />
      </button>
    </header>
  )
}
