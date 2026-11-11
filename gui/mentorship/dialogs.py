import customtkinter as ctk

from colors import Colors
from gui.ui_helpers import ask_confirm, require_text, show_error, show_success


def _center_window(window, width, height):
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def _show_modal_front(window, parent=None):
    try:
        if parent is not None:
            window.transient(parent)
    except Exception:
        pass
    try:
        window.update_idletasks()
        window.lift()
        window.focus_force()
        window.attributes('-topmost', True)
        window.after(350, lambda: window.attributes('-topmost', False))
        window.after(50, window.lift)
        window.after(100, window.focus_force)
    except Exception:
        pass


class MentorshipChatDialog:
    def __init__(self, parent, user, db, request_record, on_updated=None):
        self.parent = parent
        self.user = user
        self.db = db
        self.request_record = request_record
        self.request_id = request_record["request_id"]
        self.on_updated = on_updated

        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"Chat - {request_record.get('other_name', 'Mentorship')}")
        _center_window(self.window, 700, 520)
        self.window.grab_set()
        _show_modal_front(self.window, parent)

        self.refresh_job = None
        self.setup_ui()
        self.load_messages()
        self.schedule_refresh()

    def setup_ui(self):
        ctk.CTkLabel(
            self.window,
            text=f"{self.request_record.get('other_name', 'Mentorship')} • {self.request_record.get('subject', 'Mentorship')}",
            font=("Arial", 18, "bold"),
            text_color=Colors.TEXT_DARK
        ).pack(padx=20, pady=(15, 10), anchor="w")

        self.messages_box = ctk.CTkTextbox(self.window, wrap="word", font=("Arial", 12))
        self.messages_box.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.messages_box.configure(state="disabled")

        bottom = ctk.CTkFrame(self.window, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=(0, 15))

        can_chat = self.request_record.get('status') in ('accepted', 'completed')
        entry_placeholder = "Type a message..." if can_chat else "Chat is available after acceptance"
        self.message_entry = ctk.CTkEntry(bottom, placeholder_text=entry_placeholder, height=38)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda _e: self.send_message())
        self.message_entry.configure(state='normal' if can_chat else 'disabled')

        self.send_button = ctk.CTkButton(bottom, text="Send", width=90, fg_color=Colors.SUCCESS, command=self.send_message)
        self.send_button.pack(side="left")
        self.send_button.configure(state='normal' if can_chat else 'disabled')
        self.window.protocol('WM_DELETE_WINDOW', self.close)

    def schedule_refresh(self):
        if self.window.winfo_exists():
            self.refresh_job = self.window.after(4000, self._auto_refresh)

    def _auto_refresh(self):
        try:
            if self.window.winfo_exists():
                self.load_messages()
        finally:
            if self.window.winfo_exists():
                self.schedule_refresh()

    def close(self):
        if self.refresh_job:
            try:
                self.window.after_cancel(self.refresh_job)
            except Exception:
                pass
            self.refresh_job = None
        self.window.destroy()

    def load_messages(self):
        messages = self.db.get_messages(self.request_id) or []
        self.db.mark_messages_as_read(self.request_id, self.user['user_id'])

        self.messages_box.configure(state="normal")
        self.messages_box.delete("1.0", "end")

        if self.request_record.get('status') not in ('accepted', 'completed'):
            self.messages_box.insert("end", f"Chat will unlock after this request is accepted. Current status: {self.request_record.get('status', 'pending').title()}.\n")
        elif not messages:
            self.messages_box.insert("end", "No messages yet. Start the conversation.\n")
        else:
            for msg in messages:
                sender = "You" if msg.get("sender_id") == self.user["user_id"] else msg.get("sender_name", "Other User")
                when = msg.get("sent_at")
                if hasattr(when, "strftime"):
                    when = when.strftime("%Y-%m-%d %I:%M %p")
                self.messages_box.insert("end", f"{sender} [{when}]\n", "sender")
                self.messages_box.insert("end", f"{msg.get('message', '')}\n\n", "body")

        self.messages_box.tag_config("sender", foreground=Colors.PRIMARY)
        self.messages_box.tag_config("body", foreground=Colors.TEXT_DARK)
        self.messages_box.configure(state="disabled")
        self.messages_box.see("end")

    def send_message(self):
        text = self.message_entry.get().strip()
        if not text:
            return
        result = self.db.send_message(self.request_id, self.user['user_id'], text)
        if result == -1:
            show_error("Unable to send message.", "Message")
            return
        self.message_entry.delete(0, "end")
        self.load_messages()
        if callable(self.on_updated):
            self.on_updated()


