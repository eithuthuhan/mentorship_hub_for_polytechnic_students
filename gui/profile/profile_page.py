
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


class _BaseDialog:
    def __init__(self, parent, title, width=520, height=520):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}")
        self.window.transient(parent.winfo_toplevel())
        self.window.grab_set()
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after(250, lambda: self.window.attributes("-topmost", False))
        self.window.focus_force()
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.main = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=18, pady=18)

    def add_label(self, text):
        ctk.CTkLabel(self.main, text=text, font=("Arial", 12, "bold"), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(8, 4))

    def add_entry(self, label, value=""):
        self.add_label(label)
        entry = ctk.CTkEntry(self.main, height=40, fg_color="#F9FBFF", border_color="#D7E6F7")
        entry.insert(0, value or "")
        entry.pack(fill="x")
        return entry

    def add_text(self, label, value="", height=90):
        self.add_label(label)
        text = ctk.CTkTextbox(self.main, height=height, fg_color="#F9FBFF", border_color="#D7E6F7")
        text.insert("1.0", value or "")
        text.pack(fill="x")
        return text

    def add_buttons(self, save_cmd):
        btns = ctk.CTkFrame(self.main, fg_color="transparent")
        btns.pack(fill="x", pady=(18, 0))
        ctk.CTkButton(btns, text="Save", height=42, corner_radius=14, fg_color="#78AFFF", hover_color="#5A95EC", command=save_cmd).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btns, text="Cancel", height=42, corner_radius=14, fg_color="#EEF4FF", text_color="#1F3B5B", hover_color="#E1ECFF", command=self.window.destroy).pack(side="left", expand=True, fill="x", padx=(6, 0))


class SkillDialog(_BaseDialog):
    def __init__(self, parent, db, user_id, refresh_callback, skill=None):
        super().__init__(parent, "Edit Skill" if skill else "Add Skill", 440, 360)
        self.db = db
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.skill = skill

        self.name_entry = self.add_entry("Skill Name", skill.get('skill_name') if skill else "")
        self.category_var = ctk.StringVar(value=(skill.get('category') if skill else 'other') or 'other')
        self.add_label("Category")
        ctk.CTkComboBox(self.main, values=["programming", "design", "soft_skill", "language", "other"], variable=self.category_var, height=40, fg_color="#F9FBFF", border_color="#D7E6F7", button_color="#78AFFF").pack(fill="x")
        self.level_var = ctk.StringVar(value=(skill.get('proficiency_level') if skill else 'beginner') or 'beginner')
        self.add_label("Level")
        ctk.CTkComboBox(self.main, values=["beginner", "intermediate", "advanced", "expert"], variable=self.level_var, height=40, fg_color="#F9FBFF", border_color="#D7E6F7", button_color="#78AFFF").pack(fill="x")
        self.years_entry = self.add_entry("Years Experience", str(skill.get('years_experience', 0)) if skill else "0")
        self.add_buttons(self.save)

    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Skill name is required.")
            return
        years = int(self.years_entry.get().strip() or 0) if (self.years_entry.get().strip() or '0').isdigit() else 0
        if self.skill:
            ok = self.db.update_user_skill(self.user_id, self.skill['skill_id'], name, self.level_var.get(), years, self.category_var.get())
        else:
            ok = self.db.add_or_update_user_skill(self.user_id, name, self.level_var.get(), years, self.category_var.get())
        if ok:
            self.refresh_callback()
            self.window.destroy()
            messagebox.showinfo("Success", "Skill saved successfully.")
        else:
            messagebox.showerror("Error", "Failed to save skill.")


