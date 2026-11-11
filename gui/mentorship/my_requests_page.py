import customtkinter as ctk

from colors import Colors
from gui.ui_helpers import ask_confirm, show_error, show_success
from .dialogs import MentorshipChatDialog, MentorshipReviewDialog, RequestDetailsDialog


class MyRequestsPage:
    """Premium mentorship request list with live database-backed actions."""

    STATUS_STYLES = {
        'pending': (Colors.WARNING, 'Pending'),
        'accepted': (Colors.SUCCESS, 'Accepted'),
        'rejected': (Colors.DANGER, 'Rejected'),
        'completed': (Colors.SECONDARY, 'Completed'),
        'cancelled': (Colors.TEXT_SOFT, 'Cancelled'),
    }

    def __init__(self, parent, user, db, role_type='mentee', on_updated=None):
        self.parent = parent
        self.user = user
        self.db = db
        self.role_type = role_type
        self.on_updated = on_updated
        self.requests_cache = []
        self.filtered_requests = []

        self.setup_ui()
        self.load_requests()

    def setup_ui(self):
        self.main = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main.pack(fill="both", expand=True)

        self._build_header()
        self._build_summary_row()
        self._build_filter_bar()
        self._build_list_area()

    def _build_header(self):
        title = "📨 Incoming Requests" if self.role_type == 'mentor' else "📤 Outgoing Requests"
        subtitle = (
            "Review new mentorship requests, respond quickly, and keep mentor-side actions synced."
            if self.role_type == 'mentor'
            else "Track every request you sent, see status updates, and jump back into live conversations."
        )

        hero = ctk.CTkFrame(self.main, fg_color=Colors.BG_WHITE, corner_radius=20, border_width=1, border_color=Colors.BORDER)
        hero.pack(fill="x", padx=16, pady=(8, 12))
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=18, pady=16)
        ctk.CTkLabel(left, text=title, font=("Arial", 24, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(
            left,
            text=subtitle,
            font=("Arial", 12),
            text_color=Colors.TEXT_MUTED,
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        action = ctk.CTkFrame(hero, fg_color=Colors.BG_SOFT_BLUE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        action.grid(row=0, column=1, sticky="e", padx=18, pady=16)
        ctk.CTkLabel(action, text="Live status", font=("Arial", 11, "bold"), text_color=Colors.TEXT_MUTED).pack(padx=16, pady=(10, 2))
        self.live_status_label = ctk.CTkLabel(action, text="Waiting for sync", font=("Arial", 14, "bold"), text_color=Colors.PRIMARY)
        self.live_status_label.pack(padx=16, pady=(0, 10))

    def _build_summary_row(self):
        self.summary_row = ctk.CTkFrame(self.main, fg_color="transparent")
        self.summary_row.pack(fill="x", padx=16, pady=(0, 12))
        for i in range(4):
            self.summary_row.grid_columnconfigure(i, weight=1)

        self.summary_cards = {
            'total': self._create_summary_card(self.summary_row, 0, "Total", "0", "All requests in this view"),
            'pending': self._create_summary_card(self.summary_row, 1, "Pending", "0", "Awaiting action"),
            'active': self._create_summary_card(self.summary_row, 2, "Active", "0", "Accepted or completed"),
            'visible': self._create_summary_card(self.summary_row, 3, "Visible Now", "0", "Filtered results on screen"),
        }

    def _create_summary_card(self, parent, column, label, value, caption):
        card = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        card.grid(row=0, column=column, padx=(0 if column == 0 else 6, 0), pady=0, sticky="nsew")
        ctk.CTkLabel(card, text=label, font=("Arial", 12, "bold"), text_color=Colors.TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 4))
        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"), text_color=Colors.TEXT_DARK)
        value_label.pack(anchor="w", padx=16)
        caption_label = ctk.CTkLabel(card, text=caption, font=("Arial", 11), text_color=Colors.TEXT_SOFT, wraplength=180, justify="left")
        caption_label.pack(anchor="w", padx=16, pady=(2, 12))
        return value_label

    def _build_filter_bar(self):
        bar = ctk.CTkFrame(self.main, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.BORDER)
        bar.pack(fill="x", padx=16, pady=(0, 12))
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=16, pady=14)
        ctk.CTkLabel(left, text="Filter by status", font=("Arial", 12, "bold"), text_color=Colors.TEXT_DARK).pack(anchor="w")

        filters = ctk.CTkFrame(left, fg_color="transparent")
        filters.pack(anchor="w", pady=(8, 0))
        self.filter_var = ctk.StringVar(value="All")
        for i, filter_text in enumerate(["All", "Pending", "Accepted", "Rejected", "Completed", "Cancelled"]):
            ctk.CTkRadioButton(
                filters,
                text=filter_text,
                variable=self.filter_var,
                value=filter_text,
                command=self.filter_requests,
                font=("Arial", 12),
                text_color=Colors.TEXT_DARK,
                fg_color=Colors.PRIMARY,
                hover_color=Colors.BG_HOVER,
            ).pack(side="left", padx=(0 if i == 0 else 16, 0))

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=16, pady=14)
        self.result_label = ctk.CTkLabel(right, text="0 requests", font=("Arial", 12), text_color=Colors.TEXT_MUTED)
        self.result_label.pack(anchor="e", pady=(0, 8))
        ctk.CTkButton(right, text="Refresh", width=110, height=36, fg_color=Colors.SECONDARY, hover_color=Colors.PRIMARY, command=self.load_requests).pack(anchor="e")

    def _build_list_area(self):
        self.requests_frame = ctk.CTkScrollableFrame(
            self.main,
            fg_color="transparent",
            scrollbar_button_color=Colors.SECONDARY,
            scrollbar_button_hover_color=Colors.PRIMARY,
        )
        self.requests_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    def refresh(self):
        self.load_requests()

    def load_requests(self):
        db_role = 'mentor' if self.role_type == 'mentor' else 'mentee'
        self.requests_cache = self.db.get_mentorship_requests(self.user['user_id'], db_role) or []
        self.live_status_label.configure(text="Synced with database")
        self._update_summary_counts()
        self.filter_requests()

    def _update_summary_counts(self):
        total = len(self.requests_cache)
        pending = sum(1 for req in self.requests_cache if str(req.get('status', '')).lower() == 'pending')
        active = sum(1 for req in self.requests_cache if str(req.get('status', '')).lower() in ('accepted', 'completed'))
        self.summary_cards['total'].configure(text=str(total))
        self.summary_cards['pending'].configure(text=str(pending))
        self.summary_cards['active'].configure(text=str(active))

    def filter_requests(self):
        value = self.filter_var.get().lower()
        self.filtered_requests = self.requests_cache if value == 'all' else [req for req in self.requests_cache if str(req.get('status', '')).lower() == value]
        self.summary_cards['visible'].configure(text=str(len(self.filtered_requests)))
        self.result_label.configure(text=f"{len(self.filtered_requests)} request{'s' if len(self.filtered_requests) != 1 else ''}")
        self.render_requests(self.filtered_requests)

    def render_requests(self, requests):
        for widget in self.requests_frame.winfo_children():
            widget.destroy()

        if not requests:
            self._render_empty_state()
            return

        for index, req in enumerate(requests, 1):
            self.create_request_card(req, index)

    def _render_empty_state(self):
        card = ctk.CTkFrame(self.requests_frame, fg_color=Colors.BG_WHITE, corner_radius=20, border_width=1, border_color=Colors.BORDER, height=220)
        card.pack(fill="x", pady=10)
        card.pack_propagate(False)
        message = (
            "You do not have any incoming mentorship requests yet. Once members reach out, their requests will appear here with full details and live actions."
            if self.role_type == 'mentor'
            else "You have not sent any mentorship requests yet. Browse mentors, send a request, and track every update here in real time."
        )
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True)
        ctk.CTkLabel(inner, text="No requests to show", font=("Arial", 20, "bold"), text_color=Colors.TEXT_DARK).pack(pady=(0, 8))
        ctk.CTkLabel(inner, text=message, font=("Arial", 12), text_color=Colors.TEXT_MUTED, wraplength=760, justify="center").pack()

    def create_request_card(self, req, index):
        status_key = str(req.get('status', '')).lower()
        status_color, status_text = self.STATUS_STYLES.get(status_key, (Colors.TEXT_SOFT, status_key.title() or 'Unknown'))
        subject = req.get('subject', 'Mentorship Request')
        other_name = req.get('other_name', 'Unknown Member')
        other_role = str(req.get('other_role') or '').replace('_', ' ').title() or 'Member'
        major = req.get('other_major') or req.get('other_dept') or 'General Studies'
        message_preview = (req.get('message') or '').strip() or 'No introductory message was provided for this request.'
        if len(message_preview) > 165:
            message_preview = message_preview[:162] + '...'

        created_at = req.get('created_at')
        created_text = created_at.strftime('%Y-%m-%d') if hasattr(created_at, 'strftime') else str(created_at or '—')

        card = ctk.CTkFrame(self.requests_frame, fg_color=Colors.BG_WHITE, corner_radius=20, border_width=1, border_color=Colors.BORDER)
        card.pack(fill="x", pady=8)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        top = ctk.CTkFrame(left, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"#{index}", font=("Arial", 12, "bold"), text_color=Colors.TEXT_SOFT).pack(side="left")
        ctk.CTkLabel(top, text=subject, font=("Arial", 17, "bold"), text_color=Colors.TEXT_DARK).pack(side="left", padx=(10, 0))

        badges = ctk.CTkFrame(left, fg_color="transparent")
        badges.pack(anchor="w", pady=(10, 8))
        self._badge(badges, f"With {other_name}", Colors.BG_SOFT_BLUE, Colors.TEXT_DARK)
        self._badge(badges, other_role, Colors.ACCENT, Colors.PRIMARY)
        self._badge(badges, status_text, status_color, Colors.BG_WHITE)

        meta = f"Major / Department: {major}   •   Created: {created_text}"
        ctk.CTkLabel(left, text=meta, font=("Arial", 11), text_color=Colors.TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(left, text=message_preview, font=("Arial", 12), text_color=Colors.TEXT_DARK, wraplength=720, justify="left").pack(anchor="w", pady=(10, 0))

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.grid(row=0, column=1, sticky="ne", padx=16, pady=16)
        self._build_actions(right, req)

    def _badge(self, parent, text, bg, fg):
        label = ctk.CTkLabel(parent, text=text, font=("Arial", 11, "bold"), fg_color=bg, text_color=fg, corner_radius=999)
        label.pack(side="left", padx=(0, 8), pady=(0, 2), ipadx=10, ipady=4)

    def _build_actions(self, parent, req):
        ctk.CTkButton(parent, text="View", width=98, height=34, fg_color=Colors.SECONDARY, hover_color=Colors.PRIMARY, command=lambda r=req: self.view_request(r)).pack(fill="x", pady=(0, 8))

        status = str(req.get('status', '')).lower()
        if self.role_type == 'mentor' and status == 'pending':
            ctk.CTkButton(parent, text="Accept", width=98, height=34, fg_color=Colors.SUCCESS, command=lambda r=req: self.accept_request(r)).pack(fill="x", pady=(0, 8))
            ctk.CTkButton(parent, text="Reject", width=98, height=34, fg_color=Colors.DANGER, command=lambda r=req: self.reject_request(r)).pack(fill="x")
        elif self.role_type == 'mentee' and status == 'pending':
            ctk.CTkButton(parent, text="Cancel", width=98, height=34, fg_color=Colors.DANGER, command=lambda r=req: self.cancel_request(r)).pack(fill="x")
        elif status in ('accepted', 'completed'):
            ctk.CTkButton(parent, text="Chat", width=98, height=34, fg_color=Colors.SUCCESS, command=lambda r=req: self.message(r)).pack(fill="x", pady=(0, 8))
            if status == 'completed':
                ctk.CTkButton(parent, text="Review", width=98, height=34, fg_color=Colors.WARNING, text_color=Colors.TEXT_DARK, command=lambda r=req: self.review(r)).pack(fill="x")

    def accept_request(self, req):
        if not ask_confirm("Accept this mentorship request?"):
            return
        if self.db.update_request_status(req['request_id'], 'accepted', self.user['user_id']):
            show_success("Request accepted!")
            self.after_action()
        else:
            show_error("Unable to accept this request.")

    def reject_request(self, req):
        if not ask_confirm("Reject this mentorship request?"):
            return
        if self.db.update_request_status(req['request_id'], 'rejected', self.user['user_id']):
            show_success("Request rejected.")
            self.after_action()
        else:
            show_error("Unable to reject this request.")

    def cancel_request(self, req):
        if not ask_confirm("Cancel this request?"):
            return
        if self.db.update_request_status(req['request_id'], 'cancelled', self.user['user_id']):
            show_success("Request cancelled.")
            self.after_action()
        else:
            show_error("Unable to cancel this request.")

    def message(self, req):
        MentorshipChatDialog(self.parent, self.user, self.db, req, on_updated=self.after_action)

    def review(self, req):
        MentorshipReviewDialog(self.parent, self.user, self.db, req, self.role_type == 'mentor', on_saved=self.after_action)

    def view_request(self, req):
        RequestDetailsDialog(self.parent, self.user, self.db, req, on_updated=self.after_action)

    def after_action(self):
        self.load_requests()
        if callable(self.on_updated):
            self.on_updated()
