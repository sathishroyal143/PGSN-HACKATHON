import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { useEffect } from 'react'

import { fetchCurrentUser } from './redux/slices/authSlice'
import IncomingCallModal from './components/communication/IncomingCallModal'
import ActiveCallModal from './components/communication/ActiveCallModal'

// Layouts
import FamilyLayout from './layouts/FamilyLayout'
import CompanionLayout from './layouts/CompanionLayout'
import AdminLayout from './layouts/AdminLayout'

// Dashboards
import FamilyDashboardPage from './pages/dashboard/FamilyDashboardPage'
import CompanionDashboardPage from './pages/dashboard/CompanionDashboardPage'
import AdminDashboardPage from './pages/dashboard/AdminDashboardPage'

// Auth pages
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import OTPVerificationPage from './pages/auth/OTPVerificationPage'
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage'

// User pages
import ProfilePage from './pages/user/ProfilePage'
import EditProfilePage from './pages/user/EditProfilePage'

// Family pages
import FamilyProfilePage from './pages/family/FamilyProfilePage'
import FamilyMembersPage from './pages/family/FamilyMembersPage'
import EmergencyContactsPage from './pages/family/EmergencyContactsPage'

// Patient pages
import PatientsPage from './pages/patient/PatientsPage'
import PatientDetailPage from './pages/patient/PatientDetailPage'

// Medical Records pages
import MedicalRecordsHubPage from './pages/medical/MedicalRecordsHubPage'
import MedicalRecordsPage from './pages/medical/MedicalRecordsPage'
import MedicalRecordDetailPage from './pages/medical/MedicalRecordDetailPage'

// Care Journey pages
import JourneyPage from './pages/journey/JourneyPage'
import JourneyDetailPage from './pages/journey/JourneyDetailPage'

// Companion pages
import CompanionsPage from './pages/companions/CompanionsPage'
import CompanionDetailPage from './pages/companions/CompanionDetailPage'

// Services pages
import ServicesPage from './pages/services/ServicesPage'
import ServiceDetailPage from './pages/services/ServiceDetailPage'

// Bookings pages
import BookingsPage from './pages/bookings/BookingsPage'
import BookingDetailPage from './pages/bookings/BookingDetailPage'
import BookingCreatePage from './pages/bookings/BookingCreatePage'
import CompanionRequestsPage from './pages/bookings/CompanionRequestsPage'

// Tracking pages
import TrackingPage from './pages/tracking/TrackingPage'
import TrackingDetailPage from './pages/tracking/TrackingDetailPage'

// Communication pages
import ConversationListPage from './pages/communication/ConversationListPage'
import ChatPage from './pages/communication/ChatPage'

// Notifications pages
import NotificationsPage from './pages/notifications/NotificationsPage'
import NotificationPreferencesPage from './pages/notifications/NotificationPreferencesPage'

// Payments pages
import PaymentsPage from './pages/payments/PaymentsPage'
import InvoicePage from './pages/payments/InvoicePage'

// Reviews pages
import ReviewsPage from './pages/reviews/ReviewsPage'

// Support pages
import SupportPage from './pages/support/SupportPage'
import TicketDetailPage from './pages/support/TicketDetailPage'

// Verification page
import VerificationPage from './pages/verification/VerificationPage'

// AI / Analytics
import AIPage from './pages/ai/AIPage'
import AnalyticsPage from './pages/analytics/AnalyticsPage'
import APIGatewayPage from './pages/gateway/APIGatewayPage'