class ProjectDialog(_BaseDialog):
    def __init__(self, parent, db, user_id, refresh_callback, project=None):
        super().__init__(parent, "Edit Project" if project else "Add Project", 560, 690)
        self.db = db
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.project = project
        self.name_entry = self.add_entry("Project Name", project.get('project_name') if project else "")
        self.role_entry = self.add_entry("Your Role", project.get('role') if project else "")
        self.tech_entry = self.add_entry("Technologies", project.get('technologies') if project else "")
        self.project_url_entry = self.add_entry("Project URL", project.get('project_url') if project else "")
        self.github_entry = self.add_entry("GitHub URL", project.get('github_url') if project else "")
        self.start_entry = self.add_entry("Start Date (YYYY-MM-DD)", str(project.get('start_date') or "") if project else "")
        self.end_entry = self.add_entry("End Date (YYYY-MM-DD)", str(project.get('end_date') or "") if project else "")
        self.team_entry = self.add_entry("Team Size", str(project.get('team_size', 1)) if project else "1")
        self.desc_text = self.add_text("Description", project.get('description') if project else "", 110)
        self.ach_text = self.add_text("Achievements", project.get('achievements') if project else "", 90)
        self.current_var = ctk.BooleanVar(value=bool(project.get('is_current')) if project else False)
        ctk.CTkCheckBox(self.main, text="Current Project", variable=self.current_var).pack(anchor="w", pady=(12, 0))
        self.add_buttons(self.save)

    def _date_or_none(self, value):
        value = value.strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")

    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Project name is required.")
            return
        try:
            team_size_raw = self.team_entry.get().strip() or "1"
            if not team_size_raw.isdigit() or int(team_size_raw) < 1:
                raise ValueError("Team size must be a positive number.")
            data = {
                'project_name': name,
                'role': self.role_entry.get().strip(),
                'technologies': self.tech_entry.get().strip(),
                'project_url': self.project_url_entry.get().strip(),
                'github_url': self.github_entry.get().strip(),
                'start_date': self._date_or_none(self.start_entry.get()),
                'end_date': self._date_or_none(self.end_entry.get()),
                'team_size': int(team_size_raw),
                'description': self.desc_text.get("1.0", "end-1c").strip(),
                'achievements': self.ach_text.get("1.0", "end-1c").strip(),
                'is_current': self.current_var.get(),
            }
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        ok = self.db.update_project(self.project['project_id'], data) if self.project else self.db.create_project(self.user_id, data)
        if ok:
            self.refresh_callback()
            self.window.destroy()
            messagebox.showinfo("Success", "Project saved successfully.")
        else:
            messagebox.showerror("Error", "Failed to save project.")


class CertificateDialog(_BaseDialog):
    def __init__(self, parent, db, user_id, refresh_callback, cert=None):
        super().__init__(parent, "Edit Certificate" if cert else "Add Certificate", 540, 620)
        self.db = db
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.cert = cert
        self.name_entry = self.add_entry("Certificate Name", cert.get('cert_name') if cert else "")
        self.org_entry = self.add_entry("Issuing Organization", cert.get('issuing_organization') if cert else "")
        self.issue_entry = self.add_entry("Issue Date (YYYY-MM-DD)", str(cert.get('issue_date') or "") if cert else "")
        self.expiry_entry = self.add_entry("Expiry Date (YYYY-MM-DD)", str(cert.get('expiry_date') or "") if cert else "")
        self.credential_id_entry = self.add_entry("Credential ID", cert.get('credential_id') if cert else "")
        self.url_entry = self.add_entry("Credential URL", cert.get('credential_url') if cert else "")
        self.file_entry = self.add_entry("Certificate File Path", cert.get('cert_file') if cert else "")
        self.skills_text = self.add_text("Skills Gained", cert.get('skills_gained') if cert else "", 100)
        self.add_buttons(self.save)

    def _date_or_none(self, value, required=False):
        value = value.strip()
        if not value:
            if required:
                raise ValueError("Issue date is required.")
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")

    def save(self):
        name = self.name_entry.get().strip()
        org = self.org_entry.get().strip()
        if not name or not org:
            messagebox.showerror("Error", "Certificate name and organization are required.")
            return
        try:
            data = {
                'cert_name': name,
                'issuing_organization': org,
                'issue_date': self._date_or_none(self.issue_entry.get(), True),
                'expiry_date': self._date_or_none(self.expiry_entry.get()),
                'credential_id': self.credential_id_entry.get().strip() or None,
                'credential_url': self.url_entry.get().strip() or None,
                'cert_file': self.file_entry.get().strip() or None,
                'skills_gained': self.skills_text.get("1.0", "end-1c").strip(),
            }
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        ok = self.db.update_certification(self.cert['cert_id'], data) if self.cert else self.db.create_certification(self.user_id, data)
        if ok:
            self.refresh_callback()
            self.window.destroy()
            messagebox.showinfo("Success", "Certificate saved successfully.")
        else:
            messagebox.showerror("Error", "Failed to save certificate.")


