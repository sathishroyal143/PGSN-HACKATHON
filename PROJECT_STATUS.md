# Project Status

## Recent Updates - AI Engine Automation & Integration (July 10, 2026)

- **AI Medical Summary Automation**:
  - Replaced manual data entry text fields (Age, Conditions, Medications, Allergies) with a secure "Patient Name" dropdown in the AI Medical Summary tab.
  - Refactored `MedicalSummaryInputSerializer` and `MedicalSummaryService` to automatically fetch full patient medical profiles securely using their `patient_id`.
  - Updated the AI prompt (`medical_summary_prompt`) and the rule-based fallback formatter (`_rule_based_summary`) to dynamically inject and parse comprehensive patient profile data. This includes Demographics (Age, Gender, Blood Group), Mobility & Equipment (Mobility Level, Wheelchair, Oxygen, Stretcher), Medical History (Chronic Conditions, Known Allergies), Care Details (Current Medications, Special Needs, Dietary Restrictions, Emergency Notes), and Recent Encounters (Recent Diagnoses, Recent Prescriptions, Recent Vitals).
- **AI Priority Engine Updates**:
  - Fixed a `select_related('user')` bug in `PriorityService` that caused backend crashes during priority assessment, replacing it with correct `prefetch_related` medical records queries.
  - Added a dynamically calculated `age` property natively to the `Patient` model using `date_of_birth` to enable accurate demographic processing by the Priority Engine.
  - Restructured `PriorityEngine`'s `assess_priority` to intelligently process the same exhaustive patient profile data (Mobility Restrictions, Medical Equipment Needs, Chronic Conditions, and Emergency Notes) instead of basic condition arrays. It dynamically calculates priority scores by detecting mobility keywords (e.g., `BEDRIDDEN` +25 pts), critical equipment dependencies (+25 pts for oxygen), and high-risk chronic condition strings.

## Previous Updates - Companion Workflows & Reviews Enhancements (July 9, 2026)

- **Reviews & Complaints System**:
  - Replaced manual Booking UUID input fields with smart dropdown menus.
  - Enhanced the Bookings dropdown in both Review and Complaint forms to clearly display the Booking Date, Service Name, and Patient Name.
  - Filtered the Complaint forms to strictly restrict submissions to only `COMPLETED` bookings.
  - Removed the raw "status" badge from the complaints list view across both Family and Companion dashboards for a cleaner look.
- **Companion Profile & Metric Updates**:
  - Added a "View Companion" shortcut on the Family's Booking Details page linking to the full Companion Profile.
  - Implemented a backend signal `booking_status_changed` to dynamically update a companion's `total_bookings_completed` counter anytime a trip is completed. Historic records were successfully recalculated.
  - Converted the static "X yrs experience" string into a dynamic duration calculator based on the companion's exact account creation date (`created_at`), intelligently formatting as "X days", "X months", or "X yrs" across all list and detail pages.
- **Companion-Specific Functionality Expansion**:
  - Updated the Backend `ReviewListView` to be role-aware, serving "received reviews" to Companions and "given reviews" to Families over the exact same endpoint.
  - Exposed `family_user_id` on the `BookingListSerializer` to ensure accurate attribution when companions file complaints.
  - Fully enabled Companions to securely read feedback families have left them.
  - **New Feature**: Added an interactive "Reply to Review" capability for Companions to officially respond to family feedback directly within the UI, wired fully to the backend `ReviewReply` model.
  - **New Feature**: Fully enabled the Complaints workflow for Companions, securely routing complaints about completed journeys directly against the relevant Family User.
  - Hid the unnecessary "Live Tracking" feature on the Companion's own Booking Details view.

## Previous Updates - Care Journey Module Implementation (July 8, 2026)

- **Backend Workflows and Models**:
  - Implemented strict state transitions in `CareJourneyService` (`PENDING` → `IN_PROGRESS` → `DONE`).
  - Standardized journey steps: `ACCEPTED`, `ON_THE_WAY`, `REACHED_PATIENT`, `CONSULTATION_STARTED`, `CONSULTATION_ENDED`, `PHARMACY`, `RETURN_HOME`.
  - Added `latitude`, `longitude`, and `family_notified` to `JourneyStep`.
  - Created `JourneyMedia` model to handle uploads (Prescriptions, Bills, etc.).
  - Auto-initialization now starts a Journey at `ACCEPTED` when a Companion accepts a booking.
  - Hooked up `NotificationService` to automatically notify the Family when a Companion advances a step.
- **Frontend Family & Admin Dashboards**:
  - Created the `<ActiveJourneyWidget />` for the Family and Admin Dashboard to surface any active care journey instantly with live tracking cues.
- **Unified Care Journey Tracker (`JourneyDetailPage.jsx`)**:
  - Completely rewrote the Journey Detail page.
  - **Family/Admin View**: Serves as a read-only live tracker with an embedded OpenStreetMap (`react-leaflet`) for location tracking, a visual timeline, and overall progress indicator.
  - **Companion View**: Transforms into an interactive command center, providing "Start Step" and "Mark as Completed" actions, alongside file upload dropdowns and a "Share Location" button. Added the ability for Companions to sync general notes to the Family's view.
- **Dependencies**: Added `react-leaflet@4` and `leaflet` to the frontend dependencies.

## Previous Updates - Companion Dashboard & UI Fixes (July 8, 2026)

- **Companion Journey Page**: Changed the "View Bookings" button to a generic "Back" button that uses browser history to return to the previously active page.
- **Accepted Trips View**:
  - Re-titled the default "My Bookings" page to "Accepted Trips" for Companion users.
  - Removed the "+ New Booking" button from the Companion view to make it completely professional and tailored to their use case.
  - Removed the status filter tabs which are not applicable for the Companion's main booking list.
  - Fixed a routing issue where clicking on an accepted trip incorrectly redirected the Companion to the Family booking view. It now correctly maps to the `BookingDetailPage` component inside the Companion layout, providing a dedicated Patient & Booking details view.
- **Booking Details Page**: Updated the back button behavior to reliably return the Companion to the "Accepted Trips" screen (or the appropriate prior booking screen) instead of triggering a 404.
- **Pending Care Requests**: Added a "Back" button at the top of the `CompanionRequestsPage`.
- **Today's Trips**: Completely refactored the date-filtering logic. "Today's Trips" now accurately filters trips using localized timezone comparisons (IST), covering all date fields (`scheduled_start`, `scheduled_end`, `actual_start`, `actual_end`) and additionally includes any trips with an `IN_PROGRESS` status to ensure actively performed trips always appear.
- **Reviews & Complaints Page**: Removed the "My Bookings" quick-link button.

## Status
✅ **100% COMPLETE** - All requested updates and new features have been fully documented and pushed to the system successfully.
