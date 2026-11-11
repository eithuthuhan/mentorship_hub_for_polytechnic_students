# Cleanup Notes

## Cleanup pass completed

### Removed
- `__pycache__/` folders and `.pyc` files
- `ai_feedback.py` (AI feedback module removed from project)
- `auth.py` (old duplicate login/auth flow)
- `app.py` (empty legacy file)

### Updated
- `.gitignore` added
- `requirements.txt` normalized
- `main.py` cleaned up
- `config.py` now supports `MENTORSHIP_DB_PASSWORD` from environment variables
- `databasetable.sql` no longer includes AI feedback/recommendation schema or AI feature seed announcement

### Remaining cleanup candidates
- Normalize package imports inside `gui/` modules
- Replace broad `except:` blocks with specific exceptions
- Move hardcoded sample/demo data out of UI classes

## Additional cleanup pass
- Reused the same `Database()` instance across login and main app to avoid duplicate DB connections.
- Simplified logout flow so the app returns to the login screen without re-importing `main`.
- Replaced several bare `except:` blocks in core navigation files with safer error handling.
- Refactored mentorship stats logic to remove duplicate request-loading code.
- Cleaned `notification.py` to use helper methods for safe database calls and date parsing.

- Removed remaining AI/OpenAI config placeholders from `config.py`
- Removed sample announcement fallback so UI no longer shows fake content when database is empty
- Reworked `gui/mentorship/messages_page.py` to use real mentorship requests/messages instead of demo chat data
- Fixed `gui/dashboard/junior_dashboard.py` to use real request data and removed placeholder external links
- Replaced remaining `AI Seminar` dashboard text with generic `Tech Seminar` label
- Removed default fake meeting/map links in `gui/events/events_page.py`


## Additional cleanup pass 4

- Fixed broken `get_platform_stats()` count logic in `database.py`
- Reworked `admin_dashboard.py` to show real platform statistics instead of hardcoded numbers
- Reworked `teacher_dashboard.py` to show real requests, active students, created events, and department stats
- Reworked `senior_dashboard.py` to show real mentor/mentee requests and created events instead of demo content
- Removed remaining AI-specific sample wording from `databasetable.sql`
- Fixed sample announcement SQL insert syntax in `databasetable.sql`

## Cleanup Pass 5
- Improved `database.py` connection handling by adding a reusable connection check and cursor cleanup in `execute_query()`
- Refactored `get_mentors()` to use the shared query helper instead of a separate raw cursor path
- Added optional `skill` filtering back into mentor search without changing the existing UI structure
- Parameterized JSON filters in `get_announcements()` to avoid string-built SQL fragments
- Normalized `get_resources()` JSON skill filtering to pass valid JSON values
- Tightened `notification.py` safe helper methods so notification errors are easier to trace and windows close more safely


## Cleanup Pass 6
- Centralized repeated dashboard section-box, empty-state, frame-clear, and status-color logic in `gui/dashboard/base_dashboard.py`.
- Refactored `junior_dashboard.py`, `senior_dashboard.py`, `teacher_dashboard.py`, and `admin_dashboard.py` to reuse shared dashboard helpers without changing page layout.
- Replaced several repeated hardcoded dashboard colors with `colors.py` constants for better GUI consistency.
- Updated `gui/main_window.py` to reuse shared color constants while keeping the same project structure and navigation flow.


## Cleanup Pass 7
- Added `gui/ui_helpers.py` for reusable validation and message dialog helpers.
- Cleaned login and register validation flows with better field focus and more consistent messages.
- Improved event creation form validation for date/time/integer inputs and connected it to the real database `create_event()` flow.
- Simplified announcement creation validation using shared helpers.
- Tightened edit profile and settings form validation without changing window layout or project structure.