class ProfilePage:
    """Main Profile Page - polished real-data profile view."""

    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        self.setup_ui()
        self.load_profile_data()

    def refresh_user_data(self):
        refreshed = self.db.get_user_by_id(self.user['user_id'])
        if refreshed:
            self.user.clear()
            self.user.update(refreshed)
        for widget in self.parent.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.load_profile_data()

    def setup_ui(self):
        self.page = ctk.CTkFrame(self.parent, fg_color="#F6FAFF")
        self.page.pack(fill="both", expand=True)

        outer = ctk.CTkScrollableFrame(self.page, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        self._create_header(outer)

        content = ctk.CTkFrame(outer, fg_color="transparent")
        content.pack(fill="both", expand=True, pady=(12, 0))
        content.grid_columnconfigure(0, weight=0)
        content.grid_columnconfigure(1, weight=1)

        self.left_panel = ctk.CTkFrame(content, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.right_panel = ctk.CTkFrame(content, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        self._create_identity_card(self.left_panel)
        self._create_contact_card(self.left_panel)
        self._create_academic_card(self.left_panel)
        self._create_overview_card(self.left_panel)

        self._create_highlight_banner(self.right_panel)
        self._create_tabbed_content(self.right_panel)

    def _card(self, parent, corner_radius=18, padding=0):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=corner_radius, border_width=1, border_color="#D7E6F7")
        if padding is not None:
            card.pack(fill="x", pady=(0, 14), padx=padding)
        return card

    def _create_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=22, border_width=1, border_color="#D7E6F7")
        header.pack(fill="x")
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=22, pady=20)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(left, text="My Profile", font=("Arial", 28, "bold"), text_color="#163B68").pack(anchor="w")
        ctk.CTkLabel(
            left,
            text="Keep your profile complete so mentors, mentees, and event participants can understand your strengths, interests, and achievements.",
            font=("Arial", 12),
            text_color="#6F8098",
            wraplength=720,
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(side="right", anchor="n")
        self._header_button(actions, "✏️ Edit Profile", self.open_edit_profile, "#78AFFF", "#FFFFFF").pack(side="left", padx=4)
        self._header_button(actions, "+ Skill", self.add_skill, "#EEF4FF", "#1F3B5B").pack(side="left", padx=4)
        self._header_button(actions, "+ Project", self.add_project, "#EEF4FF", "#1F3B5B").pack(side="left", padx=4)
        self._header_button(actions, "+ Certificate", self.add_certificate, "#EEF4FF", "#1F3B5B").pack(side="left", padx=4)
        self._header_button(actions, "⟳ Refresh", self.refresh_user_data, "#EAF7F1", "#2E6B4E").pack(side="left", padx=4)

    def _header_button(self, parent, text, command, fg, text_color):
        return ctk.CTkButton(parent, text=text, height=40, corner_radius=14, fg_color=fg, hover_color="#DDEBFF" if fg != "#78AFFF" else "#5F97EC", text_color=text_color, command=command)

    def _create_identity_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=22)

        avatar = ctk.CTkLabel(body, text="👤", font=("Arial", 52), width=86, height=86, corner_radius=43, fg_color="#78AFFF", text_color="#FFFFFF")
        avatar.pack(anchor="center", pady=(0, 12))
        ctk.CTkLabel(body, text=self.user.get('full_name', 'Member'), font=("Arial", 22, "bold"), text_color="#163B68").pack(anchor="center")
        ctk.CTkLabel(body, text=self.get_role_display(), font=("Arial", 13), text_color="#6A9BDD").pack(anchor="center", pady=(4, 10))

        chips = ctk.CTkFrame(body, fg_color="transparent")
        chips.pack(fill="x", pady=(2, 10))
        self._chip(chips, self.user.get('department') or 'Department not set').pack(side="left", padx=(0, 6))
        if self.user.get('major'):
            self._chip(chips, self.user['major']).pack(side="left", padx=6)
        if self.user.get('year'):
            self._chip(chips, f"Year {self.user['year']}").pack(side="left", padx=6)

        welcome = self._build_welcome_message()
        ctk.CTkLabel(body, text=welcome, font=("Arial", 12), text_color="#60748D", wraplength=280, justify="center").pack(fill="x", pady=(8, 0))

    def _create_contact_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(body, text="Contact & Presence", font=("Arial", 16, "bold"), text_color="#163B68").pack(anchor="w", pady=(0, 10))
        self._info_row(body, "Email", self.user.get('email') or "Not provided")
        self._info_row(body, "Phone", self.user.get('phone') or "Not provided")
        location = ", ".join([x for x in [self.user.get('city'), self.user.get('country') or 'Myanmar'] if x])
        self._info_row(body, "Location", location or "Not set")

    def _create_academic_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(body, text="Academic Snapshot", font=("Arial", 16, "bold"), text_color="#163B68").pack(anchor="w", pady=(0, 10))
        self._info_row(body, "Department", self.user.get('department') or "Not set")
        self._info_row(body, "Major", self.user.get('major') or "Not set")
        self._info_row(body, "Year", str(self.user.get('year') or "Not set"))
        self._info_row(body, "Status", "Active member" if self.user.get('is_active', True) else "Inactive")

    def _create_overview_card(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(body, text="Profile Strength", font=("Arial", 16, "bold"), text_color="#163B68").pack(anchor="w")
        completion = self._calculate_completion()
        ctk.CTkProgressBar(body, progress_color="#78AFFF", fg_color="#E8F0FF").pack(fill="x", pady=(10, 8))
        body.winfo_children()[-1].set(completion / 100)
        ctk.CTkLabel(body, text=f"{completion}% complete", font=("Arial", 12, "bold"), text_color="#163B68").pack(anchor="w")
        note = "Complete your profile to build trust and get better mentorship connections." if completion < 80 else "Your profile already looks strong and ready for networking."
        ctk.CTkLabel(body, text=note, font=("Arial", 11), text_color="#6F8098", wraplength=280, justify="left").pack(anchor="w", pady=(6, 0))

    def _create_highlight_banner(self, parent):
        card = self._card(parent)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=22, pady=22)
        ctk.CTkLabel(body, text="Professional Highlights", font=("Arial", 19, "bold"), text_color="#163B68").pack(anchor="w")
        ctk.CTkLabel(
            body,
            text="This space summarizes the real information in your account, including mentorship engagement, event participation, and profile content that other members can explore.",
            font=("Arial", 12),
            text_color="#6F8098",
            wraplength=780,
            justify="left"
        ).pack(anchor="w", pady=(8, 16))

        stats = self.db.get_user_stats(self.user['user_id']) or {}
        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x")
        values = [
            ("Mentorships", (stats.get('mentor_count', 0) + stats.get('mentee_count', 0)), "Connections built across mentoring and learning."),
            ("Events", stats.get('event_count', 0), "Workshops, seminars, and sessions you joined."),
            ("Messages", stats.get('message_count', 0), "Direct conversations with members and mentors."),
            ("Rating", f"{stats.get('avg_rating', 0):.1f}", "Average mentorship rating received so far."),
        ]
        for i, (label, value, desc) in enumerate(values):
            card_item = ctk.CTkFrame(grid, fg_color="#F7FAFF", corner_radius=16, border_width=1, border_color="#E1ECFF")
            card_item.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0), pady=0)
            grid.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card_item, text=str(value), font=("Arial", 24, "bold"), text_color="#163B68").pack(anchor="w", padx=16, pady=(14, 2))
            ctk.CTkLabel(card_item, text=label, font=("Arial", 12, "bold"), text_color="#6A9BDD").pack(anchor="w", padx=16)
            ctk.CTkLabel(card_item, text=desc, font=("Arial", 11), text_color="#6F8098", wraplength=160, justify="left").pack(anchor="w", padx=16, pady=(4, 14))

    def _create_tabbed_content(self, parent):
        wrapper = self._card(parent, padding=None)
        wrapper.pack(fill="both", expand=True, pady=(0, 14))
        notebook = ctk.CTkTabview(wrapper, fg_color="#FFFFFF", segmented_button_fg_color="#EEF4FF", segmented_button_selected_color="#78AFFF", segmented_button_selected_hover_color="#5F97EC", segmented_button_unselected_color="#EEF4FF", segmented_button_unselected_hover_color="#E1ECFF", text_color="#1F3B5B")
        notebook.pack(fill="both", expand=True, padx=16, pady=16)
        notebook.add("🛠️ Skills")
        notebook.add("📁 Projects")
        notebook.add("📜 Certificates")
        self.skills_tab = notebook.tab("🛠️ Skills")
        self.projects_tab = notebook.tab("📁 Projects")
        self.certs_tab = notebook.tab("📜 Certificates")
        self.setup_skills_tab()
        self.setup_projects_tab()
        self.setup_certs_tab()

    def _build_welcome_message(self):
        stats = self.db.get_user_stats(self.user['user_id']) or {}
        total_activity = sum(int(stats.get(key, 0) or 0) for key in ['mentor_count', 'mentee_count', 'event_count', 'message_count'])
        if total_activity == 0:
            return "Welcome to your profile space. Start by adding your skills, projects, and certificates so other members can quickly understand your strengths."
        return "Welcome back. Your profile is already connected with live mentorship, event, and message activity from the database."

    def _calculate_completion(self):
        checks = [
            bool(self.user.get('full_name')),
            bool(self.user.get('email')),
            bool(self.user.get('bio')),
            bool(self.user.get('department')),
            bool(self.user.get('major')),
            bool(self.user.get('year')),
            bool(self.user.get('city')),
            bool(self.user.get('phone')),
        ]
        complete = sum(1 for item in checks if item)
        return int((complete / len(checks)) * 100)

    def _chip(self, parent, text):
        return ctk.CTkLabel(parent, text=text, font=("Arial", 11, "bold"), text_color="#356299", fg_color="#EEF4FF", corner_radius=999, padx=12, pady=6)

    def _info_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=label, font=("Arial", 11, "bold"), text_color="#6F8098").pack(side="left")
        ctk.CTkLabel(row, text=value, font=("Arial", 11), text_color="#163B68", wraplength=180, justify="right").pack(side="right")

    def setup_skills_tab(self):
        header = ctk.CTkFrame(self.skills_tab, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(header, text="Skills & Expertise", font=("Arial", 17, "bold"), text_color="#163B68").pack(side="left")
        ctk.CTkLabel(header, text="Keep this section updated so other members understand what you can offer or what you are growing into.", font=("Arial", 11), text_color="#6F8098").pack(side="left", padx=14)
        ctk.CTkButton(header, text="+ Add Skill", width=110, height=34, corner_radius=12, fg_color="#78AFFF", command=self.add_skill).pack(side="right")
        self.skills_container = ctk.CTkScrollableFrame(self.skills_tab, fg_color="transparent", height=360)
        self.skills_container.pack(fill="both", expand=True)

    def setup_projects_tab(self):
        header = ctk.CTkFrame(self.projects_tab, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(header, text="Projects & Work", font=("Arial", 17, "bold"), text_color="#163B68").pack(side="left")
        ctk.CTkLabel(header, text="Show the real work you have built, joined, or currently maintain.", font=("Arial", 11), text_color="#6F8098").pack(side="left", padx=14)
        ctk.CTkButton(header, text="+ Add Project", width=120, height=34, corner_radius=12, fg_color="#78AFFF", command=self.add_project).pack(side="right")
        self.projects_container = ctk.CTkScrollableFrame(self.projects_tab, fg_color="transparent", height=360)
        self.projects_container.pack(fill="both", expand=True)

    def setup_certs_tab(self):
        header = ctk.CTkFrame(self.certs_tab, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(header, text="Certificates & Recognition", font=("Arial", 17, "bold"), text_color="#163B68").pack(side="left")
        ctk.CTkLabel(header, text="Store official certifications, training records, and recognition that strengthen your profile.", font=("Arial", 11), text_color="#6F8098").pack(side="left", padx=14)
        ctk.CTkButton(header, text="+ Add Certificate", width=140, height=34, corner_radius=12, fg_color="#78AFFF", command=self.add_certificate).pack(side="right")
        self.certs_container = ctk.CTkScrollableFrame(self.certs_tab, fg_color="transparent", height=360)
        self.certs_container.pack(fill="both", expand=True)

    def load_profile_data(self):
        skills = self.db.get_user_skills(self.user['user_id']) or []
        projects = self.db.get_user_projects(self.user['user_id']) or []
        certs = self.db.get_user_certifications(self.user['user_id']) or []
        self.display_skills(skills)
        self.display_projects(projects)
        self.display_certificates(certs)

    def display_skills(self, skills):
        for widget in self.skills_container.winfo_children():
            widget.destroy()
        if not skills:
            self._empty_state(self.skills_container, "No skills added yet", "Add your first skill so mentors and collaborators can quickly see your strengths.")
            return
        for skill in skills:
            self.create_skill_item(skill)

    def create_skill_item(self, skill):
        item = ctk.CTkFrame(self.skills_container, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#D7E6F7")
        item.pack(fill="x", pady=5)
        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=skill['skill_name'], font=("Arial", 14, "bold"), text_color="#163B68").pack(side="left")
        self._chip(top, (skill.get('proficiency_level') or 'beginner').title()).pack(side="left", padx=10)
        if skill.get('category'):
            self._chip(top, str(skill['category']).replace('_', ' ').title()).pack(side="left")

        meta = f"Experience: {skill.get('years_experience', 0) or 0} years"
        ctk.CTkLabel(inner, text=meta, font=("Arial", 11), text_color="#6F8098").pack(anchor="w", pady=(8, 0))

        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(anchor="e", pady=(10, 0))
        ctk.CTkButton(btns, text="Edit", width=72, height=30, corner_radius=12, fg_color="#EEF4FF", text_color="#1F3B5B", command=lambda: self.edit_skill(skill)).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Delete", width=78, height=30, corner_radius=12, fg_color="#FFEDEF", text_color="#9D3A4A", hover_color="#FFDDE2", command=lambda: self.delete_skill(skill)).pack(side="left", padx=4)

    def display_projects(self, projects):
        for widget in self.projects_container.winfo_children():
            widget.destroy()
        if not projects:
            self._empty_state(self.projects_container, "No projects added yet", "Use this section to show real academic or personal work, the tools you used, and what you achieved.")
            return
        for project in projects:
            self.create_project_item(project)

    def create_project_item(self, project):
        item = ctk.CTkFrame(self.projects_container, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#D7E6F7")
        item.pack(fill="x", pady=6)
        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=15)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=project['project_name'], font=("Arial", 15, "bold"), text_color="#163B68").pack(side="left")
        if project.get('is_current'):
            self._chip(top, "Current Project").pack(side="left", padx=10)

        role_text = project.get('role') or "Role not set"
        ctk.CTkLabel(inner, text=role_text, font=("Arial", 12, "bold"), text_color="#6A9BDD").pack(anchor="w", pady=(8, 2))
        if project.get('description'):
            ctk.CTkLabel(inner, text=project['description'], font=("Arial", 11), text_color="#60748D", wraplength=760, justify="left").pack(anchor="w", pady=(2, 8))
        details = []
        if project.get('technologies'):
            details.append(f"Tech: {project['technologies']}")
        if project.get('team_size'):
            details.append(f"Team Size: {project['team_size']}")
        if project.get('start_date'):
            details.append(f"Started: {project['start_date']}")
        if project.get('end_date'):
            details.append(f"Ended: {project['end_date']}")
        if details:
            ctk.CTkLabel(inner, text=" • ".join(map(str, details)), font=("Arial", 11), text_color="#6F8098", wraplength=760, justify="left").pack(anchor="w")
        if project.get('achievements'):
            ctk.CTkLabel(inner, text=f"Achievements: {project['achievements']}", font=("Arial", 11), text_color="#60748D", wraplength=760, justify="left").pack(anchor="w", pady=(6, 0))

        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(anchor="e", pady=(12, 0))
        ctk.CTkButton(btn_frame, text="Edit", width=72, height=30, corner_radius=12, fg_color="#EEF4FF", text_color="#1F3B5B", command=lambda: self.edit_project(project)).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Delete", width=78, height=30, corner_radius=12, fg_color="#FFEDEF", text_color="#9D3A4A", hover_color="#FFDDE2", command=lambda: self.delete_project(project)).pack(side="left", padx=4)

    def display_certificates(self, certs):
        for widget in self.certs_container.winfo_children():
            widget.destroy()
        if not certs:
            self._empty_state(self.certs_container, "No certificates added yet", "Keep verified learning records here so your profile shows real proof of growth and commitment.")
            return
        for cert in certs:
            self.create_certificate_item(cert)

    def create_certificate_item(self, cert):
        item = ctk.CTkFrame(self.certs_container, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#D7E6F7")
        item.pack(fill="x", pady=6)
        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=15)
        ctk.CTkLabel(inner, text=cert['cert_name'], font=("Arial", 15, "bold"), text_color="#163B68").pack(anchor="w")
        issuer = cert.get('issuing_organization') or 'Organization not set'
        date = cert.get('issue_date') or 'Date not set'
        ctk.CTkLabel(inner, text=f"{issuer} • {date}", font=("Arial", 12, "bold"), text_color="#6A9BDD").pack(anchor="w", pady=(6, 2))
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
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(anchor="e", pady=(12, 0))
        ctk.CTkButton(btn_frame, text="Edit", width=72, height=30, corner_radius=12, fg_color="#EEF4FF", text_color="#1F3B5B", command=lambda: self.edit_certificate(cert)).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Delete", width=78, height=30, corner_radius=12, fg_color="#FFEDEF", text_color="#9D3A4A", hover_color="#FFDDE2", command=lambda: self.delete_certificate(cert)).pack(side="left", padx=4)

    def _empty_state(self, parent, title, subtitle):
        box = ctk.CTkFrame(parent, fg_color="#F8FBFF", corner_radius=18, border_width=1, border_color="#E1ECFF")
        box.pack(fill="x", pady=12, padx=6)
        ctk.CTkLabel(box, text=title, font=("Arial", 15, "bold"), text_color="#163B68").pack(pady=(22, 6))
        ctk.CTkLabel(box, text=subtitle, font=("Arial", 11), text_color="#6F8098", wraplength=700, justify="center").pack(padx=18, pady=(0, 20))

    def get_role_display(self):
        if self.user['role'] == 'teacher':
            return f"Teacher • {self.user.get('department', 'CS') or 'CS'}"
        if self.user['role'] == 'senior_student':
            return f"Senior Student • Year {self.user.get('year') or '-'}"
        if self.user['role'] == 'junior_student':
            return f"Junior Student • Year {self.user.get('year') or '-'}"
        return "Administrator"

    def add_skill(self):
        SkillDialog(self.parent, self.db, self.user['user_id'], self.load_profile_data)

    def edit_skill(self, skill):
        SkillDialog(self.parent, self.db, self.user['user_id'], self.load_profile_data, skill)

    def delete_skill(self, skill):
        if messagebox.askyesno("Confirm", f"Delete skill '{skill['skill_name']}'?"):
            if self.db.remove_user_skill(self.user['user_id'], skill['skill_id']):
                messagebox.showinfo("Success", "Skill deleted")
                self.load_profile_data()

    def add_project(self):
        ProjectDialog(self.parent, self.db, self.user['user_id'], self.load_profile_data)

    def edit_project(self, project):
        ProjectDialog(self.parent, self.db, self.user['user_id'], self.load_profile_data, project)

    def delete_project(self, project):
        if messagebox.askyesno("Confirm", f"Delete project '{project['project_name']}'?"):
            if self.db.delete_project(project['project_id']):
                messagebox.showinfo("Success", "Project deleted")
                self.load_profile_data()

    def add_certificate(self):
        CertificateDialog(self.parent, self.db, self.user['user_id'], self.load_profile_data)

    def edit_certificate(self, cert):
        CertificateDialog(self.parent, self.db, self.user['user_id'], self.load_profile_data, cert)

    def delete_certificate(self, cert):
        if messagebox.askyesno("Confirm", f"Delete certificate '{cert['cert_name']}'?"):
            if self.db.delete_certification(cert['cert_id']):
                messagebox.showinfo("Success", "Certificate deleted")
                self.load_profile_data()

    def open_edit_profile(self):
        from .edit_profile_page import EditProfilePage
        EditProfilePage(self.parent, self.user, self.db, self.refresh_user_data)
