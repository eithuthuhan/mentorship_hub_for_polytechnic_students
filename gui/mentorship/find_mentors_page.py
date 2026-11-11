import customtkinter as ctk

from gui.ui_helpers import require_text, show_error, show_success


class FindMentorsPage:
    """Premium mentor directory with live database-backed actions."""

    def __init__(self, parent, user, db, on_updated=None):
        self.parent = parent
        self.user = user
        self.db = db
        self.on_updated = on_updated
        self.mentors = []
        self.department_options = ["All"]

        self.setup_ui()
        self.load_filter_options()
        self.load_mentors()

    def setup_ui(self):
        self.main = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main.pack(fill="both", expand=True)

        hero = ctk.CTkFrame(self.main, fg_color="#EEF5FF", corner_radius=16, border_width=1, border_color="#D7E6F7")
        hero.pack(fill="x", pady=(0, 16))

        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(18, 12), pady=16)
        ctk.CTkLabel(left, text="🔍 Find Mentors", font=("Arial", 24, "bold"), text_color="#1F3B5B").pack(anchor="w")
        self.hero_subtitle = ctk.CTkLabel(
            left,
            text=self.get_role_message(),
            font=("Arial", 12),
            text_color="#5F7693",
            justify="left",
            wraplength=760,
            anchor="w",
        )
        self.hero_subtitle.pack(anchor="w", pady=(6, 0))

        right = ctk.CTkFrame(hero, fg_color="white", corner_radius=14, border_width=1, border_color="#D7E6F7", width=140, height=110)
        right.grid(row=0, column=1, sticky="ne", padx=(0, 18), pady=16)
        right.grid_propagate(False)
        self.results_count_label = ctk.CTkLabel(right, text="0", font=("Arial", 26, "bold"), text_color="#6AA7FF")
        self.results_count_label.pack(padx=12, pady=(16, 0))
        ctk.CTkLabel(right, text="available\nmentors", font=("Arial", 11), text_color="#6F8098", justify="center").pack(padx=8, pady=(8, 12))

        toolbar = ctk.CTkFrame(self.main, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 14))

        search_wrap = ctk.CTkFrame(toolbar, fg_color="white", corner_radius=14, border_width=1, border_color="#D7E6F7")
        search_wrap.pack(side="left", fill="x", expand=True)
        self.search_entry = ctk.CTkEntry(
            search_wrap,
            height=42,
            font=("Arial", 12),
            placeholder_text="Search by mentor name, bio, major, or skill...",
            border_width=0,
            fg_color="white",
            text_color="#1F3B5B",
            width=260,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=8)
        self.search_entry.bind("<Return>", lambda _event: self.search_mentors())

        ctk.CTkButton(search_wrap, text="Search", width=92, height=34, fg_color="#84B6FF", command=self.search_mentors).pack(side="left", padx=4)
        ctk.CTkButton(search_wrap, text="Clear", width=78, height=34, fg_color="#AEBFD1", command=self.clear_search).pack(side="left", padx=(4, 10))

        filter_wrap = ctk.CTkFrame(toolbar, fg_color="white", corner_radius=14, border_width=1, border_color="#D7E6F7")
        filter_wrap.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(filter_wrap, text="Major", font=("Arial", 12, "bold"), text_color="#1F3B5B").pack(side="left", padx=(12, 8))
        self.dept_var = ctk.StringVar(value="All")
        self.dept_combo = ctk.CTkComboBox(
            filter_wrap,
            width=180,
            values=self.department_options,
            variable=self.dept_var,
            command=lambda _choice: self.load_mentors(),
            button_color="#84B6FF",
            border_color="#D7E6F7",
        )
        self.dept_combo.pack(side="left", padx=(0, 10), pady=8)
        ctk.CTkButton(filter_wrap, text="Refresh", width=88, height=34, fg_color="#7FC8A9", command=self.load_mentors).pack(side="left", padx=(0, 10))

        self.mentors_frame = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        self.mentors_frame.pack(fill="both", expand=True)
        self.mentors_frame.grid_columnconfigure(0, weight=1)
        self.mentors_frame.grid_columnconfigure(1, weight=1)

    def get_role_message(self):
        role = self.user.get("role")
        if role == "junior_student":
            return "Explore teachers and senior students who can guide your learning journey, project growth, and career direction."
        if role == "senior_student":
            return "Find teachers who can support advanced work, capstone planning, research direction, and professional growth."
        if role == "teacher":
            return "Browse senior students for mentoring collaboration, project supervision support, and knowledge sharing."
        return "Browse the live mentor directory and open detailed profiles before sending a mentorship request."

    def refresh(self):
        self.load_filter_options()
        self.load_mentors()

    def load_filter_options(self):
        options = ["All"]
        if self.db:
            departments = self.db.get_available_mentor_departments(self.user["user_id"]) or []
            options.extend([item for item in departments if item not in options])
        self.department_options = options
        if hasattr(self, "dept_combo"):
            self.dept_combo.configure(values=self.department_options)
            if self.dept_var.get() not in self.department_options:
                self.dept_var.set("All")

    def load_mentors(self):
        for widget in self.mentors_frame.winfo_children():
            widget.destroy()

        search = self.search_entry.get().strip() or None
        department = self.dept_var.get() if self.dept_var.get() != "All" else None
        self.mentors = self.db.get_mentors(self.user["user_id"], search, department) or []
        self.results_count_label.configure(text=str(len(self.mentors)))

        if not self.mentors:
            self.render_empty_state(search, department)
            return

        for i, mentor in enumerate(self.mentors):
            self.create_mentor_card(self.mentors_frame, mentor, i // 2, i % 2)

    def render_empty_state(self, search, department):
        card = ctk.CTkFrame(self.mentors_frame, fg_color="white", corner_radius=16, border_width=1, border_color="#D7E6F7")
        card.pack(fill="both", expand=True, pady=30, padx=12)
        ctk.CTkLabel(card, text="No mentors matched your current search", font=("Arial", 18, "bold"), text_color="#1F3B5B").pack(pady=(34, 8))
        detail = "Try broader keywords, clear the major filter, or refresh the directory to fetch the latest mentor profiles from the database."
        if search or department:
            detail = "The current search and filter combination did not return any mentors. Clear the filters to see everyone available right now."
        ctk.CTkLabel(card, text=detail, font=("Arial", 12), text_color="#6F8098", wraplength=600, justify="center").pack(padx=20, pady=(0, 16))
        ctk.CTkButton(card, text="Clear Filters", width=140, fg_color="#84B6FF", command=self.clear_search).pack(pady=(0, 34))

    def create_mentor_card(self, parent, mentor, row, col):
        relationship = self.db.get_relationship_request(self.user["user_id"], mentor["user_id"])
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=16, border_width=1, border_color="#D7E6F7")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 10))

        avatar_color = "#6AA7FF" if mentor.get("role") == "teacher" else "#7FC8A9"
        ctk.CTkLabel(header, text="👤", font=("Arial", 28), fg_color=avatar_color, text_color="white", width=58, height=58, corner_radius=29).pack(side="left")

        title_wrap = ctk.CTkFrame(header, fg_color="transparent")
        title_wrap.pack(side="left", fill="x", expand=True, padx=(12, 0))
        ctk.CTkLabel(title_wrap, text=mentor.get("full_name", "Mentor"), font=("Arial", 16, "bold"), text_color="#1F3B5B").pack(anchor="w")
        role_text = "Teacher" if mentor.get("role") == "teacher" else "Senior Student"
        major = mentor.get("major") or mentor.get("department") or "General"
        ctk.CTkLabel(title_wrap, text=f"{role_text} • {major}", font=("Arial", 12), text_color="#6F8098").pack(anchor="w", pady=(2, 0))

        status_text, status_color = self.get_relationship_badge(relationship)
        badge = ctk.CTkLabel(header, text=status_text, font=("Arial", 11, "bold"), text_color=status_color, fg_color="#F7FAFF", corner_radius=10)
        badge.pack(side="right", padx=(8, 0), ipadx=8, ipady=4)

        metrics = ctk.CTkFrame(card, fg_color="#F8FBFF", corner_radius=12)
        metrics.pack(fill="x", padx=16, pady=(0, 12))
        self._metric(metrics, "⭐ Rating", f"{mentor['avg_rating']:.1f}" if mentor.get("avg_rating") else "New")
        self._metric(metrics, "👥 Mentees", str(mentor.get("mentee_count", 0)))
        self._metric(metrics, "🏫 Department", mentor.get("department") or "General")

        skills = mentor.get("skills") or "Mentor skills will appear here as soon as they are added to the profile."
        ctk.CTkLabel(
            card,
            text=skills if len(skills) < 140 else skills[:137] + "...",
            font=("Arial", 11),
            text_color="#35516F",
            wraplength=320,
            justify="left",
        ).pack(fill="x", padx=16)

        bio = (mentor.get("bio") or "This mentor has not written a full bio yet, but you can still open the profile and send a thoughtful request.").strip()
        ctk.CTkLabel(
            card,
            text=bio if len(bio) < 180 else bio[:177] + "...",
            font=("Arial", 11),
            text_color="#6F8098",
            wraplength=320,
            justify="left",
        ).pack(fill="x", padx=16, pady=(10, 8))

        caption = self.get_caption_text(mentor, relationship)
        ctk.CTkLabel(card, text=caption, font=("Arial", 11, "italic"), text_color="#4F6786", wraplength=320, justify="left").pack(fill="x", padx=16, pady=(0, 10))

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))
        ctk.CTkButton(btn_frame, text="View Profile", width=106, fg_color="#84B6FF", command=lambda m=mentor: self.view_profile(m)).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btn_frame, text="Preview", width=92, fg_color="#C8DDFC", text_color="#1F3B5B", command=lambda m=mentor, r=relationship: self.show_preview_dialog(m, r)).pack(side="left", padx=6)

        action_text, action_state, action_cmd, action_color = self.get_primary_action(mentor, relationship)
        ctk.CTkButton(btn_frame, text=action_text, width=112, state=action_state, fg_color=action_color, command=action_cmd).pack(side="right")

    def _metric(self, parent, label, value):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        ctk.CTkLabel(item, text=label, font=("Arial", 11), text_color="#6F8098").pack(anchor="w")
        ctk.CTkLabel(item, text=value, font=("Arial", 13, "bold"), text_color="#1F3B5B").pack(anchor="w", pady=(2, 0))

    def get_caption_text(self, mentor, relationship):
        if relationship:
            status = (relationship.get("status") or "").lower()
            if status == "pending":
                return "A request already exists between both members. Keep the conversation focused and wait for the next decision update."
            if status == "accepted":
                return "This mentoring connection is active in the database. Open the chat or schedule a session from the mentorship area."
            if status == "completed":
                return "You already have mentoring history with this member, so you can continue the conversation and review the experience."
        role_text = "teacher" if mentor.get("role") == "teacher" else "senior student"
        return f"This {role_text} can be a strong match for guidance, project support, study planning, and practical growth based on the current profile data."

    def get_relationship_badge(self, relationship):
        if not relationship:
            return "Ready for new request", "#6AA7FF"
        status = (relationship.get("status") or "").lower()
        mapping = {
            "pending": ("Pending in database", "#D59B22"),
            "accepted": ("Active mentorship", "#3D9B75"),
            "completed": ("Completed history", "#6B7DFF"),
            "rejected": ("Last request rejected", "#D16B6B"),
            "cancelled": ("Previous request cancelled", "#8C9BB0"),
        }
        return mapping.get(status, (status.title(), "#95A4B8"))

    def get_primary_action(self, mentor, relationship):
        if relationship:
            status = (relationship.get("status") or "").lower()
            if status == "pending":
                if relationship.get("mentee_id") == self.user["user_id"]:
                    return "Pending", "disabled", self.load_mentors, "#AEBFD1"
                return "Waiting", "disabled", self.load_mentors, "#AEBFD1"
            if status in ("accepted", "completed"):
                from .dialogs import MentorshipChatDialog
                return "Open Chat", "normal", lambda r=relationship: MentorshipChatDialog(self.parent, self.user, self.db, r, on_updated=self.after_action), "#7FC8A9"
        return "Send Request", "normal", lambda m=mentor: self.request_mentor(m), "#7FC8A9"

    def after_action(self):
        self.load_mentors()
        if callable(self.on_updated):
            self.on_updated()

    def show_preview_dialog(self, mentor, relationship):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Mentor Preview")
        dialog.geometry("560x560")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(250, lambda: dialog.attributes("-topmost", False))

        wrap = ctk.CTkScrollableFrame(dialog, fg_color="#F8FBFF")
        wrap.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(wrap, text=mentor.get("full_name", "Mentor"), font=("Arial", 22, "bold"), text_color="#1F3B5B").pack(anchor="w", pady=(4, 2))
        role_text = "Teacher" if mentor.get("role") == "teacher" else "Senior Student"
        ctk.CTkLabel(wrap, text=f"{role_text} • {mentor.get('major') or mentor.get('department') or 'General'}", font=("Arial", 13), text_color="#6F8098").pack(anchor="w", pady=(0, 10))

        status_text, status_color = self.get_relationship_badge(relationship)
        ctk.CTkLabel(wrap, text=status_text, font=("Arial", 12, "bold"), text_color=status_color).pack(anchor="w", pady=(0, 12))

        detail_rows = [
            ("Department", mentor.get("department") or "General"),
            ("Email", mentor.get("email") or "Not visible"),
            ("Current mentees", str(mentor.get("mentee_count", 0))),
            ("Average rating", f"{mentor['avg_rating']:.1f}" if mentor.get("avg_rating") else "New mentor"),
        ]
        info_card = ctk.CTkFrame(wrap, fg_color="white", corner_radius=14, border_width=1, border_color="#D7E6F7")
        info_card.pack(fill="x", pady=(0, 12))
        for label, value in detail_rows:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=8)
            ctk.CTkLabel(row, text=label, font=("Arial", 12, "bold"), text_color="#1F3B5B").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Arial", 12), text_color="#6F8098").pack(side="right")

        self._preview_section(wrap, "Skills and strengths", mentor.get("skills") or "No detailed skills have been added yet, but you can still view the full profile and send a thoughtful request explaining your goals.")
        self._preview_section(wrap, "About this mentor", mentor.get("bio") or "This mentor has not completed the full profile biography yet. You can still connect by writing a clear request that explains what kind of support you need.")
        self._preview_section(
            wrap,
            "Good request ideas",
            "Mention your academic goal, the project or subject you need help with, what kind of support you expect, and how often you hope to meet. Clear requests usually get better responses.",
        )

        btn_row = ctk.CTkFrame(wrap, fg_color="transparent")
        btn_row.pack(fill="x", pady=(8, 4))
        ctk.CTkButton(btn_row, text="Open Profile", fg_color="#84B6FF", command=lambda m=mentor: [dialog.destroy(), self.view_profile(m)]).pack(side="left", expand=True, fill="x", padx=(0, 6))
        action_text, action_state, action_cmd, action_color = self.get_primary_action(mentor, relationship)
        ctk.CTkButton(btn_row, text=action_text, state=action_state, fg_color=action_color, command=lambda: [dialog.destroy(), action_cmd()]).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _preview_section(self, parent, title, body):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=14, border_width=1, border_color="#D7E6F7")
        card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color="#1F3B5B").pack(anchor="w", padx=14, pady=(12, 6))
        ctk.CTkLabel(card, text=body, font=("Arial", 12), text_color="#4F6786", wraplength=470, justify="left").pack(anchor="w", padx=14, pady=(0, 12))

    def view_profile(self, mentor):
        from gui.profile.view_profile_page import ViewProfilePage
        ViewProfilePage(self.parent, self.user, self.db, mentor["user_id"])

    def request_mentor(self, mentor):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Send Mentorship Request")
        dialog.geometry("470x500")
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(250, lambda: dialog.attributes("-topmost", False))

        ctk.CTkLabel(dialog, text=f"Request {mentor['full_name']}", font=("Arial", 20, "bold"), text_color="#1F3B5B").pack(pady=(20, 8))
        ctk.CTkLabel(dialog, text="Write a clear subject and message so the other member can understand your goals and respond faster.", font=("Arial", 12), text_color="#6F8098", wraplength=390, justify="center").pack(padx=20)
        ctk.CTkLabel(dialog, text="Subject", anchor="w").pack(fill="x", padx=24, pady=(14, 5))
        subject_entry = ctk.CTkEntry(dialog, width=380, height=38)
        subject_entry.pack(padx=24, fill="x")
        ctk.CTkLabel(dialog, text="Message", anchor="w").pack(fill="x", padx=24, pady=(12, 5))
        message_box = ctk.CTkTextbox(dialog, width=380, height=170)
        message_box.pack(padx=24, fill="both", expand=True)

        def submit_request():
            try:
                subject = require_text(subject_entry.get(), "Subject")
                message = require_text(message_box.get("1.0", "end-1c"), "Message")
            except ValueError as exc:
                show_error(str(exc))
                return

            request_id = self.db.create_mentorship_request(mentor["user_id"], self.user["user_id"], subject, message)
            if request_id == -1:
                show_error("Unable to save this mentorship request. It may already exist, the role pairing may not be allowed, or one member may no longer be active.")
                return

            show_success("Mentorship request sent successfully and saved to the database.")
            dialog.destroy()
            self.after_action()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=18)
        ctk.CTkButton(btn_frame, text="Send Request", fg_color="#7FC8A9", command=submit_request).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#F29B9B", command=dialog.destroy).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def search_mentors(self):
        self.load_mentors()

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.dept_var.set("All")
        self.load_mentors()
