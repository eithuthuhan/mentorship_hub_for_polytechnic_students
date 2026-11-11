import customtkinter as ctk

from .active_mentorships_page import ActiveMentorshipsPage
from .find_mentors_page import FindMentorsPage
from .messages_page import MessagesPage
from .my_requests_page import MyRequestsPage


class MentorshipPage:
    """Main Mentorship page with live database-backed tabs."""

    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        self.tab_pages = {}

        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        self.main = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=20, pady=10)

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_wrap = ctk.CTkFrame(header, fg_color="transparent")
        title_wrap.pack(side="left")
        ctk.CTkLabel(title_wrap, text="👥 Mentorship", font=("Arial", 28, "bold"), text_color="#1F3B5B").pack(anchor="w")
        self.subtitle_label = ctk.CTkLabel(title_wrap, text="Your live mentorship overview", font=("Arial", 12), text_color="#6F8098")
        self.subtitle_label.pack(anchor="w", pady=(4, 0))

        action_wrap = ctk.CTkFrame(header, fg_color="transparent")
        action_wrap.pack(side="right")
        ctk.CTkButton(action_wrap, text="Refresh", width=100, height=36, fg_color="#84B6FF", command=self.refresh_all).pack(side="right")

        self.stats_frame = ctk.CTkFrame(self.main, fg_color="#EFF5FF", corner_radius=12)
        self.stats_frame.pack(fill="x", pady=(0, 16))

        self.tabview = ctk.CTkTabview(self.main, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("🔍 Find Mentors")
        self.tab_pages["find"] = FindMentorsPage(self.tabview.tab("🔍 Find Mentors"), self.user, self.db, on_updated=self.refresh_all)

        role = self.user.get("role")
        if role == "junior_student":
            self.tabview.add("📋 My Requests")
            self.tabview.add("✅ My Mentors")
            self.tabview.add("💬 Messages")
            self.tab_pages["requests"] = MyRequestsPage(self.tabview.tab("📋 My Requests"), self.user, self.db, "mentee", on_updated=self.refresh_all)
            self.tab_pages["active"] = ActiveMentorshipsPage(self.tabview.tab("✅ My Mentors"), self.user, self.db, "mentee", on_updated=self.refresh_all)
            self.tab_pages["messages"] = MessagesPage(self.tabview.tab("💬 Messages"), self.user, self.db)
        elif role == "senior_student":
            self.tabview.add("👨‍🏫 As Mentor")
            self.tabview.add("👨‍🎓 As Mentee")
            self.tabview.add("💬 Messages")
            self.tab_pages["mentor_requests"] = MyRequestsPage(self.tabview.tab("👨‍🏫 As Mentor"), self.user, self.db, "mentor", on_updated=self.refresh_all)
            self.tab_pages["mentee_requests"] = MyRequestsPage(self.tabview.tab("👨‍🎓 As Mentee"), self.user, self.db, "mentee", on_updated=self.refresh_all)
            self.tab_pages["messages"] = MessagesPage(self.tabview.tab("💬 Messages"), self.user, self.db)
        elif role == "teacher":
            self.tabview.add("📋 Requests")
            self.tabview.add("👥 My Mentees")
            self.tabview.add("💬 Messages")
            self.tab_pages["requests"] = MyRequestsPage(self.tabview.tab("📋 Requests"), self.user, self.db, "mentor", on_updated=self.refresh_all)
            self.tab_pages["active"] = ActiveMentorshipsPage(self.tabview.tab("👥 My Mentees"), self.user, self.db, "mentor", on_updated=self.refresh_all)
            self.tab_pages["messages"] = MessagesPage(self.tabview.tab("💬 Messages"), self.user, self.db)

    def refresh_all(self):
        self.render_stats()
        for page in self.tab_pages.values():
            if hasattr(page, 'refresh'):
                page.refresh()
            elif hasattr(page, 'load_requests'):
                page.load_requests()
            elif hasattr(page, 'load_mentorships'):
                page.load_mentorships()
            elif hasattr(page, 'load_mentors'):
                page.load_mentors()
            elif hasattr(page, 'load_conversations'):
                page.load_conversations()

    def render_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        summary = self.db.get_mentorship_summary(self.user['user_id']) if self.db else {}
        welcome = self.db.get_new_user_welcome_state(self.user['user_id']) if self.db else {'is_new': False}

        if welcome.get('is_new'):
            self.subtitle_label.configure(text="Welcome to Mentorship Hub — start by finding a mentor or reviewing new requests.")
        else:
            self.subtitle_label.configure(text="Everything below is live from the database and updates as requests, chats, and sessions change.")

        role = self.user.get('role')
        if role == 'junior_student':
            cards = [
                ("Outgoing Requests", summary.get('outgoing_pending', 0), "#F1C27D"),
                ("My Mentors", summary.get('my_mentors', 0), "#7FC8A9"),
                ("Active Chats", summary.get('active_chats', 0), "#84B6FF"),
            ]
        elif role == 'senior_student':
            cards = [
                ("Incoming Requests", summary.get('incoming_pending', 0), "#F1C27D"),
                ("Outgoing Requests", summary.get('outgoing_pending', 0), "#84B6FF"),
                ("My Mentees", summary.get('my_mentees', 0), "#7FC8A9"),
                ("My Mentors", summary.get('my_mentors', 0), "#A78BFA"),
            ]
        elif role == 'teacher':
            cards = [
                ("Incoming Requests", summary.get('incoming_pending', 0), "#F1C27D"),
                ("My Mentees", summary.get('my_mentees', 0), "#7FC8A9"),
                ("Completed", summary.get('completed_as_mentor', 0), "#84B6FF"),
                ("Active Chats", summary.get('active_chats', 0), "#A78BFA"),
            ]
        else:
            cards = []

        for idx, (label, value, color) in enumerate(cards):
            card = ctk.CTkFrame(self.stats_frame, fg_color="white", border_width=1, border_color="#D7E6F7", corner_radius=12)
            card.grid(row=0, column=idx, padx=8, pady=10, sticky="nsew")
            self.stats_frame.grid_columnconfigure(idx, weight=1)
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="#6F8098").pack(anchor="w", padx=14, pady=(12, 6))
            ctk.CTkLabel(card, text=str(value), font=("Arial", 24, "bold"), text_color=color).pack(anchor="w", padx=14, pady=(0, 12))
