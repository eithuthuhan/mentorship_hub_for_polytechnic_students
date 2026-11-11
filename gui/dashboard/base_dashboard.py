import calendar
from datetime import datetime

import customtkinter as ctk

from colors import Colors




class BaseDashboard:
    """Role တိုင်းအတွက် အခြေခံ dashboard class"""

    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        self.main_frame = None

    def get_greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            return "☀️ Good Morning"
        elif hour < 17:
            return "☀️ Good Afternoon"
        return "🌙 Good Evening"

    def get_welcome_message(self):
        try:
            state = self.db.get_new_user_welcome_state(self.user['user_id']) if self.db else {'is_new': False}
        except Exception:
            state = {'is_new': False}
        greeting = self.get_greeting()
        name = self.user.get('full_name', 'Member')
        role = self.user.get('role', '')

        if state.get('is_new'):
            if role == 'teacher':
                subtitle = "Welcome to Mentorship Hub. Your dashboard will start showing requests, students, and events as soon as activity begins."
            elif role == 'senior_student':
                subtitle = "Welcome aboard. You can mentor juniors, request guidance, and create events from this dashboard."
            elif role == 'junior_student':
                subtitle = "Welcome to Mentorship Hub. Start by exploring mentors, sending a request, or joining an event."
            else:
                subtitle = "Welcome to the platform. Your dashboard will update automatically as members, requests, and events grow."
        else:
            if role == 'teacher':
                subtitle = "Here is your live overview of mentorship requests, assigned students, and events."
            elif role == 'senior_student':
                subtitle = "Here is your live mentor and mentee activity overview."
            elif role == 'junior_student':
                subtitle = "Track your mentorship requests, mentors, and learning opportunities here."
            else:
                subtitle = "Here is the latest platform activity and system overview."

        return f"{greeting}, {name}", subtitle

    def create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))

        meta = ctk.CTkFrame(header, fg_color="transparent")
        meta.pack(side="left", fill="x", expand=True)

        title_text, subtitle = self.get_welcome_message()
        ctk.CTkLabel(meta, text=title_text, font=("Arial", 28, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(meta, text=subtitle, font=("Arial", 13), text_color=Colors.TEXT_MUTED, wraplength=760, justify="left").pack(anchor="w", pady=(4, 0))

        badge = ctk.CTkFrame(header, fg_color=Colors.BG_SOFT_BLUE, corner_radius=999)
        badge.pack(side="right", padx=(12, 0))
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        ctk.CTkLabel(badge, text=current_date, font=("Arial", 11, "bold"), text_color=Colors.TEXT_DARK).pack(padx=14, pady=10)
        return header

    def create_section_box(self, parent, title, *, expand=False, pady=(0, 15), title_size=18):
        box = ctk.CTkFrame(
            parent,
            fg_color=Colors.BG_WHITE,
            corner_radius=18,
            border_width=1,
            border_color=Colors.BORDER,
        )
        box.pack(fill="both" if expand else "x", expand=expand, pady=pady)

        title_wrap = ctk.CTkFrame(box, fg_color="transparent")
        title_wrap.pack(fill="x", padx=18, pady=(16, 6))
        ctk.CTkLabel(title_wrap, text=title, font=("Arial", title_size, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w")
        ctk.CTkFrame(box, fg_color=Colors.BORDER, height=1).pack(fill="x", padx=18, pady=(0, 10))

        body = ctk.CTkFrame(box, fg_color="transparent")
        body.pack(fill="both" if expand else "x", expand=expand, padx=18, pady=(0, 14))
        return box, body

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def show_empty_state(self, frame, message):
        note = ctk.CTkFrame(frame, fg_color=Colors.BG_SOFT_BLUE, corner_radius=12)
        note.pack(fill="x", pady=5)
        ctk.CTkLabel(note, text=message, font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=420, justify="left").pack(anchor="w", padx=12, pady=10)

    def get_status_color(self, status):
        status_text = (status or '').lower()
        if status_text == 'pending':
            return Colors.WARNING
        if status_text in {'accepted', 'active'}:
            return Colors.SUCCESS
        if status_text in {'rejected', 'cancelled'}:
            return Colors.DANGER
        if status_text in {'completed'}:
            return Colors.PRIMARY
        return Colors.TEXT_MUTED

    def format_date(self, value, fallback='—'):
        if hasattr(value, 'strftime'):
            return value.strftime('%b %d, %Y')
        return str(value) if value else fallback

    def create_info_row(self, parent, icon, primary, secondary=None, status=None, status_color=None):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", pady=6)

        ctk.CTkLabel(item, text=icon, font=("Arial", 15), text_color=Colors.TEXT_DARK).pack(side="left", padx=(0, 10))

        text_wrap = ctk.CTkFrame(item, fg_color="transparent")
        text_wrap.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_wrap, text=primary, font=("Arial", 13, "bold"), text_color=Colors.TEXT_DARK, anchor="w").pack(anchor="w")
        if secondary:
            ctk.CTkLabel(text_wrap, text=secondary, font=("Arial", 11), text_color=Colors.TEXT_MUTED, anchor="w", wraplength=480, justify="left").pack(anchor="w", pady=(2, 0))

        if status is not None:
            badge = ctk.CTkFrame(item, fg_color=(status_color or Colors.BG_SOFT_BLUE), corner_radius=999)
            badge.pack(side="right")
            text_color = Colors.TEXT_LIGHT if (status_color and status_color not in {Colors.BG_SOFT_BLUE, Colors.SECONDARY}) else Colors.TEXT_DARK
            ctk.CTkLabel(badge, text=status, font=("Arial", 10, "bold"), text_color=text_color).pack(padx=10, pady=4)
        return item

    def create_metric_row(self, parent, label, value, color=Colors.TEXT_DARK):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", pady=5)
        ctk.CTkLabel(item, text=label, font=("Arial", 13), text_color=Colors.TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(item, text=str(value), font=("Arial", 13, "bold"), text_color=color).pack(side="right")
        return item

    def create_action_buttons(self, parent, actions):
        if not actions:
            return None

        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(side="right", padx=(10, 0))

        palette = [Colors.SECONDARY, Colors.SUCCESS, Colors.WARNING, Colors.DANGER, Colors.PRIMARY]
        for index, action in enumerate(actions[:3]):
            if not isinstance(action, dict):
                continue
            btn = ctk.CTkButton(
                wrap,
                text=action.get('text', 'Open'),
                width=78,
                height=30,
                corner_radius=10,
                fg_color=action.get('fg_color') or palette[index % len(palette)],
                hover_color=action.get('hover_color') or action.get('fg_color') or palette[index % len(palette)],
                text_color=action.get('text_color') or Colors.TEXT_DARK,
                font=("Arial", 11, "bold"),
                command=action.get('command'),
                state=action.get('state', 'normal'),
            )
            btn.pack(side="left", padx=4)
        return wrap

    def create_action_card(self, parent, icon, primary, secondary=None, status=None, status_color=None, actions=None):
        card = ctk.CTkFrame(parent, fg_color=Colors.BG_SOFTER, corner_radius=14, border_width=1, border_color=Colors.BORDER)
        card.pack(fill="x", pady=6)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 8))

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        line = ctk.CTkFrame(left, fg_color="transparent")
        line.pack(fill="x")
        ctk.CTkLabel(line, text=icon, font=("Arial", 16), text_color=Colors.TEXT_DARK).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(line, text=primary, font=("Arial", 13, "bold"), text_color=Colors.TEXT_DARK, anchor="w").pack(side="left", fill="x", expand=True)

        if status is not None:
            badge = ctk.CTkFrame(line, fg_color=(status_color or Colors.BG_SOFT_BLUE), corner_radius=999)
            badge.pack(side="right")
            text_color = Colors.TEXT_LIGHT if (status_color and status_color not in {Colors.BG_SOFT_BLUE, Colors.SECONDARY, Colors.WARNING}) else Colors.TEXT_DARK
            ctk.CTkLabel(badge, text=status, font=("Arial", 10, "bold"), text_color=text_color).pack(padx=10, pady=4)

        if secondary:
            ctk.CTkLabel(left, text=secondary, font=("Arial", 11), text_color=Colors.TEXT_MUTED, wraplength=520, justify="left").pack(anchor="w", pady=(4, 0))

        self.create_action_buttons(top, actions or [])
        return card


    def render_dashboard_notice(self, parent, title, message):
        box = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        box.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(box, text=title, font=("Arial", 18, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w", padx=18, pady=(16, 6))
        ctk.CTkLabel(box, text=message, font=("Arial", 12), text_color=Colors.TEXT_MUTED, wraplength=900, justify="left").pack(anchor="w", padx=18, pady=(0, 16))
        return box

    def create_header_actions(self, parent, actions):
        if not actions:
            return None

        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 14))
        for action in actions:
            btn = ctk.CTkButton(
                bar,
                text=action.get('text', 'Action'),
                command=action.get('command'),
                fg_color=action.get('fg_color', Colors.BG_WHITE),
                hover_color=action.get('hover_color', Colors.BG_SOFT_BLUE),
                text_color=action.get('text_color', Colors.TEXT_DARK),
                border_width=action.get('border_width', 1),
                border_color=action.get('border_color', Colors.BORDER),
                corner_radius=12,
                height=36,
                font=("Arial", 12, "bold"),
                width=120,
            )
            btn.pack(side="left", padx=(0, 8))
        return bar


    def handle_section_error(self, message):
        if not getattr(self, 'main_frame', None):
            return
        for child in self.main_frame.winfo_children():
            if getattr(child, '_dashboard_error_notice', False):
                try:
                    child.destroy()
                except Exception:
                    pass
        notice = self.render_dashboard_notice(self.main_frame, "Dashboard Notice", message)
        notice._dashboard_error_notice = True
        try:
            notice.pack_configure(before=self.main_frame.winfo_children()[1] if len(self.main_frame.winfo_children()) > 1 else None)
        except Exception:
            pass

    def create_calendar(self, parent):
        box = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        box.pack(fill="x", pady=(0, 20))

        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day

        month_name = now.strftime("%B %Y")
        ctk.CTkLabel(box, text=month_name, font=("Arial", 17, "bold"), text_color=Colors.TEXT_DARK).pack(pady=(14, 6))

        cal_frame = ctk.CTkFrame(box, fg_color="transparent")
        cal_frame.pack(padx=15, pady=12)

        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ctk.CTkLabel(cal_frame, text=day, font=("Arial", 10, "bold"), text_color=Colors.TEXT_MUTED, width=40).grid(row=0, column=i, padx=3, pady=3)

        cal = calendar.monthcalendar(current_year, current_month)

        for row, week in enumerate(cal, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(cal_frame, text="", width=40, height=32).grid(row=row, column=col, padx=3, pady=3)
                else:
                    if day == current_day:
                        lbl = ctk.CTkLabel(
                            cal_frame,
                            text=str(day),
                            width=40,
                            height=32,
                            fg_color=Colors.SECONDARY,
                            text_color=Colors.TEXT_DARK,
                            corner_radius=10,
                            font=("Arial", 10, "bold"),
                        )
                    else:
                        lbl = ctk.CTkLabel(
                            cal_frame,
                            text=str(day),
                            width=40,
                            height=32,
                            fg_color="transparent",
                            text_color=Colors.TEXT_DARK,
                        )
                    lbl.grid(row=row, column=col, padx=3, pady=3)
