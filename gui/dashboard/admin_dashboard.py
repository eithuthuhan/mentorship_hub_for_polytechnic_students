import customtkinter as ctk

from colors import Colors
from gui.events.event_detail_page import EventDetailPage
from gui.mentorship.dialogs import RequestDetailsDialog
from gui.profile.view_profile_page import ViewProfilePage
from .base_dashboard import BaseDashboard


class AdminDashboard(BaseDashboard):
    """Admin dashboard with live platform overview and preview actions."""

    def __init__(self, parent, user, db):
        super().__init__(parent, user, db)
        self.total_users_value = None
        self.teachers_value = None
        self.seniors_value = None
        self.juniors_value = None
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
        self.render_dashboard_notice(self.main_frame, "Admin Dashboard", f"The dashboard is running in safe mode while the page rebuilds itself. Details: {error}")
        self.create_stats_cards()
        _, self.mentorship_frame = self.create_section_box(self.main_frame, "Mentorship Overview")
        _, self.events_frame = self.create_section_box(self.main_frame, "Event Overview")
        _, self.system_frame = self.create_section_box(self.main_frame, "System Health")
        _, self.requests_frame = self.create_section_box(self.main_frame, "Latest Mentorship Requests", expand=True)
        _, self.latest_events_frame = self.create_section_box(self.main_frame, "Latest Events")
        _, self.members_frame = self.create_section_box(self.main_frame, "New Members")
        try:
            self.load_data()
        except Exception:
            pass

    def setup_ui(self):
        self.main_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_header(self.main_frame)
        self.create_header_actions(self.main_frame, [{"text": "↻ Refresh", "command": self.load_data}])
        self.create_stats_cards()

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, pady=10)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        _, self.mentorship_frame = self.create_section_box(left, "Mentorship Overview")
        _, self.system_frame = self.create_section_box(left, "System Health", pady=(15, 0))
        _, self.requests_frame = self.create_section_box(left, "Latest Mentorship Requests", expand=True, pady=(15, 0))

        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        _, self.events_frame = self.create_section_box(right, "Event Overview")
        _, self.latest_events_frame = self.create_section_box(right, "Latest Events", pady=(15, 0))
        _, self.members_frame = self.create_section_box(right, "New Members", pady=(15, 0))
        self.create_calendar(right)

    def create_stats_cards(self):
        cards = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards.pack(fill="x", pady=10)
        for i in range(4):
            cards.grid_columnconfigure(i, weight=1)

        self.total_users_value = self.create_stat_card(cards, "TOTAL USERS", "0", Colors.PRIMARY, 0)
        self.teachers_value = self.create_stat_card(cards, "Teachers", "0", Colors.SECONDARY, 1)
        self.seniors_value = self.create_stat_card(cards, "Seniors", "0", Colors.WARNING, 2)
        self.juniors_value = self.create_stat_card(cards, "Juniors", "0", Colors.SUCCESS, 3)

    def create_stat_card(self, parent, title, value, color, col):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=16)
        card.grid(row=0, column=col, padx=6, pady=5, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=("Arial", 12), text_color=Colors.TEXT_LIGHT).pack(pady=(16, 6))
        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 28, "bold"), text_color=Colors.TEXT_LIGHT)
        value_label.pack(pady=(0, 16))
        return value_label

    def load_data(self):
        stats = self.db.get_platform_stats() or {}
        latest_requests = self.db.get_recent_mentorship_requests(limit=5) or []
        latest_events = self.db.get_recent_events(limit=5) or []
        latest_members = self.db.get_recent_users(limit=5) or []

        if self.total_users_value is not None:
            self.total_users_value.configure(text=str(stats.get('total_users', 0)))
            self.teachers_value.configure(text=str(stats.get('teachers', 0)))
            self.seniors_value.configure(text=str(stats.get('senior_students', 0)))
            self.juniors_value.configure(text=str(stats.get('junior_students', 0)))

        self._render_overview(stats)
        self._render_system_health(stats)
        self._render_recent_requests(latest_requests)
        self._render_recent_events(latest_events)
        self._render_recent_members(latest_members)
        self.db.log_activity(self.user['user_id'], 'view_dashboard', 'Viewed admin dashboard')

    def _render_overview(self, stats):
        self.clear_frame(self.mentorship_frame)
        self.create_metric_row(self.mentorship_frame, 'Total Requests', stats.get('total_mentorships', 0))
        self.create_metric_row(self.mentorship_frame, 'Pending Requests', stats.get('pending_mentorships', 0), Colors.WARNING)
        self.create_metric_row(self.mentorship_frame, 'Active Mentorships', stats.get('active_mentorships', 0), Colors.SUCCESS)
        self.create_metric_row(self.mentorship_frame, 'Completed Mentorships', stats.get('completed_mentorships', 0), Colors.PRIMARY)

        self.clear_frame(self.events_frame)
        self.create_metric_row(self.events_frame, 'Total Events', stats.get('total_events', 0))
        self.create_metric_row(self.events_frame, 'Upcoming Events', stats.get('upcoming_events', 0), Colors.SECONDARY)
        self.create_metric_row(self.events_frame, 'Completed Events', stats.get('completed_events', 0), Colors.TEXT_DARK)
        self.create_metric_row(self.events_frame, 'Messages Sent', stats.get('total_messages', 0), Colors.TEXT_DARK)

    def _render_system_health(self, stats):
        connection = getattr(self.db, 'connection', None)
        is_connected = getattr(connection, 'is_connected', None)
        db_ok = bool(connection and (is_connected() if callable(is_connected) else False))

        self.clear_frame(self.system_frame)
        self.create_action_card(
            self.system_frame,
            '🗄️',
            'Database Connection',
            'Database is connected and ready.' if db_ok else 'Database connection is currently unavailable.',
            'Healthy' if db_ok else 'Offline',
            Colors.SUCCESS if db_ok else Colors.DANGER,
        )
        self.create_action_card(
            self.system_frame,
            '👥',
            'Members on Platform',
            f"{stats.get('total_users', 0)} accounts are currently stored in the system.",
        )
        self.create_action_card(
            self.system_frame,
            '📈',
            'Estimated Data Load',
            f"{self._estimate_storage_used(stats)}% of the current sample capacity is being used.",
        )

    def _render_recent_requests(self, requests):
        self.clear_frame(self.requests_frame)
        if not requests:
            self.show_empty_state(self.requests_frame, 'No mentorship requests in the database yet.')
            return
        for request in requests:
            status = (request.get('status') or '').title() or 'Unknown'
            secondary = f"{request.get('mentee_name', 'Unknown')} → {request.get('mentor_name', 'Unknown')} • {self.format_date(request.get('created_at'))}"
            actions = [{'text': 'View', 'command': lambda r=request: self._open_request_details(r)}]
            if (request.get('status') or '').lower() == 'pending':
                actions = [
                    {'text': 'Accept', 'command': lambda r=request: self._update_request_status(r, 'accepted'), 'fg_color': Colors.SUCCESS},
                    {'text': 'Reject', 'command': lambda r=request: self._update_request_status(r, 'rejected'), 'fg_color': Colors.DANGER},
                    {'text': 'View', 'command': lambda r=request: self._open_request_details(r), 'fg_color': Colors.SECONDARY},
                ]
            self.create_action_card(self.requests_frame, '🤝', request.get('subject', 'Mentorship Request'), secondary, status, self.get_status_color(request.get('status')), actions)

    def _render_recent_events(self, events):
        self.clear_frame(self.latest_events_frame)
        if not events:
            self.show_empty_state(self.latest_events_frame, 'No events have been created yet.')
            return
        for event in events:
            venue = event.get('platform') if (event.get('mode') or '').lower() == 'online' else event.get('location')
            secondary = f"By {event.get('organizer_name', 'Unknown')} • {self.format_date(event.get('start_date'))} • {venue or 'Venue not added'}"
            self.create_action_card(self.latest_events_frame, '📅', event.get('title', 'Event'), secondary, (event.get('status') or 'upcoming').title(), self.get_status_color('accepted' if event.get('status') == 'ongoing' else event.get('status')), [{'text': 'Details', 'command': lambda e=event: self._open_event_details(e)}])

    def _render_recent_members(self, members):
        self.clear_frame(self.members_frame)
        if not members:
            self.show_empty_state(self.members_frame, 'No new members have registered yet.')
            return
        for member in members:
            role_text = (member.get('role') or '').replace('_', ' ').title()
            dept = member.get('department') or 'Department not set'
            year = f"Year {member['year']}" if member.get('year') else 'Year not set'
            secondary = f"{role_text} • {dept} • {year}"
            badge_text = 'Active' if member.get('is_active') else 'Inactive'
            self.create_action_card(self.members_frame, '👤', member.get('full_name', 'Member'), secondary, badge_text, Colors.SUCCESS if member.get('is_active') else Colors.DANGER, [{'text': 'Profile', 'command': lambda m=member: self._open_profile(m)}])

    def _open_request_details(self, request):
        RequestDetailsDialog(self.parent, self.user, self.db, request, on_updated=self.load_data)

    def _update_request_status(self, request, status):
        ok = self.db.update_request_status(request['request_id'], status, request.get('mentor_id'))
        if ok:
            self.load_data()

    def _open_event_details(self, event):
        EventDetailPage(self.parent, self.user, self.db, event, on_updated=self.load_data)

    def _open_profile(self, member):
        ViewProfilePage(self.parent, self.user, self.db, member['user_id'])

    def _estimate_storage_used(self, stats):
        total_records = stats.get('total_users', 0) + stats.get('total_mentorships', 0) + stats.get('total_events', 0) + stats.get('total_messages', 0)
        if total_records <= 10:
            return 15
        if total_records <= 50:
            return 35
        if total_records <= 150:
            return 55
        if total_records <= 300:
            return 70
        return 85
