# gui/events/events_page.py
import customtkinter as ctk
import webbrowser
from datetime import datetime

from gui.ui_helpers import ask_confirm, require_text, show_error, show_success


class EventsPage:
    """Live events page with database-backed lists, registration, and organizer views."""

    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        self.events_cache = []
        self.user_event_ids = set()
        self.registered_events = []
        self.created_events = []

        self.setup_ui()
        self.load_events()

    def setup_ui(self):
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="📅 Events", font=("Arial", 28, "bold"), text_color="#1F3B5B").pack(side="left")

        right_actions = ctk.CTkFrame(header, fg_color="transparent")
        right_actions.pack(side="right")
        ctk.CTkButton(right_actions, text="Refresh", width=96, height=40, fg_color="#84B6FF", command=self.load_events).pack(side="right", padx=(8, 0))
        if self.user['role'] in ['teacher', 'senior_student']:
            ctk.CTkButton(right_actions, text="+ Create Event", width=150, height=40, fg_color="#7FC8A9", command=self.open_create_event).pack(side="right")

        self.tabview = ctk.CTkTabview(main, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("📋 All Events")
        self.tabview.add("✅ My Events")
        self.setup_all_events_tab()
        self.setup_my_events_tab()

    def setup_all_events_tab(self):
        tab = self.tabview.tab("📋 All Events")
        filter_frame = ctk.CTkFrame(tab, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 15))

        self.search_entry = ctk.CTkEntry(filter_frame, width=300, height=35, placeholder_text="Search events...")
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda _e: self.search_events())

        self.type_var = ctk.StringVar(value="All")
        ctk.CTkComboBox(filter_frame, width=140, values=["All", "Workshop", "Seminar", "Hackathon", "Webinar", "Career_Fair"], variable=self.type_var, command=self.filter_events).pack(side="left", padx=5)

        self.mode_var = ctk.StringVar(value="All")
        ctk.CTkComboBox(filter_frame, width=100, values=["All", "Online", "Offline", "Hybrid"], variable=self.mode_var, command=self.filter_events).pack(side="left", padx=5)

        ctk.CTkButton(filter_frame, text="Search", width=80, height=35, fg_color="#84B6FF", command=self.search_events).pack(side="left", padx=5)

        self.events_grid = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.events_grid.pack(fill="both", expand=True)
        self.events_grid.grid_columnconfigure(0, weight=1)
        self.events_grid.grid_columnconfigure(1, weight=1)

    def setup_my_events_tab(self):
        tab = self.tabview.tab("✅ My Events")
        created = ctk.CTkFrame(tab, fg_color="transparent")
        created.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(created, text="My Created Events", font=("Arial", 18, "bold"), text_color="#1F3B5B").pack(anchor="w", pady=(0, 10))
        self.created_frame = ctk.CTkScrollableFrame(created, fg_color="transparent", height=170)
        self.created_frame.pack(fill="x")

        upcoming = ctk.CTkFrame(tab, fg_color="transparent")
        upcoming.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(upcoming, text="My Registered Upcoming Events", font=("Arial", 18, "bold"), text_color="#1F3B5B").pack(anchor="w", pady=(0, 10))
        self.upcoming_frame = ctk.CTkScrollableFrame(upcoming, fg_color="transparent", height=200)
        self.upcoming_frame.pack(fill="x")

        past = ctk.CTkFrame(tab, fg_color="transparent")
        past.pack(fill="both", expand=True)
        ctk.CTkLabel(past, text="Past Events", font=("Arial", 18, "bold"), text_color="#1F3B5B").pack(anchor="w", pady=(0, 10))
        self.past_frame = ctk.CTkScrollableFrame(past, fg_color="transparent")
        self.past_frame.pack(fill="both", expand=True)

    def load_events(self):
        for widget in self.events_grid.winfo_children():
            widget.destroy()

        filters = {}
        if self.type_var.get() != "All":
            filters['event_type'] = self.type_var.get().lower()
        if self.mode_var.get() != "All":
            filters['mode'] = self.mode_var.get().lower()
        if self.search_entry.get().strip():
            filters['search'] = self.search_entry.get().strip()

        self.events_cache = self.db.get_events(filters) or []
        payload = self.db.get_event_dashboard_payload(self.user['user_id']) if hasattr(self.db, 'get_event_dashboard_payload') else {}
        self.registered_events = payload.get('registered_events', self.db.get_user_events(self.user['user_id']) or [])
        self.created_events = payload.get('created_events', self.db.get_user_created_events(self.user['user_id'], include_past=True) or [])
        self.user_event_ids = {event['event_id'] for event in self.registered_events}

        if not self.events_cache:
            msg_frame = ctk.CTkFrame(self.events_grid, fg_color="transparent")
            msg_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(msg_frame, text="No events found", font=("Arial", 16), text_color="#6F8098").pack()
        else:
            for i, event in enumerate(self.events_cache):
                self.create_event_card(self.events_grid, event, i // 2, i % 2)

        self.load_my_events()

    def create_event_card(self, parent, event, row, col):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, border_width=1, border_color="#D7E6F7")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        type_colors = {"workshop": "#84B6FF", "seminar": "#B79AE8", "hackathon": "#F29B9B", "webinar": "#7FC8A9", "career_fair": "#F1C27D"}
        badge = ctk.CTkFrame(card, fg_color=type_colors.get(event['event_type'], "#AEBFD1"), corner_radius=5)
        badge.place(x=15, y=15)
        ctk.CTkLabel(badge, text=event['event_type'].replace('_', ' ').title(), font=("Arial", 10, "bold"), text_color="white").pack(padx=8, pady=2)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=(40, 15))
        ctk.CTkLabel(content, text=event['title'], font=("Arial", 16, "bold"), text_color="#1F3B5B").pack(anchor="w")
        ctk.CTkLabel(content, text=f"📅 {self.format_event_datetime(event)}", font=("Arial", 11), text_color="#6F8098", anchor="w").pack(anchor="w", pady=1)
        location_icon = "🌐" if event['mode'] == 'online' else "📍"
        location = event.get('platform') or event.get('location') or 'TBD'
        ctk.CTkLabel(content, text=f"{location_icon} {location}", font=("Arial", 11), text_color="#6F8098").pack(anchor="w", pady=1)
        ctk.CTkLabel(content, text=f"👤 {event['organizer_name']}", font=("Arial", 11), text_color="#6F8098").pack(anchor="w", pady=1)

        registered = event.get('registered_count', 0)
        max_participants = event.get('max_participants', 0)
        spots_text = f"👥 {registered}/{max_participants} spots filled" if max_participants > 0 else f"👥 {registered} participants"
        ctk.CTkLabel(content, text=spots_text, font=("Arial", 11), text_color="#6F8098").pack(anchor="w", pady=1)

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        event_date = event.get('start_date')
        if hasattr(event_date, 'date'):
            event_date = event_date.date()
        deadline = event.get('registration_deadline')
        if hasattr(deadline, 'date'):
            deadline = deadline.date()
        is_owner = event.get('organizer_id') == self.user['user_id']
        is_past = bool(event_date and event_date < datetime.now().date())
        deadline_passed = bool(deadline and deadline < datetime.now().date())
        is_full = bool(event.get('max_participants', 0) > 0 and event.get('registered_count', 0) >= event.get('max_participants', 0))

        if is_owner:
            main_text, main_action, main_color = 'Organizer', None, '#AEBFD1'
        elif event['event_id'] in self.user_event_ids:
            main_text, main_action, main_color = 'Join Info', lambda e=event: self.show_join_info(e), '#7FC8A9'
        elif is_past:
            main_text, main_action, main_color = 'Closed', None, '#AEBFD1'
        elif deadline_passed:
            main_text, main_action, main_color = 'Deadline Passed', None, '#AEBFD1'
        elif is_full:
            main_text, main_action, main_color = 'Full', None, '#AEBFD1'
        else:
            main_text, main_action, main_color = 'Register', lambda e=event: self.register_event(e), '#7FC8A9'

        ctk.CTkButton(btn_frame, text=main_text, height=35, fg_color=main_color, command=main_action, state='normal' if callable(main_action) else 'disabled').pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Details", height=35, fg_color="#84B6FF", command=lambda e=event: self.show_event_details(e)).pack(side="right", padx=2, expand=True, fill="x")

    def register_event(self, event):
        success, message = self.db.register_for_event(event['event_id'], self.user['user_id'])
        if success:
            show_success(message)
            self.load_events()
        else:
            show_error(message)

    def show_join_info(self, event):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Join: {event['title']}")
        dialog.geometry("420x320")
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (420 // 2)
        y = (dialog.winfo_screenheight() // 2) - (320 // 2)
        dialog.geometry(f'+{x}+{y}')

        ctk.CTkLabel(dialog, text="Event Join Information", font=("Arial", 18, "bold")).pack(pady=15)
        info_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)

        if event['mode'] == 'online':
            ctk.CTkLabel(info_frame, text=f"Platform: {event.get('platform') or 'Online Platform'}", font=("Arial", 12)).pack(anchor="w", pady=3)
        elif event['mode'] == 'offline':
            ctk.CTkLabel(info_frame, text=f"Location: {event.get('location') or 'Not provided'}", font=("Arial", 12)).pack(anchor="w", pady=3)
        else:
            ctk.CTkLabel(info_frame, text=f"Online: {event.get('platform') or 'Not provided'}", font=("Arial", 12)).pack(anchor="w", pady=3)
            ctk.CTkLabel(info_frame, text=f"Offline: {event.get('location') or 'Not provided'}", font=("Arial", 12)).pack(anchor="w", pady=3)
        ctk.CTkLabel(info_frame, text=f"Start: {self.format_event_datetime(event)}", font=("Arial", 12)).pack(anchor="w", pady=3)
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def load_my_events(self):
        for frame in (self.created_frame, self.upcoming_frame, self.past_frame):
            for widget in frame.winfo_children():
                widget.destroy()

        self.render_created_events()
        if not self.registered_events:
            ctk.CTkLabel(self.upcoming_frame, text="No events registered", font=("Arial", 12), text_color="#6F8098").pack(pady=20)
            ctk.CTkLabel(self.past_frame, text="No past events", font=("Arial", 12), text_color="#6F8098").pack(pady=20)
            return

        today = datetime.now().date()
        has_past = False
        has_upcoming = False
        for event in self.registered_events:
            event_date = event['start_date'].date() if hasattr(event['start_date'], 'date') else event['start_date']
            if event_date >= today:
                has_upcoming = True
                self.create_my_event_item(self.upcoming_frame, event, "upcoming")
            else:
                has_past = True
                self.create_my_event_item(self.past_frame, event, "past")

        if not has_upcoming:
            ctk.CTkLabel(self.upcoming_frame, text="No upcoming events", font=("Arial", 12), text_color="#6F8098").pack(pady=20)
        if not has_past:
            ctk.CTkLabel(self.past_frame, text="No past events", font=("Arial", 12), text_color="#6F8098").pack(pady=20)

    def render_created_events(self):
        can_create = self.user['role'] in ['teacher', 'senior_student']
        if not can_create:
            ctk.CTkLabel(self.created_frame, text="Only teachers and senior students can create events.", font=("Arial", 12), text_color="#6F8098").pack(pady=20)
            return
        if not self.created_events:
            ctk.CTkLabel(self.created_frame, text="You have not created any events yet", font=("Arial", 12), text_color="#6F8098").pack(pady=20)
            return
        for event in self.created_events:
            item = ctk.CTkFrame(self.created_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#D7E6F7")
            item.pack(fill="x", pady=4)
            inner = ctk.CTkFrame(item, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)
            ctk.CTkLabel(inner, text=f"{event['title']} • {self.format_event_datetime(event)}", font=("Arial", 11), text_color="#1F3B5B").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(inner, text="Details", width=70, height=28, fg_color="#84B6FF", command=lambda e=event: self.show_event_details(e)).pack(side="right", padx=2)

    def create_my_event_item(self, parent, event, status):
        item = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#D7E6F7")
        item.pack(fill="x", pady=2)
        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(inner, text="🔜" if status == "upcoming" else "✅", font=("Arial", 14)).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(inner, text=f"{event['title']} - {self.format_event_datetime(event)}", font=("Arial", 11), text_color="#1F3B5B").pack(side="left", fill="x", expand=True)

        if status == "upcoming":
            ctk.CTkButton(inner, text="Cancel", width=60, height=25, fg_color="#F29B9B", command=lambda e=event: self.cancel_event(e)).pack(side="right", padx=2)
            ctk.CTkButton(inner, text="Join", width=60, height=25, fg_color="#7FC8A9", command=lambda e=event: self.show_join_info(e)).pack(side="right", padx=2)
        else:
            ctk.CTkButton(inner, text="Review", width=60, height=25, fg_color="#F1C27D", command=lambda e=event: self.review_event(e)).pack(side="right", padx=2)
            ctk.CTkButton(inner, text="Certificate", width=80, height=25, fg_color="#84B6FF", command=lambda e=event: self.get_certificate(e)).pack(side="right", padx=2)

    def cancel_event(self, event):
        if not ask_confirm(f"Cancel registration for {event['title']}?"):
            return
        if self.db.cancel_event_registration(event['event_id'], self.user['user_id']):
            show_success("Registration cancelled")
            self.load_events()
        else:
            show_error("Unable to cancel this registration. The event may already have started.")

    def review_event(self, event):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Event Review")
        dialog.geometry("420x360")
        ctk.CTkLabel(dialog, text=event['title'], font=("Arial", 18, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="Rating (1-5)").pack(anchor="w", padx=20)
        rating_var = ctk.StringVar(value=str(int(event.get('feedback_rating') or 5)))
        ctk.CTkComboBox(dialog, values=["1", "2", "3", "4", "5"], variable=rating_var, width=120).pack(anchor="w", padx=20, pady=(5, 10))
        ctk.CTkLabel(dialog, text="Comment").pack(anchor="w", padx=20)
        comment_box = ctk.CTkTextbox(dialog, width=360, height=140)
        comment_box.pack(padx=20, pady=(5, 15))
        if event.get('feedback_comment'):
            comment_box.insert('end', event['feedback_comment'])

        def submit_review():
            try:
                rating = int(rating_var.get())
                comment = require_text(comment_box.get('1.0', 'end-1c'), 'Comment')
            except ValueError as exc:
                show_error(str(exc))
                return
            if self.db.submit_event_feedback(event['event_id'], self.user['user_id'], rating, comment):
                show_success('Review submitted successfully.')
                dialog.destroy()
                self.load_events()
            else:
                show_error('Failed to submit review. Feedback is only available after the event has passed or attendance is marked.')

        ctk.CTkButton(dialog, text="Submit", fg_color="#7FC8A9", command=submit_review).pack(side='left', padx=20, pady=10)
        ctk.CTkButton(dialog, text="Close", fg_color="#AEBFD1", command=dialog.destroy).pack(side='right', padx=20, pady=10)

    def get_certificate(self, event):
        if event.get('certificate_url'):
            webbrowser.open(event['certificate_url'])
            return
        if event.get('certificate_generated'):
            show_success("Certificate is marked as ready, but no download link is stored yet.", "Certificate")
            return
        if event.get('registration_status') != 'attended':
            show_error("Certificate is only available after attendance is marked.", "Certificate")
            return
        if self.db.mark_event_certificate_ready(event['event_id'], self.user['user_id']):
            show_success("Certificate marked as ready for this participant.", "Certificate")
            self.load_events()
        else:
            show_error("Unable to prepare certificate.", "Certificate")

    def show_event_details(self, event):
        from .event_detail_page import EventDetailPage
        EventDetailPage(self.parent, self.user, self.db, event, on_updated=self.load_events)

    def filter_events(self, choice=None):
        self.load_events()

    def search_events(self):
        self.load_events()

    def open_create_event(self):
        from .create_event_page import CreateEventPage
        CreateEventPage(self.parent, self.user, self.db, on_created=self.load_events)

    def format_event_datetime(self, event):
        date_str = event['start_date'].strftime("%b %d, %Y") if hasattr(event['start_date'], 'strftime') else str(event['start_date'])
        time_str = event['start_time'].strftime("%I:%M %p") if hasattr(event['start_time'], 'strftime') else str(event['start_time'])
        return f"{date_str} at {time_str}"
