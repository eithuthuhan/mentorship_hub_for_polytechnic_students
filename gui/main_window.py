import customtkinter as ctk
from tkinter import messagebox

from colors import Colors
from i18n import tr, normalize_language


class MainWindow:
    def __init__(self, root, user, db, on_logout=None):
        self.root = root
        self.user = user
        self.db = db
        self.on_logout = on_logout

        self.root.title(f"Mentorship Hub - {user['full_name']}")
        self.root.geometry("1360x780")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.current_page = None
        self.language = normalize_language(self.user.get("preferred_language"))
        self.setup_sidebar()
        self.load_dashboard()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, width=290, fg_color=Colors.PRIMARY, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        profile_frame = ctk.CTkFrame(self.sidebar, fg_color=Colors.BG_HOVER, height=220, corner_radius=0)
        profile_frame.pack(fill="x")
        profile_frame.pack_propagate(False)

        ctk.CTkLabel(profile_frame, text="👤", font=("Arial", 44), text_color=Colors.TEXT_LIGHT).pack(pady=(28, 8))
        ctk.CTkLabel(profile_frame, text=self.user["full_name"], font=("Arial", 16, "bold"), text_color=Colors.TEXT_LIGHT).pack()
        ctk.CTkLabel(profile_frame, text=self.user.get("role", "member").replace("_", " ").title(), font=("Arial", 11), text_color=Colors.ACCENT).pack(pady=(6, 0))
        ctk.CTkLabel(profile_frame, text=tr(self.language, "dashboard_welcome"), font=("Arial", 11), text_color=Colors.TEXT_LIGHT).pack(pady=(18, 0))

        menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, pady=24)

        menus = [
            (tr(self.language, "dashboard"), self.load_dashboard),
            (tr(self.language, "mentorship"), self.open_mentorship),
            (tr(self.language, "events"), self.open_events),
            (tr(self.language, "announcements"), self.open_announcements),
            (tr(self.language, "my_profile"), self.open_profile),
            (tr(self.language, "settings"), self.open_settings),
        ]

        for text, command in menus:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                command=command,
                fg_color="transparent",
                text_color=Colors.TEXT_LIGHT,
                hover_color=Colors.BG_HOVER,
                corner_radius=12,
                anchor="w",
                font=("Arial", 13, "bold"),
                height=44,
            )
            btn.pack(fill="x", padx=14, pady=4)

        logout_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logout_frame.pack(side="bottom", fill="x", pady=20)

        ctk.CTkButton(
            logout_frame,
            text=tr(self.language, "logout"),
            fg_color=Colors.DANGER,
            hover_color="#E17F7F",
            text_color=Colors.TEXT_DARK,
            font=("Arial", 13, "bold"),
            corner_radius=14,
            border_width=0,
            command=self.logout,
        ).pack(fill="x", padx=20, pady=10, ipady=2)

        self.content = ctk.CTkFrame(self.root, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True, padx=14, pady=14)

    def refresh_language(self):
        self.language = normalize_language(self.user.get("preferred_language"))
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_sidebar()
        self.load_dashboard()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page_error(self, page_name, error):
        error_box = ctk.CTkFrame(self.content, fg_color=Colors.BG_WHITE, corner_radius=18, border_width=1, border_color=Colors.DANGER)
        error_box.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(error_box, text=f"{page_name} Error", font=("Arial", 22, "bold"), text_color=Colors.DANGER).pack(pady=(30, 10))
        ctk.CTkLabel(error_box, text=str(error), font=("Arial", 14), text_color=Colors.TEXT_DARK, wraplength=900).pack(padx=20, pady=(0, 15))

    def load_dashboard(self):
        self.clear_content()
        try:
            if self.user["role"] == "junior_student":
                from gui.dashboard.junior_dashboard import JuniorDashboard
                self.current_page = JuniorDashboard(self.content, self.user, self.db)
            elif self.user["role"] == "senior_student":
                from gui.dashboard.senior_dashboard import SeniorDashboard
                self.current_page = SeniorDashboard(self.content, self.user, self.db)
            elif self.user["role"] == "teacher":
                from gui.dashboard.teacher_dashboard import TeacherDashboard
                self.current_page = TeacherDashboard(self.content, self.user, self.db)
            else:
                from gui.dashboard.admin_dashboard import AdminDashboard
                self.current_page = AdminDashboard(self.content, self.user, self.db)
        except Exception as error:
            self.show_page_error("Dashboard", error)

    def open_mentorship(self):
        self.clear_content()
        try:
            from gui.mentorship.mentorship_page import MentorshipPage

            MentorshipPage(self.content, self.user, self.db)
        except Exception as error:
            self.show_page_error("Mentorship Page", error)

    def open_events(self):
        self.clear_content()
        try:
            from gui.events.events_page import EventsPage

            EventsPage(self.content, self.user, self.db)
        except Exception as error:
            self.show_page_error("Events Page", error)

    def open_announcements(self):
        self.clear_content()
        try:
            from gui.announcements.announcements_page import AnnouncementsPage

            AnnouncementsPage(self.content, self.user, self.db)
        except Exception as error:
            self.show_page_error("Announcements Page", error)

    def open_profile(self):
        self.clear_content()
        try:
            from gui.profile.profile_page import ProfilePage

            ProfilePage(self.content, self.user, self.db)
        except Exception as error:
            self.show_page_error("Profile Page", error)

    def open_settings(self):
        try:
            from gui.profile.settings_page import SettingsPage

            SettingsPage(self, self.user, self.db)
        except Exception as error:
            self.clear_content()
            self.show_page_error("Settings Page", error)

    def logout(self):
        if not messagebox.askyesno(tr(self.language, "logout_title"), tr(self.language, "logout_confirm")):
            return

        if callable(self.on_logout):
            self.on_logout()
            return

        self.root.destroy()
