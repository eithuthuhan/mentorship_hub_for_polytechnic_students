import tkinter as tk
from datetime import datetime, timedelta

from colors import Colors


class NotificationSystem:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.notifications = []
        self.window = None

    def check_notifications(self):
        """Check for new notifications."""
        notifications = []

        requests_as_teacher = self._safe_call(self.db.get_mentorship_requests, self.user_id, "teacher", default=[])
        pending_mentor = [request for request in requests_as_teacher if request.get("status") == "pending"]
        if pending_mentor:
            notifications.append({
                "type": "mentor_request",
                "title": "New Mentorship Request",
                "message": f"You have {len(pending_mentor)} pending mentorship request(s)",
                "count": len(pending_mentor),
            })

        requests_as_mentee = self._safe_call(self.db.get_mentorship_requests, self.user_id, "mentee", default=[])
        accepted = [request for request in requests_as_mentee if request.get("status") == "accepted"]
        if accepted:
            notifications.append({
                "type": "mentorship_accepted",
                "title": "Mentorship Accepted",
                "message": f"{len(accepted)} of your mentorship requests have been accepted",
                "count": len(accepted),
            })

        events = self._safe_call(self.db.get_events, default=[])
        today = datetime.now().date()
        upcoming = []
        for event in events:
            event_date = self._parse_date(event.get("start_date"))
            if not event_date:
                continue

            days_until = (event_date - today).days
            if 0 <= days_until <= 3:
                upcoming.append(event)

        if upcoming:
            notifications.append({
                "type": "event",
                "title": "Upcoming Events",
                "message": f"You have {len(upcoming)} events in the next 3 days",
                "count": len(upcoming),
            })

        unread_count = self._safe_call(self.db.get_unread_message_count, self.user_id, default=0)
        if unread_count > 0:
            notifications.append({
                "type": "message",
                "title": "Unread Messages",
                "message": f"You have {unread_count} unread message(s)",
                "count": unread_count,
            })

        announcements = self._safe_call(self.db.get_announcements, default=[])
        one_day_ago = datetime.now() - timedelta(days=1)
        new_announcements = []
        for announcement in announcements:
            published_at = self._parse_datetime(announcement.get("published_at"))
            if published_at and published_at > one_day_ago:
                new_announcements.append(announcement)

        if new_announcements:
            notifications.append({
                "type": "announcement",
                "title": "New Announcements",
                "message": f"There are {len(new_announcements)} new announcement(s)",
                "count": len(new_announcements),
            })

        return notifications

    def _safe_call(self, func, *args, default=None):
        try:
            return func(*args)
        except Exception as error:
            print(f"Notification data error: {error}")
            return default

    def _parse_date(self, value):
        if hasattr(value, "date"):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None
        return value

    def _parse_datetime(self, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None

    def show_notification(self, title, message, notification_type="info"):
        """Show toast notification."""
        if self.window and self.window.winfo_exists():
            self.window.destroy()

        self.window = tk.Toplevel()
        self.window.title("")
        self.window.geometry("320x120")
        self.window.overrideredirect(True)

        if notification_type == "mentor_request":
            bg_color = Colors.SUCCESS
        elif notification_type == "message":
            bg_color = Colors.SECONDARY
        elif notification_type == "event":
            bg_color = Colors.WARNING
        elif notification_type == "announcement":
            bg_color = Colors.INFO
        else:
            bg_color = Colors.SECONDARY

        self.window.configure(bg=bg_color)
        self.window.update_idletasks()
        x = self.window.winfo_screenwidth() - 340
        y = 10
        self.window.geometry(f"+{x}+{y}")

        close_btn = tk.Label(self.window, text="✕", font=("Arial", 10, "bold"), fg="white", bg=bg_color, cursor="hand2")
        close_btn.place(x=300, y=5)
        close_btn.bind("<Button-1>", lambda _event: self.window.destroy())

        icons = {
            "mentor_request": "🤝",
            "mentorship_accepted": "✅",
            "message": "💬",
            "event": "📅",
            "announcement": "📢",
            "info": "🔔",
        }
        icon = icons.get(notification_type, "🔔")

        tk.Label(self.window, text=icon, font=("Arial", 24), fg="white", bg=bg_color).pack(pady=(10, 0))
        tk.Label(self.window, text=title, font=("Arial", 12, "bold"), fg="white", bg=bg_color).pack()
        tk.Label(self.window, text=message, font=("Arial", 10), fg="white", bg=bg_color, wraplength=280).pack(pady=(0, 10))

        self.window.after(5000, self.safe_destroy)

    def safe_destroy(self):
        """Safely destroy notification window if it exists."""
        if not self.window:
            return

        try:
            if self.window.winfo_exists():
                self.window.destroy()
        except tk.TclError:
            return
        finally:
            self.window = None

    def create_notification_center(self, parent):
        """Create notification center UI."""
        frame = tk.Frame(parent, bg=Colors.BG_WHITE, relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.X, padx=20, pady=10)

        header = tk.Frame(frame, bg=Colors.PRIMARY)
        header.pack(fill=tk.X)

        tk.Label(header, text="🔔 Notifications", font=("Arial", 12, "bold"), fg="white", bg=Colors.PRIMARY).pack(side=tk.LEFT, padx=10, pady=5)

        self.unread_count = tk.Label(header, text="0", font=("Arial", 10, "bold"), bg=Colors.DANGER, fg="white", padx=5)
        self.unread_count.pack(side=tk.LEFT, padx=5)

        refresh_btn = tk.Label(header, text="↻", font=("Arial", 14), fg="white", bg=Colors.PRIMARY, cursor="hand2")
        refresh_btn.pack(side=tk.RIGHT, padx=10)
        refresh_btn.bind("<Button-1>", lambda _event: self.refresh_notifications())

        mark_btn = tk.Label(header, text="✓ All", font=("Arial", 10), fg="white", bg=Colors.PRIMARY, cursor="hand2")
        mark_btn.pack(side=tk.RIGHT, padx=5)
        mark_btn.bind("<Button-1>", lambda _event: self.mark_all_read())

        self.notif_content = tk.Frame(frame, bg=Colors.BG_WHITE)
        self.notif_content.pack(fill=tk.X, padx=10, pady=10)

        self.refresh_notifications()

    def refresh_notifications(self):
        """Refresh notification list."""
        for widget in self.notif_content.winfo_children():
            widget.destroy()

        notifications = self.check_notifications()
        total_unread = sum(notification.get("count", 0) for notification in notifications)
        self.unread_count.config(text=str(total_unread))

        if not notifications:
            empty_frame = tk.Frame(self.notif_content, bg=Colors.BG_WHITE, height=60)
            empty_frame.pack(fill=tk.X)
            tk.Label(empty_frame, text="✨ No new notifications", font=("Arial", 10), fg=Colors.TEXT_MUTED, bg=Colors.BG_WHITE).pack(pady=15)
            return

        for notification in notifications:
            self.create_notification_item(self.notif_content, notification)

    def create_notification_item(self, parent, notif):
        """Create a notification item."""
        colors = {
            "mentor_request": Colors.SUCCESS,
            "mentorship_accepted": "#7FC8A9",
            "message": Colors.SECONDARY,
            "event": Colors.WARNING,
            "announcement": Colors.INFO,
        }
        dot_color = colors.get(notif["type"], Colors.SECONDARY)

        item = tk.Frame(parent, bg=Colors.BG_LIGHT, relief=tk.FLAT, bd=1)
        item.pack(fill=tk.X, pady=2)

        strip = tk.Frame(item, bg=dot_color, width=5)
        strip.pack(side=tk.LEFT, fill=tk.Y)

        content = tk.Frame(item, bg=Colors.BG_LIGHT)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)

        tk.Label(content, text=notif["title"], font=("Arial", 10, "bold"), fg=Colors.TEXT_DARK, bg=Colors.BG_LIGHT).pack(anchor="w")
        tk.Label(content, text=notif["message"], font=("Arial", 9), fg=Colors.TEXT_MUTED, bg=Colors.BG_LIGHT, wraplength=350, justify="left").pack(anchor="w", pady=(2, 0))

    def mark_all_read(self):
        """Refresh notifications after user clears current view."""
        self.refresh_notifications()
