from datetime import date

import customtkinter as ctk

from colors import Colors
from gui.events.event_detail_page import EventDetailPage
from gui.mentorship.dialogs import MentorshipChatDialog, RequestDetailsDialog
from .base_dashboard import BaseDashboard


class JuniorDashboard(BaseDashboard):
    """Junior Student အတွက် Dashboard"""

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
        self.render_dashboard_notice(self.main_frame, "Junior Dashboard", f"The dashboard is running in safe mode while the page rebuilds itself. Details: {error}")

    def setup_ui(self):
        self.main_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_header(self.main_frame)
        self.create_header_actions(self.main_frame, [{"text": "↻ Refresh", "command": self.load_data}])

        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        left = ctk.CTkFrame(content_frame, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        _, self.requests_frame = self.create_section_box(left, "Outgoing Requests (Mentee)", pady=(0, 20))
        _, self.mentors_frame = self.create_section_box(left, "My Mentors", expand=True)

        right = ctk.CTkFrame(content_frame, fg_color="transparent", width=360)
        right.pack(side="right", fill="both", padx=(10, 0))
        right.pack_propagate(False)
        self.create_calendar(right)
        _, self.events_frame = self.create_section_box(right, "Recommended Upcoming Events", expand=False, pady=(0, 0))

    def open_request(self, req):
        RequestDetailsDialog(self.parent, self.user, self.db, req, on_updated=self.load_data)

    def open_chat(self, req):
        MentorshipChatDialog(self.parent, self.user, self.db, req, on_updated=self.load_data)

    def open_event(self, event):
        EventDetailPage(self.parent, self.user, self.db, event, on_updated=self.load_data)

    def load_data(self):
        try:
            requests = self.db.get_mentorship_requests(self.user['user_id'], 'mentee') or []
            upcoming_events = self.db.get_events({'start_date': date.today()}) or []

            self.clear_frame(self.requests_frame)
            if requests:
                for req in requests[:5]:
                    status = (req.get('status') or '').lower()
                    actions = [{'text': 'View', 'command': lambda r=req: self.open_request(r)}]
                    if status in {'accepted', 'completed'}:
                        actions.insert(0, {'text': 'Chat', 'command': lambda r=req: self.open_chat(r)})
                    self.create_action_card(
                        self.requests_frame,
                        '📨',
                        req.get('subject', 'Mentorship Request'),
                        f"Mentor: {req.get('other_name', 'Unknown')}",
                        status.title() if status else 'Unknown',
                        self.get_status_color(status),
                        actions,
                    )
            else:
                self.show_empty_state(self.requests_frame, "You have not sent any mentorship request yet.")

            self.clear_frame(self.mentors_frame)
            accepted_requests = [req for req in requests if (req.get('status') or '').lower() == 'accepted']
            if accepted_requests:
                for req in accepted_requests[:5]:
                    secondary = req.get('message') or req.get('other_major') or req.get('other_dept') or 'Accepted mentorship connection'
                    self.create_action_card(
                        self.mentors_frame,
                        '👨‍🏫',
                        req.get('other_name', 'Unknown'),
                        f"{req.get('subject', 'Mentorship')} • {secondary}",
                        'Active',
                        self.get_status_color('accepted'),
                        [
                            {'text': 'Chat', 'command': lambda r=req: self.open_chat(r)},
                            {'text': 'View', 'command': lambda r=req: self.open_request(r)},
                        ],
                    )
            else:
                self.show_empty_state(self.mentors_frame, "No mentor has accepted your request yet.")

            self.clear_frame(self.events_frame)
            visible_events = [event for event in upcoming_events if (event.get('status') or '').lower() == 'upcoming']
            if visible_events:
                for event in visible_events[:4]:
                    registration = self.db.get_event_registration_status(event['event_id'], self.user['user_id']) or {}
                    event_status = 'Joined' if registration.get('status') in ('registered', 'attended') else 'Upcoming'
                    color = Colors.SUCCESS if event_status == 'Joined' else self.get_status_color('completed')
                    details = f"{self.format_date(event.get('start_date'))} • {event.get('mode', 'online').title()} • {event.get('registered_count', 0)} joined"
                    self.create_action_card(
                        self.events_frame,
                        '📅',
                        event.get('title', 'Event'),
                        details,
                        event_status,
                        color,
                        [{'text': 'Details', 'command': lambda e=event: self.open_event(e)}],
                    )
            else:
                self.show_empty_state(self.events_frame, "No upcoming events have been created yet.")

            self.db.log_activity(self.user['user_id'], 'view_dashboard', 'Viewed junior dashboard')
        except Exception as e:
            self.handle_section_error(f"Unable to load dashboard data right now. Details: {e}")
