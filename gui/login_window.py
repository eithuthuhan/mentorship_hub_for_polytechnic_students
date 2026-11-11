import threading

import customtkinter as ctk
from colors import Colors
from gui.ui_helpers import focus_widget, show_error, show_success


class LoginWindow:
    def __init__(self, root, db, on_login_success):
        self.root = root
        self.root.title("Mentorship Hub - Login")
        self.on_login_success = on_login_success
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(fg_color=Colors.BG_LIGHT)

        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.pack(expand=True, fill="both", padx=34, pady=34)

        left = ctk.CTkFrame(main, fg_color=Colors.BG_DARK, corner_radius=28)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        glow = ctk.CTkFrame(left, fg_color=Colors.SECONDARY, corner_radius=220, width=220, height=220)
        glow.place(relx=0.18, rely=0.18, anchor="center")
        glow.lower()

        brand_frame = ctk.CTkFrame(left, fg_color="transparent")
        brand_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(brand_frame, text="🎓", font=("Arial", 82), text_color=Colors.TEXT_LIGHT).pack()
        ctk.CTkLabel(brand_frame, text="Mentorship Hub", font=("Arial", 32, "bold"), text_color=Colors.TEXT_LIGHT).pack(pady=(18, 8))
        ctk.CTkLabel(brand_frame, text="Clean. Modern. Connected campus mentoring.", font=("Arial", 13), text_color=Colors.ACCENT).pack()
        pill = ctk.CTkFrame(brand_frame, fg_color=Colors.BG_SOFT_BLUE, corner_radius=100)
        pill.pack(pady=(18, 18))
        ctk.CTkLabel(pill, text="Built for Polytechnic Students", font=("Arial", 11, "bold"), text_color=Colors.TEXT_DARK).pack(padx=16, pady=8)
        for feature in [
            "✓ Find expert mentors quickly",
            "✓ Join events and workshops",
            "✓ Build skills with real peers",
            "✓ Track mentorship progress",
        ]:
            ctk.CTkLabel(brand_frame, text=feature, font=("Arial", 12), text_color=Colors.TEXT_LIGHT).pack(pady=4)

        right = ctk.CTkFrame(main, fg_color=Colors.BG_WHITE, corner_radius=28, border_width=1, border_color=Colors.BORDER)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0))

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(form, text="Welcome Back", font=("Arial", 30, "bold"), text_color=Colors.TEXT_DARK).pack(pady=(0, 8))
        ctk.CTkLabel(form, text="Login using your username or email", font=("Arial", 12), text_color=Colors.TEXT_MUTED).pack(pady=(0, 28))

        ctk.CTkLabel(form, text="Username / Email", font=("Arial", 12, "bold"), anchor="w", text_color=Colors.TEXT_DARK).pack(fill="x")
        self.username_entry = ctk.CTkEntry(
            form,
            width=320,
            height=46,
            corner_radius=14,
            border_color=Colors.BORDER,
            fg_color=Colors.BG_SOFTER,
            placeholder_text="Enter your username or email",
        )
        self.username_entry.pack(pady=(6, 16))

        ctk.CTkLabel(form, text="Password", font=("Arial", 12, "bold"), anchor="w", text_color=Colors.TEXT_DARK).pack(fill="x")
        self.password_entry = ctk.CTkEntry(
            form,
            width=320,
            height=46,
            show="•",
            corner_radius=14,
            border_color=Colors.BORDER,
            fg_color=Colors.BG_SOFTER,
            placeholder_text="Enter your password",
        )
        self.password_entry.pack(pady=(6, 22))

        self.login_btn = ctk.CTkButton(
            form,
            text="LOGIN",
            width=320,
            height=48,
            font=("Arial", 14, "bold"),
            corner_radius=14,
            fg_color=Colors.SECONDARY,
            hover_color=Colors.PRIMARY,
            text_color=Colors.TEXT_DARK,
            command=self.login,
        )
        self.login_btn.pack(pady=10)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.pack(pady=12)
        ctk.CTkButton(actions, text="Sign Up", width=152, height=42, corner_radius=12, fg_color=Colors.BG_SOFT_BLUE, hover_color=Colors.ACCENT, text_color=Colors.TEXT_DARK, command=self.open_register).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="About Us", width=152, height=42, corner_radius=12, fg_color=Colors.BG_SOFT_BLUE, hover_color=Colors.ACCENT, text_color=Colors.TEXT_DARK, command=self.open_about).pack(side="left", padx=5)

        self.root.bind("<Return>", lambda _event: self.login())
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            show_error("Please fill all fields!")
            focus_widget(self.username_entry if not username else self.password_entry)
            return

        self.login_btn.configure(state="disabled", text="LOGGING IN...")
        thread = threading.Thread(target=self.perform_login, args=(username, password), daemon=True)
        thread.start()

    def perform_login(self, username, password):
        try:
            user = self.db.login_user(username, password)
            self.root.after(0, self.login_callback, user)
        except Exception as error:
            self.root.after(0, self.login_error, str(error))

    def login_callback(self, user):
        self.login_btn.configure(state="normal", text="LOGIN")
        if user:
            show_success(f"Welcome back, {user['full_name']}!")
            self.on_login_success(user)
            return

        show_error("Invalid username/email or password!")
        self.password_entry.delete(0, "end")
        focus_widget(self.password_entry)

    def login_error(self, error):
        self.login_btn.configure(state="normal", text="LOGIN")
        show_error(f"Login failed: {error}")

    def open_register(self):
        from gui.register_window import RegisterWindow

        RegisterWindow(self.root, self.db, on_success=self.prefill_username)

    def prefill_username(self, username):
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, username)
        self.password_entry.delete(0, "end")
        focus_widget(self.password_entry)

    def open_about(self):
        from gui.about_us_page import AboutUsPage

        AboutUsPage(self.root)