class MentorshipReviewDialog:
    def __init__(self, parent, user, db, request_record, is_mentor_rating, on_saved=None):
        self.parent = parent
        self.user = user
        self.db = db
        self.request_record = request_record
        self.is_mentor_rating = is_mentor_rating
        self.on_saved = on_saved

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Mentorship Review")
        _center_window(self.window, 420, 360)
        self.window.grab_set()
        _show_modal_front(self.window, parent)

        ctk.CTkLabel(self.window, text="Rate mentorship experience", font=("Arial", 18, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(
            self.window,
            text=f"{request_record.get('other_name', 'Mentorship')} • {request_record.get('subject', 'Mentorship')}",
            font=("Arial", 12),
            text_color=Colors.TEXT_MUTED
        ).pack(pady=(0, 15))

        ctk.CTkLabel(self.window, text="Rating (1-5)").pack(anchor="w", padx=20)
        self.rating_var = ctk.StringVar(value="5")
        ctk.CTkComboBox(self.window, values=["1", "2", "3", "4", "5"], variable=self.rating_var, width=120).pack(anchor="w", padx=20, pady=(5, 12))

        ctk.CTkLabel(self.window, text="Review").pack(anchor="w", padx=20)
        self.review_box = ctk.CTkTextbox(self.window, width=360, height=120)
        self.review_box.pack(padx=20, pady=(5, 15))

        buttons = ctk.CTkFrame(self.window, fg_color="transparent")
        buttons.pack(pady=(0, 15))
        ctk.CTkButton(buttons, text="Submit", fg_color=Colors.SUCCESS, command=self.submit).pack(side="left", padx=6)
        ctk.CTkButton(buttons, text="Cancel", fg_color=Colors.DANGER, command=self.close).pack(side="left", padx=6)

    def submit(self):
        try:
            rating = int(self.rating_var.get())
            review = require_text(self.review_box.get("1.0", "end-1c"), "Review")
        except ValueError as exc:
            show_error(str(exc))
            return

        ok = self.db.rate_mentorship(self.request_record['request_id'], rating, review, self.is_mentor_rating)
        if ok:
            show_success("Review submitted successfully.")
            self.window.destroy()
            if callable(self.on_saved):
                self.on_saved()
        else:
            show_error("Failed to submit review.")


class ScheduleSessionDialog:
    def __init__(self, parent, user, db, request_record, on_saved=None):
        self.parent = parent
        self.user = user
        self.db = db
        self.request_record = request_record
        self.on_saved = on_saved

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Schedule Session")
        _center_window(self.window, 420, 360)
        self.window.grab_set()
        _show_modal_front(self.window, parent)

        ctk.CTkLabel(self.window, text="Schedule mentorship session", font=("Arial", 18, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(self.window, text=request_record.get('other_name', 'Mentorship'), font=("Arial", 12), text_color=Colors.TEXT_MUTED).pack(pady=(0, 15))

        ctk.CTkLabel(self.window, text="Date & time (YYYY-MM-DD HH:MM)").pack(anchor="w", padx=20)
        self.datetime_entry = ctk.CTkEntry(self.window, width=360, placeholder_text="2026-03-30 14:30")
        self.datetime_entry.pack(padx=20, pady=(5, 12))

        ctk.CTkLabel(self.window, text="Duration in minutes").pack(anchor="w", padx=20)
        self.duration_entry = ctk.CTkEntry(self.window, width=360, placeholder_text="60")
        self.duration_entry.pack(padx=20, pady=(5, 12))

        ctk.CTkLabel(self.window, text="Agenda (optional)").pack(anchor="w", padx=20)
        self.agenda_box = ctk.CTkTextbox(self.window, width=360, height=90)
        self.agenda_box.pack(padx=20, pady=(5, 15))

        buttons = ctk.CTkFrame(self.window, fg_color="transparent")
        buttons.pack(pady=(0, 15))
        ctk.CTkButton(buttons, text="Save", fg_color=Colors.SUCCESS, command=self.save).pack(side="left", padx=6)
        ctk.CTkButton(buttons, text="Cancel", fg_color=Colors.DANGER, command=self.close).pack(side="left", padx=6)

    def save(self):
        from datetime import datetime

        try:
            when_text = require_text(self.datetime_entry.get(), "Date & time")
            session_date = datetime.strptime(when_text, "%Y-%m-%d %H:%M")
            duration_text = require_text(self.duration_entry.get(), "Duration")
            duration = int(duration_text)
            if session_date < datetime.now():
                raise ValueError("Session date must be in the future.")
            if duration <= 0:
                raise ValueError("Duration must be greater than 0 minutes.")
            agenda = self.agenda_box.get("1.0", "end-1c").strip() or None
        except ValueError as exc:
            show_error(str(exc) if str(exc) else "Please enter date/time as YYYY-MM-DD HH:MM and duration as a whole number.")
            return

        result = self.db.create_session(self.request_record['request_id'], session_date, duration, agenda)
        if result == -1:
            show_error("Failed to schedule session.")
            return

        show_success("Session scheduled successfully.")
        self.window.destroy()
        if callable(self.on_saved):
            self.on_saved()


class RequestDetailsDialog:
    def __init__(self, parent, user, db, request_record, on_updated=None):
        self.parent = parent
        self.user = user
        self.db = db
        self.request_record = request_record
        self.on_updated = on_updated

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Request Details")
        _center_window(self.window, 700, 620)
        self.window.grab_set()
        _show_modal_front(self.window, parent)

        self.header_label = ctk.CTkLabel(self.window, text='', font=("Arial", 22, "bold"), text_color=Colors.TEXT_DARK)
        self.header_label.pack(anchor="w", padx=20, pady=(20, 10))

        self.summary_badge = ctk.CTkFrame(self.window, fg_color=Colors.BG_SOFT_BLUE, corner_radius=999)
        self.summary_badge.pack(anchor='w', padx=20, pady=(0, 12))
        self.summary_badge_label = ctk.CTkLabel(self.summary_badge, text='', font=("Arial", 11, "bold"), text_color=Colors.TEXT_DARK)
        self.summary_badge_label.pack(padx=12, pady=6)

        self.body = ctk.CTkScrollableFrame(self.window, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        self.body.pack(fill='both', expand=True, padx=20, pady=(0, 15))

        self.overview_frame = ctk.CTkFrame(self.body, fg_color='transparent')
        self.overview_frame.pack(fill='x', padx=8, pady=(8, 10))

        self.message_card = ctk.CTkFrame(self.body, fg_color=Colors.BG_SOFTER, corner_radius=16, border_width=1, border_color=Colors.BORDER)
        self.message_card.pack(fill='x', padx=8, pady=(0, 10))

        self.action_bar = ctk.CTkFrame(self.window, fg_color='transparent')
        self.action_bar.pack(fill='x', padx=20, pady=(0, 12))

        ctk.CTkButton(self.window, text="Close", fg_color=Colors.PRIMARY, command=self.close).pack(pady=(0, 15))
        self.refresh()

    def close(self):
        self.window.destroy()

    def _build_display_record(self, fresh):
        record = dict(self.request_record or {})
        if fresh:
            record.update(fresh)
        is_mentor = record.get('mentor_id') == self.user.get('user_id')
        other_name = record.get('other_name')
        if not other_name:
            other_name = record.get('mentee_name') if is_mentor else record.get('mentor_name')
        record['other_name'] = other_name or 'Unknown Member'
        record['my_side'] = 'mentor' if is_mentor else 'mentee'
        return record

    def _format_value(self, value, fallback='—'):
        if hasattr(value, 'strftime'):
            try:
                return value.strftime('%Y-%m-%d %I:%M %p')
            except Exception:
                return value.strftime('%Y-%m-%d')
        return str(value) if value not in (None, '') else fallback

    def _detail_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color='transparent')
        row.pack(fill='x', pady=5)
        ctk.CTkLabel(row, text=label, font=("Arial", 12), text_color=Colors.TEXT_MUTED).pack(side='left')
        ctk.CTkLabel(row, text=value, font=("Arial", 12, "bold"), text_color=Colors.TEXT_DARK, wraplength=360, justify='right').pack(side='right')

    def refresh(self):
        fresh = self.db.get_mentorship_request_by_id(self.request_record['request_id']) if self.db else None
        self.request_record = self._build_display_record(fresh)

        status = (self.request_record.get('status') or 'pending').lower()
        mentor_name = self.request_record.get('mentor_name') or ('You' if self.request_record.get('mentor_id') == self.user.get('user_id') else self.request_record.get('other_name'))
        mentee_name = self.request_record.get('mentee_name') or ('You' if self.request_record.get('mentee_id') == self.user.get('user_id') else self.request_record.get('other_name'))

        self.header_label.configure(text=self.request_record.get('subject', 'Mentorship Request'))
        self.summary_badge_label.configure(text=f"Status: {status.title()} • With {self.request_record.get('other_name', 'Unknown Member')}")

        for widget in self.overview_frame.winfo_children():
            widget.destroy()
        self._detail_row(self.overview_frame, 'Mentor', mentor_name)
        self._detail_row(self.overview_frame, 'Mentee', mentee_name)
        self._detail_row(self.overview_frame, 'Current view', 'Mentor side' if self.request_record.get('my_side') == 'mentor' else 'Mentee side')
        self._detail_row(self.overview_frame, 'Created', self._format_value(self.request_record.get('created_at')))
        if self.request_record.get('accepted_at'):
            self._detail_row(self.overview_frame, 'Accepted', self._format_value(self.request_record.get('accepted_at')))
        self._detail_row(self.overview_frame, 'Request ID', str(self.request_record.get('request_id', '—')))

        for widget in self.message_card.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.message_card, text='Request Message', font=("Arial", 15, "bold"), text_color=Colors.TEXT_DARK).pack(anchor='w', padx=14, pady=(12, 6))
        ctk.CTkLabel(
            self.message_card,
            text=self.request_record.get('message') or 'No message was written for this request yet.',
            font=("Arial", 12),
            text_color=Colors.TEXT_DARK,
            wraplength=600,
            justify='left'
        ).pack(anchor='w', padx=14, pady=(0, 14))

        for widget in self.action_bar.winfo_children():
            widget.destroy()

        is_mentor = self.request_record.get('mentor_id') == self.user.get('user_id')
        if status == 'pending' and is_mentor:
            ctk.CTkButton(self.action_bar, text='Accept', fg_color=Colors.SUCCESS, command=self.accept).pack(side='left', padx=(0, 8))
            ctk.CTkButton(self.action_bar, text='Reject', fg_color=Colors.DANGER, command=self.reject).pack(side='left')
        elif status == 'pending' and not is_mentor:
            ctk.CTkButton(self.action_bar, text='Cancel Request', fg_color=Colors.DANGER, command=self.cancel_request).pack(side='left')
        elif status in ('accepted', 'completed'):
            ctk.CTkButton(self.action_bar, text='Open Chat', fg_color=Colors.SECONDARY, command=self.open_chat).pack(side='left', padx=(0, 8))
            if is_mentor and status == 'accepted':
                ctk.CTkButton(self.action_bar, text='Schedule', fg_color=Colors.WARNING, command=self.schedule_session).pack(side='left', padx=(0, 8))
            if status == 'completed':
                ctk.CTkButton(self.action_bar, text='Review', fg_color=Colors.SUCCESS, command=self.open_review).pack(side='left')

    def accept(self):
        if not ask_confirm('Accept this mentorship request?'):
            return
        ok = self.db.update_request_status(self.request_record['request_id'], 'accepted', self.user['user_id'])
        if ok:
            show_success('Request accepted!')
            self.refresh()
            if callable(self.on_updated):
                self.on_updated()
        else:
            show_error('Unable to accept this request.')

    def reject(self):
        if not ask_confirm('Reject this mentorship request?'):
            return
        ok = self.db.update_request_status(self.request_record['request_id'], 'rejected', self.user['user_id'])
        if ok:
            show_success('Request rejected.')
            self.refresh()
            if callable(self.on_updated):
                self.on_updated()
        else:
            show_error('Unable to reject this request.')

    def cancel_request(self):
        if not ask_confirm('Cancel this mentorship request?'):
            return
        ok = self.db.update_request_status(self.request_record['request_id'], 'cancelled', self.user['user_id'])
        if ok:
            show_success('Request cancelled.')
            self.refresh()
            if callable(self.on_updated):
                self.on_updated()
        else:
            show_error('Unable to cancel this request.')

    def open_chat(self):
        MentorshipChatDialog(self.window, self.user, self.db, self.request_record, on_updated=self.on_updated)

    def schedule_session(self):
        ScheduleSessionDialog(self.window, self.user, self.db, self.request_record, on_saved=self.on_updated)

    def open_review(self):
        is_mentor_rating = self.request_record.get('mentor_id') == self.user.get('user_id')
        MentorshipReviewDialog(self.window, self.user, self.db, self.request_record, is_mentor_rating, on_saved=self.on_updated)