## Cleanup Pass 8
- Added real mentorship chat popup dialog for accepted requests and active mentorships.
- Added mentorship review dialog with database submission for completed requests.
- Added mentorship session scheduling dialog backed by database sessions.
- Implemented request filtering, detailed request viewer, and removed remaining request placeholder actions.
- Fixed event details import by adding `event_detail_page.py`.
- Implemented event search filtering, real event registration flow, event feedback submission, and certificate readiness handling.
- Expanded `get_user_events()` to include participant feedback/certificate fields.
- Replaced placeholder profile request action with real request dialog flow.

## Runtime bug fixing / feature testing round

- Fixed `gui/events/create_event_page.py` so event creation now uses real validation and the database `create_event()` flow instead of an incomplete placeholder success message.
- Fixed missing `messagebox`-style runtime issues by switching `gui/events/create_event_page.py` and `gui/profile/edit_profile_page.py` to shared UI helper dialogs.
- Added proper email/year validation to `gui/profile/edit_profile_page.py`.
- Replaced the remaining placeholder action in `gui/profile/view_profile_page.py` with a real mentorship request dialog that submits through `create_mentorship_request()`.
- Re-ran `python -m compileall` and a constructor-level smoke test across major GUI pages with dependency stubs to catch runtime initialization errors.


## Runtime Bug Fixing Round 2
- Fixed mentorship message loading to support both mentor-side and mentee-side conversations for senior students.
- Fixed `database.get_messages()` to use the real `messages.created_at` column and expose it as `sent_at` for the existing GUI.
- Improved `get_user_events()` payload with `feedback_submitted` and `certificate_ready` aliases for safer UI checks.
- Updated announcements loading to respect the current user role/department/year filters instead of showing every published announcement.
- Hardened admin dashboard DB health checks so the page does not break when a connection object is missing or mocked in tests.


## Runtime Bug Fixing / Feature Testing Round 3
- Hardened event registration flow to block closed/past/deadline-expired events.
- Allowed safe re-registration after a cancelled event registration.
- Prevented cancellation after an event has already started.
- Added mentorship session scheduling validation for future dates and positive duration.
- Restricted event feedback submission to attended or past events.
- Disabled unavailable event action buttons in the events UI for better empty/edge-state handling.


## Runtime Bug Fixing / Feature Testing Round 4
- Hardened mentorship requests to block self-requests, inactive-user requests, and invalid mentor/mentee role combinations.
- Locked mentorship chat sending to request participants only, and only after a request is accepted or completed.
- Updated mentorship chat UIs to disable message input for pending/rejected requests and show clearer status messaging.
- Restricted mentorship reviews to completed mentorships and prevented duplicate review submissions from the same side.
- Tightened event cancellation, feedback, and certificate actions so no-op or invalid updates no longer appear successful.
- Improved non-select database write handling to use row counts for update/delete safety checks.


## Dashboard DB Action Pass
- Dashboard request buttons now refresh from live database after accept/reject/chat/review/session actions.
- Request details dialog now reads the current request state and can accept/reject/open chat directly.
- Event details dialog now reads the latest event data, shows recent participants, and supports live register/cancel flows.
- Junior, senior, and teacher dashboard cards now open dialogs that push changes back to the dashboard immediately.


## Mentorship live data pass
- Mentorship header stats now use live database summary counts.
- Find Mentors cards now show current relationship status and prevent duplicate request confusion.
- My Requests, Active Mentorships, and Request Details now refresh after live DB actions.
- Messages tab now shows unread counts per request and includes a refresh button.


## Best pass: live events + messaging
- Event search/filter now queries the database directly with search text and status-aware filters.
- My Events now separates created events and registered events, both loaded from real database rows.
- Event details now refresh the parent page after register/cancel actions.
- Create Event now triggers live refresh after successful save.
- Messages page now uses live conversation summaries from the database, auto-refreshes every 4 seconds, and preserves the selected conversation.
- Mentorship chat dialog now auto-refreshes so both users can see up-to-date messages without reopening the dialog.
- Mentorship request loading now supports explicit mentor/mentee context reliably.


## Final packaged build
- Prepared final fresh-database package
- Added FINAL_SETUP.md with sample accounts and setup steps