function RequireAuth({ children, role }) {
  const { isAuthenticated, user } = useSelector((s) => s.auth)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (role && user?.role && user.role !== role) {
    if (user.role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />
    if (user.role === 'COMPANION') return <Navigate to="/companion/dashboard" replace />
    return <Navigate to="/family/dashboard" replace />
  }
  return children
}

function GuestOnly({ children }) {
  const { isAuthenticated, user } = useSelector((s) => s.auth)
  if (isAuthenticated && user) {
    if (user.role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />
    if (user.role === 'COMPANION') return <Navigate to="/companion/dashboard" replace />
    return <Navigate to="/family/dashboard" replace />
  }
  return children
}

function AppContent() {
  return (
    <Routes>
      {/* Guest-only routes */}
      <Route path="/login" element={<GuestOnly><LoginPage /></GuestOnly>} />
      <Route path="/register" element={<GuestOnly><RegisterPage /></GuestOnly>} />
      <Route path="/forgot-password" element={<GuestOnly><ForgotPasswordPage /></GuestOnly>} />
      <Route path="/verify-otp" element={<OTPVerificationPage />} />

      {/* ----------------- FAMILY DASHBOARD ----------------- */}
      <Route path="/family" element={<RequireAuth><FamilyLayout /></RequireAuth>}>
        <Route path="dashboard" element={<FamilyDashboardPage />} />
        
        {/* People */}
        <Route path="profile" element={<FamilyProfilePage />} />
        <Route path="members" element={<FamilyMembersPage />} />
        <Route path="patients" element={<PatientsPage />} />
        <Route path="patients/:id" element={<PatientDetailPage />} />
        <Route path="emergency-contacts" element={<EmergencyContactsPage />} />

        {/* Care */}
        <Route path="records" element={<MedicalRecordsHubPage />} />
        <Route path="patients/:patientId/records" element={<MedicalRecordsPage />} />
        <Route path="bookings" element={<BookingsPage />} />
        <Route path="bookings/new" element={<BookingCreatePage />} />
        <Route path="bookings/:id" element={<BookingDetailPage />} />
        <Route path="services" element={<ServicesPage />} />
        <Route path="services/:id" element={<ServiceDetailPage />} />
        <Route path="tracking" element={<TrackingPage />} />
        <Route path="tracking/:id" element={<TrackingDetailPage />} />
        <Route path="journeys" element={<JourneyPage />} />
        <Route path="journeys/:id" element={<JourneyDetailPage />} />
        <Route path="companions/:id" element={<CompanionDetailPage />} />

        {/* Communication */}
        <Route path="communication" element={<ConversationListPage />} />
        <Route path="communication/:id" element={<ChatPage />} />
        <Route path="notifications" element={<NotificationsPage />} />

        {/* Finance */}
        <Route path="payments" element={<PaymentsPage />} />
        <Route path="reviews" element={<ReviewsPage />} />
        <Route path="ai" element={<AIPage />} />
      </Route>

      {/* ----------------- COMPANION DASHBOARD ----------------- */}
      <Route path="/companion" element={<RequireAuth role="COMPANION"><CompanionLayout /></RequireAuth>}>
        <Route path="dashboard" element={<CompanionDashboardPage />} />
        
        <Route path="profile" element={<ProfilePage />} />
        <Route path="profile/edit" element={<EditProfilePage />} />
        
        <Route path="requests/pending" element={<CompanionRequestsPage />} />
        <Route path="requests/accepted" element={<BookingsPage />} />
        <Route path="requests/today" element={<BookingsPage />} />
        <Route path="bookings/:id" element={<BookingDetailPage />} />
        
        <Route path="journey" element={<JourneyPage />} />
        <Route path="journey/:id" element={<JourneyDetailPage />} />
        
        <Route path="communication" element={<ConversationListPage />} />
        <Route path="communication/:id" element={<ChatPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        
        <Route path="earnings" element={<PaymentsPage />} />
        <Route path="history" element={<BookingsPage />} />
        <Route path="reviews" element={<ReviewsPage />} />
        <Route path="verification" element={<VerificationPage />} />
      </Route>

      {/* ----------------- ADMIN DASHBOARD ----------------- */}
      <Route path="/admin" element={<RequireAuth role="ADMIN"><AdminLayout /></RequireAuth>}>
        <Route path="dashboard" element={<AdminDashboardPage />} />
        
        <Route path="families" element={<FamilyMembersPage />} />
        <Route path="patients" element={<PatientsPage />} />
        <Route path="patients/:id" element={<PatientDetailPage />} />
        <Route path="companions" element={<CompanionsPage />} />
        <Route path="companions/:id" element={<CompanionDetailPage />} />
        <Route path="verification" element={<VerificationPage />} />
        
        <Route path="services" element={<ServicesPage />} />
        <Route path="services/:id" element={<ServiceDetailPage />} />
        
        <Route path="bookings" element={<BookingsPage />} />
        <Route path="bookings/:id" element={<BookingDetailPage />} />
        
        <Route path="tracking/:id" element={<TrackingDetailPage />} />
        <Route path="journeys/:id" element={<JourneyDetailPage />} />
        
        <Route path="payments" element={<PaymentsPage />} />
        
        <Route path="support" element={<SupportPage />} />
        <Route path="support/tickets/:ticketId" element={<TicketDetailPage />} />
        <Route path="complaints" element={<SupportPage />} />
        <Route path="reviews" element={<ReviewsPage />} />
        
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="ai" element={<AIPage />} />
        <Route path="api-gateway" element={<APIGatewayPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="settings" element={<NotificationPreferencesPage />} />
      </Route>

      {/* Fallback */}
      <Route path="/" element={<GuestOnly><Navigate to="/login" replace /></GuestOnly>} />
      <Route path="/dashboard" element={<GuestOnly><Navigate to="/login" replace /></GuestOnly>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  const dispatch = useDispatch()
  const { isAuthenticated, user } = useSelector((s) => s.auth)

  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(fetchCurrentUser())
    }
  }, [isAuthenticated, user, dispatch])

  // Don't render AppContent if we are authenticated but waiting for user data
  if (isAuthenticated && !user) {
    return <div className="flex h-screen w-screen items-center justify-center bg-gray-50"><div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div></div>
  }

  return (
    <>
      <AppContent />
      <IncomingCallModal />
      <ActiveCallModal />
    </>
  )
}
