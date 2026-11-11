import customtkinter as ctk

from .dialogs import MentorshipChatDialog, RequestDetailsDialog, ScheduleSessionDialog


class ActiveMentorshipsPage:
    """Live accepted mentorship list."""

    def __init__(self, parent, user, db, role_type='mentee', on_updated=None):
        self.parent = parent
        self.user = user
        self.db = db
        self.role_type = role_type
        self.on_updated = on_updated

        self.setup_ui()
        self.load_mentorships()

    def setup_ui(self):
        self.scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True)

    def refresh(self):
        self.load_mentorships()

    def load_mentorships(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        requests = self.db.get_mentorship_requests(self.user['user_id'], 'teacher' if self.role_type == 'mentor' else 'mentee', status='accepted') or []
        if not requests:
            empty_text = 'No active mentees yet' if self.role_type == 'mentor' else 'No active mentors yet'
            ctk.CTkLabel(self.scrollable, text=empty_text, font=("Arial", 14), text_color="#6F8098").pack(pady=40)
            return

        for req in requests:
            sessions = self.db.get_sessions(req['request_id']) or []
            completed = len([s for s in sessions if s.get('status') == 'completed'])
            planned = len(sessions)
            progress = 0 if planned == 0 else int((completed / planned) * 100)
            next_session = self._get_next_session_text(sessions)
            self.create_mentorship_card({
                'with': req.get('other_name', 'Unknown'),
                'topic': req.get('subject', 'Mentorship Session'),
                'progress': progress,
                'next': next_session,
                'request_record': req,
                'session_count': planned,
                'completed_sessions': completed,
            })

    def _get_next_session_text(self, sessions):
        upcoming = []
        for session in sessions:
            when = session.get('session_date')
            status = session.get('status', '')
            if hasattr(when, 'strftime') and status not in ('completed', 'cancelled'):
                upcoming.append(when)
        if not upcoming:
            return 'Not scheduled yet'
        return sorted(upcoming)[0].strftime('%Y-%m-%d %I:%M %p')

    def create_mentorship_card(self, m):
        card = ctk.CTkFrame(self.scrollable, fg_color="white", corner_radius=12, border_width=1, border_color="#D7E6F7")
        card.pack(fill="x", pady=6, padx=5)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 6))
        ctk.CTkLabel(header, text=f"👤 {m['with']}", font=("Arial", 16, "bold"), text_color="#1F3B5B").pack(side="left")
        ctk.CTkLabel(header, text=f"📅 Next: {m['next']}", font=("Arial", 12), text_color="#F1C27D").pack(side="right")

        ctk.CTkLabel(card, text=m['topic'], font=("Arial", 13), text_color="#84B6FF").pack(anchor="w", padx=15, pady=(0, 4))
        ctk.CTkLabel(card, text=f"Sessions: {m['completed_sessions']}/{m['session_count']} completed", font=("Arial", 11), text_color="#6F8098").pack(anchor="w", padx=15)

        progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(progress_frame, text="Progress:", font=("Arial", 11), text_color="#6F8098").pack(side="left")
        progress_bar = ctk.CTkProgressBar(progress_frame, width=280)
        progress_bar.pack(side="left", padx=10)
        progress_bar.set(max(0, min(m['progress'], 100)) / 100)
        ctk.CTkLabel(progress_frame, text=f"{m['progress']}%", font=("Arial", 11), text_color="#7FC8A9").pack(side="left")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(10, 15))
        ctk.CTkButton(btn_frame, text="💬 Chat", width=90, fg_color="#84B6FF", command=lambda: self.message(m)).pack(side="left", padx=3)
        if self.role_type == 'mentor':
            ctk.CTkButton(btn_frame, text="📅 Schedule", width=100, fg_color="#F1C27D", command=lambda: self.schedule(m)).pack(side="left", padx=3)
        ctk.CTkButton(btn_frame, text="📄 Details", width=90, fg_color="#7FC8A9", command=lambda: self.view_details(m)).pack(side="left", padx=3)

    def message(self, m):
        MentorshipChatDialog(self.parent, self.user, self.db, m['request_record'], on_updated=self.after_action)

    def schedule(self, m):
        ScheduleSessionDialog(self.parent, self.user, self.db, m['request_record'], on_saved=self.after_action)

    def view_details(self, m):
        RequestDetailsDialog(self.parent, self.user, self.db, m['request_record'], on_updated=self.after_action)

    def after_action(self):
        self.load_mentorships()
        if callable(self.on_updated):
            self.on_updated()
