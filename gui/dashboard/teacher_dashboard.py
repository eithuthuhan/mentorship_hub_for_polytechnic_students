import customtkinter as ctk

from colors import Colors
from gui.events.event_detail_page import EventDetailPage
from gui.mentorship.dialogs import MentorshipChatDialog, RequestDetailsDialog, ScheduleSessionDialog
from gui.ui_helpers import ask_confirm, show_error, show_success
from .base_dashboard import BaseDashboard


class TeacherDashboard(BaseDashboard):
    """Teacher အတွက် Dashboard"""

    def __init__(self, parent, user, db):
        super().__init__(parent, user, db)
        try:
            self.setup_ui()
            self.load_data()
        except Exception as error:
            self._render_safe_fallback(error)



    def _render_safe_fallback(self, error):
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.main_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.create_header(self.main_frame)
        self.render_dashboard_notice(self.main_frame, "Teacher Dashboard", f"The dashboard is running in safe mode while the page rebuilds itself. Details: {error}")

    def setup_ui(self):
        self.main_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_header(self.main_frame)
        self.create_header_actions(self.main_frame, [{"text": "↻ Refresh", "command": self.load_data}])

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        _, self.requests_frame = self.create_section_box(left, "Incoming Requests (Mentor)")
        _, self.students_frame = self.create_section_box(left, "My Mentees")

        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        _, self.events_frame = self.create_section_box(right, "My Created Events")
        self.create_calendar(right)
        _, self.stats_frame = self.create_section_box(right, "Department Statistics", pady=(0, 0))

    def _accept_request(self, req):
        if not ask_confirm("Accept this mentorship request?"):
            return
        if self.db.update_request_status(req['request_id'], 'accepted', self.user['user_id']):
            show_success("Request accepted!")
            self.load_data()
        else:
            show_error("Unable to accept the request.")

    def _reject_request(self, req):
        if not ask_confirm("Reject this mentorship request?"):
            return
        if self.db.update_request_status(req['request_id'], 'rejected', self.user['user_id']):
            show_success("Request rejected.")
            self.load_data()
        else:
            show_error("Unable to reject the request.")

    def _open_chat(self, req):
        MentorshipChatDialog(self.parent, self.user, self.db, req, on_updated=self.load_data)

    def _open_schedule(self, req):
        ScheduleSessionDialog(self.parent, self.user, self.db, req, on_saved=self.load_data)

    def _open_request(self, req):
        RequestDetailsDialog(self.parent, self.user, self.db, req, on_updated=self.load_data)

    def _open_event(self, event):
        EventDetailPage(self.parent, self.user, self.db, event, on_updated=self.load_data)

    def load_data(self):
        try:
            mentor_requests = self.db.get_mentorship_requests(self.user['user_id'], 'mentor') or []
            active_students = [req for req in mentor_requests if (req.get('status') or '').lower() == 'accepted']
            my_events = self.db.get_user_created_events(self.user['user_id']) or []
            department_students = self.db.get_all_users(role='junior_student', department=self.user.get('department')) or []

            for frame in (self.requests_frame, self.students_frame, self.events_frame, self.stats_frame):
                self.clear_frame(frame)

            if mentor_requests:
                for req in mentor_requests[:5]:
                    status = (req.get('status') or 'unknown').lower()
                    actions = [{'text': 'View', 'command': lambda r=req: self._open_request(r)}]
                    if status == 'pending':
                        actions = [
                            {'text': 'Accept', 'command': lambda r=req: self._accept_request(r)},
                            {'text': 'Reject', 'fg_color': Colors.DANGER, 'command': lambda r=req: self._reject_request(r)},
                        ]
                    elif status in {'accepted', 'completed'}:
                        actions.insert(0, {'text': 'Chat', 'command': lambda r=req: self._open_chat(r)})
                    self.create_action_card(
                        self.requests_frame,
                        '📥',
                        req.get('subject', 'Mentorship'),
                        f"From: {req.get('other_name', 'Unknown')}",
                        status.title(),
                        self.get_status_color(status),
                        actions,
                    )
            else:
                self.show_empty_state(self.requests_frame, 'No mentorship requests yet.')

            if active_students:
                for req in active_students[:5]:
                    secondary = req.get('message') or req.get('other_major') or req.get('other_dept') or 'Accepted mentorship connection'
                    self.create_action_card(
                        self.students_frame,
                        '🧑‍🎓',
                        req.get('other_name', 'Unknown'),
                        f"{req.get('subject', 'Mentorship')} • {secondary}",
                        'Active',
                        self.get_status_color('accepted'),
                        [
                            {'text': 'Chat', 'command': lambda r=req: self._open_chat(r)},
                            {'text': 'Schedule', 'command': lambda r=req: self._open_schedule(r)},
                            {'text': 'View', 'command': lambda r=req: self._open_request(r)},
                        ],
                    )
            else:
                self.show_empty_state(self.students_frame, 'No active mentees yet.')

            if my_events:
                for event in my_events[:5]:
                    secondary = f"{self.format_date(event.get('start_date'))} • {event.get('registered_count', 0)} registered"
                    self.create_action_card(
                        self.events_frame,
                        '📅',
                        event.get('title', 'Event'),
                        secondary,
                        (event.get('status') or 'upcoming').title(),
                        self.get_status_color(event.get('status')),
                        [{'text': 'Details', 'command': lambda e=event: self._open_event(e)}],
                    )
            else:
                self.show_empty_state(self.events_frame, 'No created events yet.')

            upcoming_events = [event for event in my_events if (event.get('status') or '').lower() == 'upcoming']
            self.create_metric_row(self.stats_frame, 'Department', self.user.get('department') or 'N/A')
            self.create_metric_row(self.stats_frame, 'Junior Students', len(department_students))
            self.create_metric_row(self.stats_frame, 'Active Mentees', len(active_students))
            self.create_metric_row(self.stats_frame, 'Created Events', len(my_events))
            self.create_metric_row(self.stats_frame, 'Upcoming Events', len(upcoming_events))

            self.db.log_activity(self.user['user_id'], 'view_dashboard', 'Viewed teacher dashboard')
        except Exception as e:
            self.handle_section_error(f"Unable to load dashboard data right now. Details: {e}")
