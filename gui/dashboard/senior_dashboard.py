import customtkinter as ctk

from colors import Colors
from gui.events.event_detail_page import EventDetailPage
from gui.mentorship.dialogs import (
    MentorshipChatDialog,
    MentorshipReviewDialog,
    RequestDetailsDialog,
    ScheduleSessionDialog,
)
from gui.ui_helpers import ask_confirm, show_error, show_success
from .base_dashboard import BaseDashboard


class SeniorDashboard(BaseDashboard):
    """Senior Student အတွက် Dashboard"""

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
        self.render_dashboard_notice(self.main_frame, "Senior Dashboard", f"The dashboard is running in safe mode while the page rebuilds itself. Details: {error}")

    def setup_ui(self):
        self.main_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_header(self.main_frame)
        self.create_header_actions(self.main_frame, [{"text": "↻ Refresh", "command": self.load_data}])

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(left, text="👨‍🏫 Mentor Side", font=("Arial", 20, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w", pady=(0, 10))
        _, self.incoming_frame = self.create_section_box(left, "Incoming Requests (Mentor)", title_size=16)
        _, self.mentees_frame = self.create_section_box(left, "My Mentees", title_size=16)
        _, self.events_frame = self.create_section_box(left, "My Created Events", title_size=16)

        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        ctk.CTkLabel(right, text="👨‍🎓 Mentee Side", font=("Arial", 20, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w", pady=(0, 10))
        _, self.outgoing_frame = self.create_section_box(right, "Outgoing Requests (Mentee)", title_size=16)
        _, self.mentors_frame = self.create_section_box(right, "My Mentors", title_size=16)
        self.create_calendar(right)

    def _clear_frames(self):
        for frame in (self.incoming_frame, self.mentees_frame, self.events_frame, self.outgoing_frame, self.mentors_frame):
            self.clear_frame(frame)

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

    def _open_review(self, req, is_mentor_rating):
        MentorshipReviewDialog(self.parent, self.user, self.db, req, is_mentor_rating, on_saved=self.load_data)

    def _open_schedule(self, req):
        ScheduleSessionDialog(self.parent, self.user, self.db, req, on_saved=self.load_data)

    def _open_request(self, req):
        RequestDetailsDialog(self.parent, self.user, self.db, req, on_updated=self.load_data)

    def _open_event(self, event):
        EventDetailPage(self.parent, self.user, self.db, event, on_updated=self.load_data)

    def load_data(self):
        try:
            self._clear_frames()
            mentor_requests = self.db.get_mentorship_requests(self.user['user_id'], 'mentor') or []
            mentee_requests = self.db.get_mentorship_requests(self.user['user_id'], 'mentee') or []
            my_events = self.db.get_user_created_events(self.user['user_id']) or []

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
                        self.incoming_frame,
                        '📥',
                        req.get('subject', 'Mentorship'),
                        f"From: {req.get('other_name', 'Unknown')}",
                        status.title(),
                        self.get_status_color(status),
                        actions,
                    )
            else:
                self.show_empty_state(self.incoming_frame, 'No incoming mentorship requests yet.')

            accepted_mentees = [req for req in mentor_requests if (req.get('status') or '').lower() == 'accepted']
            if accepted_mentees:
                for req in accepted_mentees[:5]:
                    secondary = req.get('message') or req.get('other_major') or req.get('other_dept') or 'Active mentorship connection'
                    self.create_action_card(
                        self.mentees_frame,
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
                self.show_empty_state(self.mentees_frame, 'No active mentees yet.')

            if my_events:
                for event in my_events[:5]:
                    event_status = (event.get('status') or 'upcoming').title()
                    secondary = f"{self.format_date(event.get('start_date'))} • {event.get('registered_count', 0)} participants"
                    self.create_action_card(
                        self.events_frame,
                        '📅',
                        event.get('title', 'Event'),
                        secondary,
                        event_status,
                        self.get_status_color(event.get('status')),
                        [{'text': 'Details', 'command': lambda e=event: self._open_event(e)}],
                    )
            else:
                self.show_empty_state(self.events_frame, 'No events created yet.')

            if mentee_requests:
                for req in mentee_requests[:5]:
                    status = (req.get('status') or 'unknown').lower()
                    actions = [{'text': 'View', 'command': lambda r=req: self._open_request(r)}]
                    if status in {'accepted', 'completed'}:
                        actions.insert(0, {'text': 'Chat', 'command': lambda r=req: self._open_chat(r)})
                    if status == 'completed':
                        actions.insert(1, {'text': 'Review', 'command': lambda r=req: self._open_review(r, False)})
                    self.create_action_card(
                        self.outgoing_frame,
                        '📨',
                        req.get('subject', 'Mentorship'),
                        f"Mentor: {req.get('other_name', 'Unknown')}",
                        status.title(),
                        self.get_status_color(status),
                        actions,
                    )
            else:
                self.show_empty_state(self.outgoing_frame, 'No outgoing requests yet.')

            accepted_mentors = [req for req in mentee_requests if (req.get('status') or '').lower() == 'accepted']
            if accepted_mentors:
                for req in accepted_mentors[:5]:
                    secondary = req.get('message') or req.get('other_major') or req.get('other_dept') or 'Accepted mentorship connection'
                    self.create_action_card(
                        self.mentors_frame,
                        '👨‍🏫',
                        req.get('other_name', 'Unknown'),
                        f"{req.get('subject', 'Mentorship')} • {secondary}",
                        'Active',
                        self.get_status_color('accepted'),
                        [
                            {'text': 'Chat', 'command': lambda r=req: self._open_chat(r)},
                            {'text': 'View', 'command': lambda r=req: self._open_request(r)},
                        ],
                    )
            else:
                self.show_empty_state(self.mentors_frame, 'No mentors assigned yet.')

            self.db.log_activity(self.user['user_id'], 'view_dashboard', 'Viewed senior dashboard')
        except Exception as e:
            self.handle_section_error(f"Unable to load dashboard data right now. Details: {e}")
