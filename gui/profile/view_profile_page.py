import customtkinter as ctk

from gui.ui_helpers import require_text, show_error, show_success, show_info


class ViewProfilePage:
    """Premium read-only profile page for viewing another member."""

    def __init__(self, parent, current_user, db, user_id):
        self.parent = parent
        self.current_user = current_user
        self.db = db
        self.user_id = user_id
        self.user = None
        self.stats = {}
        self.skills = []
        self.projects = []
        self.certs = []
        self.relationship = None

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Member Profile")
        self.window.geometry("1120x760")
        self.window.configure(fg_color="#F6FAFF")
        self.window.transient(parent.winfo_toplevel())
        self.window.grab_set()
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after(250, lambda: self.window.attributes("-topmost", False))
        self.window.focus_force()

        self.center_window(1120, 760)
        self.load_user_data()
        if self.user:
            self.setup_ui()

    def center_window(self, width, height):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def load_user_data(self):
        self.user = self.db.get_user_by_id(self.user_id)
        if not self.user:
            show_error("User not found")
            self.window.destroy()
            return
        self.stats = self.db.get_user_stats(self.user_id) or {}
        self.skills = self.db.get_user_skills(self.user_id) or []
        self.projects = self.db.get_user_projects(self.user_id) or []
        self.certs = self.db.get_user_certifications(self.user_id) or []
        self.relationship = self.db.get_relationship_request(self.current_user['user_id'], self.user_id)

    def refresh(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        self.load_user_data()
        if self.user:
            self.setup_ui()

    def setup_ui(self):
        shell = ctk.CTkFrame(self.window, fg_color="#F6FAFF")
        shell.pack(fill="both", expand=True)

        outer = ctk.CTkScrollableFrame(shell, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=20, pady=18)

        self._create_header(outer)

        layout = ctk.CTkFrame(outer, fg_color="transparent")
        layout.pack(fill="both", expand=True, pady=(14, 0))
        layout.grid_columnconfigure(0, weight=0)
        layout.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(layout, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        right = ctk.CTkFrame(layout, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")

        self._create_identity_card(left)
        self._create_contact_card(left)
        self._create_summary_card(left)
        self._create_connection_card(left)

        self._create_highlight_banner(right)
        self._create_tabbed_content(right)

    def _card(self, parent, pady=(0, 14), corner_radius=20):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=corner_radius, border_width=1, border_color="#D7E6F7")
        card.pack(fill="x", pady=pady)
        return card

    def _header_button(self, parent, text, command, fg="#EEF4FF", text_color="#1F3B5B"):
        return ctk.CTkButton(
            parent,
            text=text,
            height=40,
            corner_radius=14,
            fg_color=fg,
            hover_color="#E1ECFF" if fg != "#78AFFF" else "#5F97EC",
            text_color=text_color,
            command=command,
        )

    def _chip(self, parent, text, fg="#EEF4FF", text_color="#356299"):
        return ctk.CTkLabel(parent, text=text, font=("Arial", 11, "bold"), text_color=text_color, fg_color=fg, corner_radius=999, padx=12, pady=6)

    def _section_title(self, parent, title, subtitle=None):
        ctk.CTkLabel(parent, text=title, font=("Arial", 18, "bold"), text_color="#163B68").pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(parent, text=subtitle, font=("Arial", 11), text_color="#6F8098", wraplength=760, justify="left").pack(anchor="w", pady=(6, 0))

    def _meta_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=label, width=110, anchor="w", font=("Arial", 11, "bold"), text_color="#6F8098").pack(side="left")
        ctk.CTkLabel(row, text=value or "Not provided", anchor="w", font=("Arial", 11), text_color="#163B68", wraplength=250, justify="left").pack(side="left", fill="x", expand=True)

    def _empty_state(self, parent, title, subtitle):
        box = ctk.CTkFrame(parent, fg_color="#F8FBFF", corner_radius=18, border_width=1, border_color="#E1ECFF")
        box.pack(fill="x", pady=10)
        ctk.CTkLabel(box, text=title, font=("Arial", 15, "bold"), text_color="#163B68").pack(pady=(20, 6))
        ctk.CTkLabel(box, text=subtitle, font=("Arial", 11), text_color="#6F8098", wraplength=700, justify="center").pack(padx=18, pady=(0, 18))

    def _create_header(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=24, border_width=1, border_color="#D7E6F7")
        card.pack(fill="x")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=22, pady=20)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(left, text="Member Profile", font=("Arial", 28, "bold"), text_color="#163B68").pack(anchor="w")
        ctk.CTkLabel(
            left,
            text="Explore a richer, real-data profile view with live academic information, verified skills, projects, certifications, and current mentorship relationship status.",
            font=("Arial", 12),
            text_color="#6F8098",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(side="right", anchor="n")
        self._header_button(actions, "View Connection", self.show_relationship_summary).pack(side="left", padx=4)
        if self.relationship and self.relationship.get('status') in ('accepted', 'completed'):
            self._header_button(actions, "Open Chat", self.open_chat, fg="#EAF7F1", text_color="#2E6B4E").pack(side="left", padx=4)
        elif self.user['user_id'] != self.current_user['user_id']:
            self._header_button(actions, "Send Request", self.send_request, fg="#78AFFF", text_color="#FFFFFF").pack(side="left", padx=4)
        self._header_button(actions, "Refresh", self.refresh).pack(side="left", padx=4)
        self._header_button(actions, "Close", self.window.destroy, fg="#FFEDEF", text_color="#9D3A4A").pack(side="left", padx=4)

    def _create_identity_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=22)
        ctk.CTkLabel(body, text="👤", font=("Arial", 52), width=88, height=88, corner_radius=44, fg_color="#78AFFF", text_color="#FFFFFF").pack(anchor="center", pady=(0, 12))
        ctk.CTkLabel(body, text=self.user.get('full_name', 'Member'), font=("Arial", 22, "bold"), text_color="#163B68").pack(anchor="center")
        ctk.CTkLabel(body, text=self.get_role_display(), font=("Arial", 13), text_color="#6A9BDD").pack(anchor="center", pady=(4, 12))

        chips = ctk.CTkFrame(body, fg_color="transparent")
        chips.pack(fill="x", pady=(0, 10))
        self._chip(chips, self.user.get('department') or 'Department not set').pack(side="left", padx=(0, 6))
        if self.user.get('major'):
            self._chip(chips, self.user['major']).pack(side="left", padx=6)
        if self.user.get('year'):
            self._chip(chips, f"Year {self.user['year']}").pack(side="left", padx=6)

        ctk.CTkLabel(body, text=self._build_intro_caption(), font=("Arial", 12), text_color="#60748D", wraplength=290, justify="center").pack(fill="x", pady=(8, 0))

    def _create_contact_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(body, text="Contact & Academic Details", font=("Arial", 16, "bold"), text_color="#163B68").pack(anchor="w", pady=(0, 10))
        self._meta_row(body, "Email", self.user.get('email'))
        self._meta_row(body, "Phone", self.user.get('phone'))
        self._meta_row(body, "Department", self.user.get('department'))
        self._meta_row(body, "Major", self.user.get('major'))
        self._meta_row(body, "Year", str(self.user.get('year') or 'Not set'))

    def _create_summary_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(body, text="Live Profile Snapshot", font=("Arial", 16, "bold"), text_color="#163B68").pack(anchor="w", pady=(0, 12))

        values = [
            ("Skills", len(self.skills)),
            ("Projects", len(self.projects)),
            ("Certificates", len(self.certs)),
            ("Connections", int(self.stats.get('mentor_count', 0) or 0) + int(self.stats.get('mentee_count', 0) or 0)),
        ]
        for label, value in values:
            row = ctk.CTkFrame(body, fg_color="#F8FBFF", corner_radius=14)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label, font=("Arial", 11, "bold"), text_color="#6F8098").pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(row, text=str(value), font=("Arial", 18, "bold"), text_color="#163B68").pack(side="right", padx=12, pady=10)

    def _create_connection_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(body, text="Relationship Status", font=("Arial", 16, "bold"), text_color="#163B68").pack(anchor="w", pady=(0, 10))
        status_text, caption = self._relationship_caption()
        self._chip(body, status_text, fg="#EAF7F1" if "Accepted" in status_text or "Completed" in status_text else "#EEF4FF", text_color="#2E6B4E" if "Accepted" in status_text or "Completed" in status_text else "#356299").pack(anchor="w")
        ctk.CTkLabel(body, text=caption, font=("Arial", 11), text_color="#60748D", wraplength=280, justify="left").pack(anchor="w", pady=(10, 12))
        btns = ctk.CTkFrame(body, fg_color="transparent")
        btns.pack(fill="x")
        if self.relationship and self.relationship.get('status') in ('accepted', 'completed'):
            self._header_button(btns, "Open Chat", self.open_chat, fg="#78AFFF", text_color="#FFFFFF").pack(side="left", fill="x", expand=True, padx=(0, 6))
        elif self.user['user_id'] != self.current_user['user_id']:
            self._header_button(btns, "Send Request", self.send_request, fg="#78AFFF", text_color="#FFFFFF").pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._header_button(btns, "More Details", self.show_relationship_summary).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _create_highlight_banner(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=22, pady=22)
        self._section_title(body, "Professional Highlights", "This summary is built from live database content so the profile stays aligned with real mentorship activity, project work, events, and demonstrated growth.")
        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x", pady=(16, 0))
        values = [
            ("Mentorships", int(self.stats.get('mentor_count', 0) or 0) + int(self.stats.get('mentee_count', 0) or 0), "Active relationships built through the platform."),
            ("Events", int(self.stats.get('event_count', 0) or 0), "Sessions, workshops, and activities this member joined."),
            ("Messages", int(self.stats.get('message_count', 0) or 0), "Real conversation activity recorded in the system."),
            ("Rating", f"{float(self.stats.get('avg_rating', 0) or 0):.1f}", "Average mentorship rating based on submitted reviews."),
        ]
        for i, (label, value, desc) in enumerate(values):
            card_item = ctk.CTkFrame(grid, fg_color="#F7FAFF", corner_radius=16, border_width=1, border_color="#E1ECFF")
            card_item.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0))
            grid.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card_item, text=str(value), font=("Arial", 24, "bold"), text_color="#163B68").pack(anchor="w", padx=16, pady=(14, 2))
            ctk.CTkLabel(card_item, text=label, font=("Arial", 12, "bold"), text_color="#6A9BDD").pack(anchor="w", padx=16)
            ctk.CTkLabel(card_item, text=desc, font=("Arial", 11), text_color="#6F8098", wraplength=165, justify="left").pack(anchor="w", padx=16, pady=(4, 14))

    def _create_tabbed_content(self, parent):
        wrapper = self._card(parent)
        notebook = ctk.CTkTabview(
            wrapper,
            fg_color="#FFFFFF",
            segmented_button_fg_color="#EEF4FF",
            segmented_button_selected_color="#78AFFF",
            segmented_button_selected_hover_color="#5F97EC",
            segmented_button_unselected_color="#EEF4FF",
            segmented_button_unselected_hover_color="#E1ECFF",
            text_color="#1F3B5B",
        )
        notebook.pack(fill="both", expand=True, padx=16, pady=16)
        notebook.add("Overview")
        notebook.add("Skills")
        notebook.add("Projects")
        notebook.add("Certificates")

        overview = notebook.tab("Overview")
        skills_tab = notebook.tab("Skills")
        projects_tab = notebook.tab("Projects")
        certs_tab = notebook.tab("Certificates")

        self._build_overview_tab(overview)
        self._build_skills_tab(skills_tab)
        self._build_projects_tab(projects_tab)
        self._build_certs_tab(certs_tab)

    def _build_overview_tab(self, parent):
        body = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=8, pady=8)
        about_card = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E1ECFF")
        about_card.pack(fill="x", pady=(0, 12))
        inner = ctk.CTkFrame(about_card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=18)
        self._section_title(inner, "About This Member")
        ctk.CTkLabel(inner, text=self.user.get('bio') or "This member has not added a bio yet, but you can still review their real skills, projects, certifications, and relationship status below.", font=("Arial", 11), text_color="#60748D", wraplength=760, justify="left").pack(anchor="w", pady=(8, 0))

        quick = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E1ECFF")
        quick.pack(fill="x", pady=(0, 12))
        quick_inner = ctk.CTkFrame(quick, fg_color="transparent")
        quick_inner.pack(fill="x", padx=18, pady=18)
        self._section_title(quick_inner, "Why Connect With This Member")
        bullets = [
            "Their profile uses real system data, so visible skills and projects reflect actual records saved in the database.",
            "Mentorship relationship status is checked live before request or chat actions are shown.",
            "Projects and certifications help you understand where this member has practical or verified experience.",
        ]
        for bullet in bullets:
            ctk.CTkLabel(quick_inner, text=f"• {bullet}", font=("Arial", 11), text_color="#60748D", wraplength=760, justify="left").pack(anchor="w", pady=3)

    def _build_skills_tab(self, parent):
        body = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=8, pady=8)
        if not self.skills:
            self._empty_state(body, "No skills added yet", "Once this member adds skills, they will appear here with real proficiency, category, and experience information.")
            return
        for skill in self.skills:
            card = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#D7E6F7")
            card.pack(fill="x", pady=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=14)
            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=skill['skill_name'], font=("Arial", 14, "bold"), text_color="#163B68").pack(side="left")
            self._chip(top, (skill.get('proficiency_level') or 'beginner').title()).pack(side="left", padx=8)
            if skill.get('category'):
                self._chip(top, str(skill['category']).replace('_', ' ').title()).pack(side="left")
            ctk.CTkLabel(inner, text=f"Experience: {skill.get('years_experience', 0) or 0} years", font=("Arial", 11), text_color="#6F8098").pack(anchor="w", pady=(8, 0))

    def _build_projects_tab(self, parent):
        body = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=8, pady=8)
        if not self.projects:
            self._empty_state(body, "No projects added yet", "Project records will appear here once this member saves real project data such as technologies, team size, role, and achievements.")
            return
        for project in self.projects:
            card = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#D7E6F7")
            card.pack(fill="x", pady=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=14)
            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=project['project_name'], font=("Arial", 15, "bold"), text_color="#163B68").pack(side="left")
            if project.get('is_current'):
                self._chip(top, "Current Project").pack(side="left", padx=8)
            ctk.CTkLabel(inner, text=project.get('role') or 'Role not set', font=("Arial", 12, "bold"), text_color="#6A9BDD").pack(anchor="w", pady=(8, 2))
            if project.get('description'):
                ctk.CTkLabel(inner, text=project['description'], font=("Arial", 11), text_color="#60748D", wraplength=760, justify="left").pack(anchor="w", pady=(2, 8))
            meta = []
            if project.get('technologies'):
                meta.append(f"Tech: {project['technologies']}")
            if project.get('team_size'):
                meta.append(f"Team Size: {project['team_size']}")
            if project.get('start_date'):
                meta.append(f"Started: {project['start_date']}")
            if project.get('end_date'):
                meta.append(f"Ended: {project['end_date']}")
            if meta:
                ctk.CTkLabel(inner, text=" • ".join(map(str, meta)), font=("Arial", 11), text_color="#6F8098", wraplength=760, justify="left").pack(anchor="w")
            if project.get('achievements'):
                ctk.CTkLabel(inner, text=f"Achievements: {project['achievements']}", font=("Arial", 11), text_color="#60748D", wraplength=760, justify="left").pack(anchor="w", pady=(6, 0))

    def _build_certs_tab(self, parent):
        body = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=8, pady=8)
        if not self.certs:
            self._empty_state(body, "No certifications added yet", "Certificates and verified learning records will appear here once this member saves them to the database.")
            return
        for cert in self.certs:
            card = ctk.CTkFrame(body, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#D7E6F7")
            card.pack(fill="x", pady=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=14)
            ctk.CTkLabel(inner, text=cert['cert_name'], font=("Arial", 15, "bold"), text_color="#163B68").pack(anchor="w")
            issuer = cert.get('issuing_organization') or 'Organization not set'
            issue_date = cert.get('issue_date') or 'Date not set'
            ctk.CTkLabel(inner, text=f"{issuer} • {issue_date}", font=("Arial", 12, "bold"), text_color="#6A9BDD").pack(anchor="w", pady=(6, 2))
            extra = []
            if cert.get('expiry_date'):
                extra.append(f"Expiry: {cert['expiry_date']}")
            if cert.get('credential_id'):
                extra.append(f"Credential ID: {cert['credential_id']}")
            if cert.get('credential_url'):
                extra.append(f"Credential URL: {cert['credential_url']}")
            if extra:
                ctk.CTkLabel(inner, text=" • ".join(map(str, extra)), font=("Arial", 11), text_color="#6F8098", wraplength=760, justify="left").pack(anchor="w", pady=(2, 4))
            if cert.get('skills_gained'):
                ctk.CTkLabel(inner, text=f"Skills Gained: {cert['skills_gained']}", font=("Arial", 11), text_color="#60748D", wraplength=760, justify="left").pack(anchor="w")

    def _build_intro_caption(self):
        if self.user['user_id'] == self.current_user['user_id']:
            return "This is your own profile preview. It combines your saved academic details with the live profile data stored in the system."
        status_text, _ = self._relationship_caption()
        return f"You are viewing a live profile card for this member. Current relationship status: {status_text.lower()}."

    def _relationship_caption(self):
        if not self.relationship:
            return (
                "No Request Yet",
                "There is no mentorship request history between you and this member yet. You can send a request when you are ready."
            )
        status = (self.relationship.get('status') or '').title()
        if self.relationship.get('status') == 'pending':
            if self.relationship.get('mentee_id') == self.current_user['user_id']:
                caption = "You have already sent a mentorship request. It is waiting for the mentor to review and respond."
            else:
                caption = "This member has already sent you a mentorship request. Review it from the requests section or connection details."
        elif self.relationship.get('status') == 'accepted':
            caption = "Your mentorship connection is active. You can continue the conversation through the chat feature and coordinate real mentorship activity."
        elif self.relationship.get('status') == 'completed':
            caption = "This mentorship relationship has been completed. You can still review the request history and chat record."
        elif self.relationship.get('status') == 'rejected':
            caption = "A previous request was rejected. You can review the old request details and decide whether another connection makes sense later."
        else:
            caption = "Relationship information is available, but the current status is not one of the common active states."
        return f"{status} Request", caption

    def show_relationship_summary(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Connection Details")
        dialog.geometry("520x420")
        dialog.configure(fg_color="#F6FAFF")
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(250, lambda: dialog.attributes("-topmost", False))
        dialog.focus_force()

        x = (dialog.winfo_screenwidth() // 2) - 260
        y = (dialog.winfo_screenheight() // 2) - 210
        dialog.geometry(f"520x420+{x}+{y}")

        main = ctk.CTkFrame(dialog, fg_color="#FFFFFF", corner_radius=20, border_width=1, border_color="#D7E6F7")
        main.pack(fill="both", expand=True, padx=18, pady=18)
        inner = ctk.CTkScrollableFrame(main, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(inner, text="Connection Details", font=("Arial", 22, "bold"), text_color="#163B68").pack(anchor="w")
        status_text, caption = self._relationship_caption()
        self._chip(inner, status_text).pack(anchor="w", pady=(10, 10))
        ctk.CTkLabel(inner, text=caption, font=("Arial", 11), text_color="#60748D", wraplength=430, justify="left").pack(anchor="w")

        if self.relationship:
            self._meta_row(inner, "Request ID", str(self.relationship.get('request_id') or '-'))
            self._meta_row(inner, "Mentor", self.relationship.get('mentor_name') or self.user.get('full_name'))
            self._meta_row(inner, "Mentee", self.relationship.get('mentee_name') or self.current_user.get('full_name'))
            self._meta_row(inner, "Subject", self.relationship.get('subject') or 'Not provided')
            self._meta_row(inner, "Created", str(self.relationship.get('created_at') or 'Not available'))
            self._meta_row(inner, "Accepted", str(self.relationship.get('accepted_at') or 'Not accepted yet'))
            ctk.CTkLabel(inner, text="Message", font=("Arial", 12, "bold"), text_color="#163B68").pack(anchor="w", pady=(12, 6))
            msg = ctk.CTkTextbox(inner, height=120, fg_color="#F8FBFF", border_color="#D7E6F7")
            msg.pack(fill="x")
            msg.insert("1.0", self.relationship.get('message') or 'No request message available.')
            msg.configure(state="disabled")
        else:
            ctk.CTkLabel(inner, text="There is no existing request data to display yet.", font=("Arial", 11), text_color="#60748D").pack(anchor="w", pady=(12, 0))

        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(fill="x", pady=(18, 0))
        if self.relationship and self.relationship.get('status') in ('accepted', 'completed'):
            self._header_button(btns, "Open Chat", self.open_chat, fg="#78AFFF", text_color="#FFFFFF").pack(side="left", fill="x", expand=True, padx=(0, 6))
        elif self.user['user_id'] != self.current_user['user_id']:
            self._header_button(btns, "Send Request", self.send_request, fg="#78AFFF", text_color="#FFFFFF").pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._header_button(btns, "Close", dialog.destroy, fg="#FFEDEF", text_color="#9D3A4A").pack(side="left", fill="x", expand=True, padx=(6, 0))

    def get_role_display(self):
        if self.user['role'] == 'teacher':
            return f"Teacher • {self.user.get('department', 'Department') or 'Department'}"
        if self.user['role'] == 'senior_student':
            return f"Senior Student • Year {self.user.get('year') or '-'}"
        if self.user['role'] == 'junior_student':
            return f"Junior Student • Year {self.user.get('year') or '-'}"
        return "Administrator"

    def open_chat(self):
        if not self.relationship or self.relationship.get('status') not in ('accepted', 'completed'):
            show_info("Chat becomes available after a mentorship request is accepted.")
            return
        from gui.mentorship.dialogs import open_chat_dialog
        open_chat_dialog(self.window, self.current_user, self.relationship, self.db, on_update=self.refresh)

    def send_request(self):
        if self.user['user_id'] == self.current_user['user_id']:
            show_error("You cannot send a request to yourself.")
            return
        if self.relationship and self.relationship.get('status') in ('pending', 'accepted'):
            show_info("There is already an active mentorship request between you and this member.")
            return

        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Send Mentorship Request")
        dialog.geometry("460x360")
        dialog.configure(fg_color="#F6FAFF")
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(250, lambda: dialog.attributes("-topmost", False))
        dialog.focus_force()

        shell = ctk.CTkFrame(dialog, fg_color="#FFFFFF", corner_radius=20, border_width=1, border_color="#D7E6F7")
        shell.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(shell, text=f"Request {self.user['full_name']}", font=("Arial", 20, "bold"), text_color="#163B68").pack(anchor="w", padx=22, pady=(22, 6))
        ctk.CTkLabel(shell, text="Write a short but clear request so the mentor understands your goal, learning need, or collaboration interest.", font=("Arial", 11), text_color="#6F8098", wraplength=380, justify="left").pack(anchor="w", padx=22, pady=(0, 14))

        ctk.CTkLabel(shell, text="Subject", anchor="w", font=("Arial", 11, "bold"), text_color="#163B68").pack(fill="x", padx=22, pady=(0, 6))
        subject_entry = ctk.CTkEntry(shell, height=40, fg_color="#F9FBFF", border_color="#D7E6F7")
        subject_entry.pack(fill="x", padx=22)
        subject_entry.insert(0, f"Mentorship Request for {self.user.get('major') or 'Guidance'}")

        ctk.CTkLabel(shell, text="Message", anchor="w", font=("Arial", 11, "bold"), text_color="#163B68").pack(fill="x", padx=22, pady=(12, 6))
        message_text = ctk.CTkTextbox(shell, height=120, fg_color="#F9FBFF", border_color="#D7E6F7")
        message_text.pack(fill="both", expand=True, padx=22)
        message_text.insert("1.0", f"Hello {self.user['full_name']},\n\nI would like to connect with you for mentorship and guidance. I am especially interested in learning from your experience in {self.user.get('major') or self.user.get('department') or 'your academic field'}.\n")

        def submit_request():
            try:
                subject = require_text(subject_entry.get(), "Subject")
                message = require_text(message_text.get("1.0", "end-1c"), "Message")
            except ValueError as error:
                show_error(str(error))
                return

            request_id = self.db.create_mentorship_request(
                self.user['user_id'],
                self.current_user['user_id'],
                subject,
                message,
            )
            if not request_id or request_id == -1:
                show_error("Failed to send mentorship request.")
                return

            show_success("Mentorship request sent successfully.")
            dialog.destroy()
            self.refresh()

        btns = ctk.CTkFrame(shell, fg_color="transparent")
        btns.pack(fill="x", padx=22, pady=18)
        self._header_button(btns, "Send", submit_request, fg="#78AFFF", text_color="#FFFFFF").pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._header_button(btns, "Cancel", dialog.destroy, fg="#EEF4FF", text_color="#1F3B5B").pack(side="left", fill="x", expand=True, padx=(6, 0))
