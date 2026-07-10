import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import familyReducer from './slices/familySlice'
import userReducer from './slices/userSlice'
import patientReducer from './slices/patientSlice'
import medicalRecordsReducer from './slices/medicalRecordsSlice'
import careJourneyReducer from './slices/careJourneySlice'
import companionsReducer from './slices/companionsSlice'
import servicesReducer from './slices/servicesSlice'
import bookingsReducer from './slices/bookingsSlice'
import trackingReducer from './slices/trackingSlice'
import communicationReducer from './slices/communicationSlice'
import notificationsReducer from './slices/notificationsSlice'
import paymentsReducer from './slices/paymentsSlice'
import reviewsReducer from './slices/reviewsSlice'
import dashboardReducer from './slices/dashboardSlice'
import supportReducer from './slices/supportSlice'
import verificationReducer from './slices/verificationSlice'
import aiReducer from './slices/aiSlice'
import analyticsReducer from './slices/analyticsSlice'
import gatewayReducer from './slices/gatewaySlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    family: familyReducer,
    user: userReducer,
    patient: patientReducer,
    medicalRecords: medicalRecordsReducer,
    careJourney: careJourneyReducer,
    companions: companionsReducer,
    services: servicesReducer,
    bookings: bookingsReducer,
    tracking: trackingReducer,
    communication: communicationReducer,
    notifications: notificationsReducer,
    payments: paymentsReducer,
    reviews: reviewsReducer,
    dashboard: dashboardReducer,
    support: supportReducer,
    verification: verificationReducer,
    ai: aiReducer,
    analytics: analyticsReducer,
    gateway: gatewayReducer,
  },
})
