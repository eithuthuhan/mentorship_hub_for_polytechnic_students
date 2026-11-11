import customtkinter as ctk

from colors import Colors
from gui.ui_helpers import ask_confirm, show_error, show_info, show_success


class EventDetailPage:
    def __init__(self, parent, user, db, event, on_updated=None):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(event.get('title', 'Event Details'))
        self.window.geometry('860x720')
        self.user = user
        self.db = db
        self.event = event
        self.on_updated = on_updated
        try:
            self.window.transient(parent)
        except Exception:
            pass
        self.window.update_idletasks()
        self.window.lift()
        self.window.focus_force()
        try:
            self.window.attributes('-topmost', True)
            self.window.after(350, lambda: self.window.attributes('-topmost', False))
            self.window.after(50, self.window.lift)
            self.window.after(100, self.window.focus_force)
        except Exception:
            pass
        self.setup_ui()
        self.load_event()
        self.window.grab_set()

    def setup_ui(self):
        self.main = ctk.CTkScrollableFrame(self.window, fg_color='transparent')
        self.main.pack(fill='both', expand=True, padx=20, pady=20)

        self.title_label = ctk.CTkLabel(self.main, text='', font=('Arial', 26, 'bold'), text_color=Colors.TEXT_DARK)
        self.title_label.pack(anchor='w', pady=(0, 8))

        self.meta_frame = ctk.CTkFrame(self.main, fg_color=Colors.BG_SOFT_BLUE, corner_radius=16)
        self.meta_frame.pack(fill='x', pady=(0, 14))

        self.action_frame = ctk.CTkFrame(self.main, fg_color='transparent')
        self.action_frame.pack(fill='x', pady=(0, 14))

        self.description_box = ctk.CTkTextbox(self.main, width=720, height=220, wrap='word', font=('Arial', 12), fg_color=Colors.BG_WHITE, text_color=Colors.TEXT_DARK, border_width=1, border_color=Colors.BORDER)
        self.description_box.pack(fill='both', expand=False, pady=(0, 14))
        self.description_box.configure(state='disabled')

        self.info_frame = ctk.CTkFrame(self.main, fg_color=Colors.BG_WHITE, corner_radius=16, border_width=1, border_color=Colors.BORDER)
        self.info_frame.pack(fill='x', pady=(0, 14))

        self.participants_frame = ctk.CTkFrame(self.main, fg_color=Colors.BG_WHITE, corner_radius=16, border_width=1, border_color=Colors.BORDER)
        self.participants_frame.pack(fill='x', pady=(0, 14))

        ctk.CTkButton(self.main, text='Close', fg_color=Colors.PRIMARY, command=self.window.destroy).pack(pady=(6, 0))

    def load_event(self):
        fresh_event = self.db.get_event_by_id(self.event['event_id']) if self.db else None
        if fresh_event:
            self.event = fresh_event

        self.title_label.configure(text=self.event.get('title', 'Event'))
        self._render_meta()
        self._render_actions()
        self._render_description()
        self._render_info()
        self._render_participants()

    def _render_meta(self):
        for widget in self.meta_frame.winfo_children():
            widget.destroy()

        left = ctk.CTkFrame(self.meta_frame, fg_color='transparent')
        left.pack(side='left', fill='x', expand=True, padx=14, pady=12)
        ctk.CTkLabel(left, text=f"{(self.event.get('event_type') or '').replace('_', ' ').title()} • {(self.event.get('mode') or '').title()}", font=('Arial', 13, 'bold'), text_color=Colors.TEXT_DARK).pack(anchor='w')
        ctk.CTkLabel(left, text=f"Organizer: {self.event.get('organizer_name', 'Unknown')}", font=('Arial', 12), text_color=Colors.TEXT_MUTED).pack(anchor='w', pady=(4, 0))

        right = ctk.CTkFrame(self.meta_frame, fg_color='transparent')
        right.pack(side='right', padx=14, pady=12)
        status = (self.event.get('status') or 'upcoming').title()
        ctk.CTkLabel(right, text=status, font=('Arial', 12, 'bold'), text_color=Colors.TEXT_DARK).pack(anchor='e')
        ctk.CTkLabel(right, text=f"{self.event.get('registered_count', 0)} registered", font=('Arial', 11), text_color=Colors.TEXT_MUTED).pack(anchor='e', pady=(4, 0))

    def _render_actions(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        event_id = self.event['event_id']
        role = self.user.get('role')
        organizer_id = self.event.get('organizer_id')
        registration = self.db.get_event_registration_status(event_id, self.user['user_id']) if self.db else None
        is_owner = organizer_id == self.user['user_id']

        if is_owner:
            ctk.CTkLabel(self.action_frame, text='This event was created by you.', font=('Arial', 12), text_color=Colors.TEXT_MUTED).pack(side='left')
            return

        can_join = role in ('junior_student', 'senior_student', 'teacher')
        if not can_join:
            return

        if registration and registration.get('status') == 'registered':
            ctk.CTkButton(self.action_frame, text='Cancel Registration', fg_color=Colors.DANGER, command=self._cancel_registration).pack(side='left', padx=(0, 8))
            ctk.CTkButton(self.action_frame, text='Join Info', fg_color=Colors.SECONDARY, command=self._show_join_info).pack(side='left', padx=(0, 8))
        elif registration and registration.get('status') == 'attended':
            ctk.CTkButton(self.action_frame, text='Join Info', fg_color=Colors.SECONDARY, command=self._show_join_info).pack(side='left', padx=(0, 8))
            ctk.CTkButton(self.action_frame, text='Attendance Saved', fg_color=Colors.SUCCESS, state='disabled').pack(side='left')
        else:
            ctk.CTkButton(self.action_frame, text='Register', fg_color=Colors.SUCCESS, command=self._register).pack(side='left')

    def _render_description(self):
        description = (self.event.get('description') or '').strip()
        venue = self.event.get('platform') if (self.event.get('mode') or '').lower() == 'online' else self.event.get('location')
        audience = self.event.get('target_audience') or 'All interested members'
        extra = [
            description or 'No description provided yet.',
            '',
            'What you can expect:',
            f"• A guided session focused on {self.event.get('title', 'this event').lower()}.",
            '• Practical discussion, networking, and follow-up guidance where relevant.',
            '• Structured explanation, question-and-answer time, and clear next-step recommendations.',
            '• A friendly environment for both first-time participants and active members.',
            f"• Suitable for: {audience}.",
            f"• Venue / access: {venue or 'Details will be shared with registered participants.'}",
            '• Registered participants will be able to revisit the event details page for quick access to joining information.',
        ]
        self.description_box.configure(state='normal')
        self.description_box.delete('1.0', 'end')
        self.description_box.insert('end', "\n".join(extra))
        self.description_box.configure(state='disabled')

    def _render_info(self):
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.info_frame, text='Event Information', font=('Arial', 16, 'bold'), text_color=Colors.TEXT_DARK).pack(anchor='w', padx=14, pady=(12, 8))

        rows = [
            ('Start date', self._fmt(self.event.get('start_date'))),
            ('Start time', self._fmt(self.event.get('start_time'))),
            ('End date', self._fmt(self.event.get('end_date'))),
            ('End time', self._fmt(self.event.get('end_time'))),
            ('Registration deadline', self._fmt(self.event.get('registration_deadline'))),
            ('Location', self.event.get('location') or '—'),
            ('Platform', self.event.get('platform') or '—'),
            ('Target audience', self.event.get('target_audience') or '—'),
            ('Capacity', self.event.get('max_participants') or 'Unlimited'),
        ]

        for label, value in rows:
            row = ctk.CTkFrame(self.info_frame, fg_color='transparent')
            row.pack(fill='x', padx=14, pady=4)
            ctk.CTkLabel(row, text=label, font=('Arial', 12), text_color=Colors.TEXT_MUTED).pack(side='left')
            ctk.CTkLabel(row, text=str(value), font=('Arial', 12, 'bold'), text_color=Colors.TEXT_DARK).pack(side='right')

    def _render_participants(self):
        for widget in self.participants_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.participants_frame, text='Recent Participants', font=('Arial', 16, 'bold'), text_color=Colors.TEXT_DARK).pack(anchor='w', padx=14, pady=(12, 8))

        participants = self.db.get_event_participants(self.event['event_id'], statuses=['registered', 'attended']) if self.db else []
        if not participants:
            ctk.CTkLabel(self.participants_frame, text='No participant data yet.', font=('Arial', 12), text_color=Colors.TEXT_MUTED).pack(anchor='w', padx=14, pady=(0, 14))
            return

        for participant in participants[:8]:
            row = ctk.CTkFrame(self.participants_frame, fg_color=Colors.BG_SOFTER, corner_radius=12)
            row.pack(fill='x', padx=14, pady=5)
            ctk.CTkLabel(row, text=participant.get('full_name', 'Member'), font=('Arial', 12, 'bold'), text_color=Colors.TEXT_DARK).pack(side='left', padx=12, pady=10)
            secondary = f"{participant.get('role', '').replace('_', ' ').title()} • {participant.get('status', 'registered').title()}"
            ctk.CTkLabel(row, text=secondary, font=('Arial', 11), text_color=Colors.TEXT_MUTED).pack(side='right', padx=12)

    def _register(self):
        ok, message = self.db.register_for_event(self.event['event_id'], self.user['user_id'])
        if ok:
            show_success(message)
            self._updated()
        else:
            show_error(message or 'Unable to register for this event.')

    def _cancel_registration(self):
        if not ask_confirm('Cancel your registration for this event?'):
            return
        ok = self.db.cancel_event_registration(self.event['event_id'], self.user['user_id'])
        if ok:
            show_success('Registration cancelled.')
            self._updated()
        else:
            show_error('Unable to cancel registration.')

    def _show_join_info(self):
        mode = (self.event.get('mode') or '').lower()
        if mode == 'online':
            info = self.event.get('platform') or 'Online event information has not been added yet.'
        else:
            info = self.event.get('location') or 'Location information has not been added yet.'
        show_info(info, 'Join Information')

    def _updated(self):
        self.load_event()
        if callable(self.on_updated):
            self.on_updated()

    def _fmt(self, value):
        if hasattr(value, 'strftime'):
            if hasattr(value, 'hour'):
                return value.strftime('%Y-%m-%d %H:%M')
            return value.strftime('%Y-%m-%d')
        return value or '—'
