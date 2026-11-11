import customtkinter as ctk
from colors import Colors
from gui.ui_helpers import focus_widget, parse_int, show_error, show_success, validate_email


class RegisterWindow:
    """Self-registration window backed by MySQL users table."""

    def __init__(self, parent, db, on_success=None):
        self.db = db
        self.on_success = on_success
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Create Account")
        self.window.geometry("600x760")
        self.window.configure(fg_color=Colors.BG_LIGHT)
        self.window.grab_set()
        self.center_window()
        self.setup_ui()

    def center_window(self):
        self.window.update_idletasks()
        width, height = 600, 760
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        shell = ctk.CTkFrame(self.window, fg_color=Colors.BG_WHITE, corner_radius=24, border_width=1, border_color=Colors.BORDER)
        shell.pack(fill="both", expand=True, padx=18, pady=18)

        main = ctk.CTkScrollableFrame(shell, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(main, text="Create Your Account", font=("Arial", 28, "bold"), text_color=Colors.TEXT_DARK).pack(pady=(0, 6))
        ctk.CTkLabel(
            main,
            text="Fill in your information to join the platform.",
            font=("Arial", 12),
            text_color=Colors.TEXT_MUTED,
        ).pack(pady=(0, 18))

        self.entries = {}
        self.add_entry(main, "Full Name", "full_name")
        self.add_entry(main, "Username", "username")
        self.add_entry(main, "Email", "email")
        self.add_entry(main, "Password", "password", show="•")
        self.add_entry(main, "Confirm Password", "confirm_password", show="•")

        ctk.CTkLabel(main, text="Role", anchor="w", text_color=Colors.TEXT_DARK, font=("Arial", 12, "bold")).pack(fill="x", pady=(12, 4))
        self.role_var = ctk.StringVar(value="junior_student")
        role_values = ["junior_student", "senior_student", "teacher"]
        ctk.CTkComboBox(
            main,
            values=role_values,
            variable=self.role_var,
            command=self.on_role_change,
            height=40,
            corner_radius=12,
            border_color=Colors.BORDER,
            button_color=Colors.SECONDARY,
            button_hover_color=Colors.PRIMARY,
            fg_color=Colors.BG_SOFTER,
            text_color=Colors.TEXT_DARK,
        ).pack(fill="x")

        self.add_entry(main, "Department", "department")
        self.add_entry(main, "Major", "major")
        self.add_entry(main, "Year", "year")
        self.add_entry(main, "Phone", "phone")
        self.add_entry(main, "Student ID", "student_id")
        self.add_entry(main, "Teacher ID", "teacher_id")

        ctk.CTkLabel(main, text="Short Bio", anchor="w", text_color=Colors.TEXT_DARK, font=("Arial", 12, "bold")).pack(fill="x", pady=(12, 4))
        self.bio_text = ctk.CTkTextbox(main, height=110, corner_radius=12, border_width=1, border_color=Colors.BORDER, fg_color=Colors.BG_SOFTER, text_color=Colors.TEXT_DARK)
        self.bio_text.pack(fill="x")

        btns = ctk.CTkFrame(main, fg_color="transparent")
        btns.pack(fill="x", pady=20)
        ctk.CTkButton(btns, text="Register", fg_color=Colors.SECONDARY, hover_color=Colors.PRIMARY, text_color=Colors.TEXT_DARK, corner_radius=14, height=44, command=self.register).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btns, text="Cancel", fg_color=Colors.BG_SOFT_BLUE, hover_color=Colors.ACCENT, text_color=Colors.TEXT_DARK, corner_radius=14, height=44, command=self.window.destroy).pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.on_role_change(self.role_var.get())

    def add_entry(self, parent, label, key, show=None):
        ctk.CTkLabel(parent, text=label, anchor="w", text_color=Colors.TEXT_DARK, font=("Arial", 12, "bold")).pack(fill="x", pady=(12, 4))
        entry = ctk.CTkEntry(parent, height=40, show=show or "", corner_radius=12, border_color=Colors.BORDER, fg_color=Colors.BG_SOFTER, text_color=Colors.TEXT_DARK)
        entry.pack(fill="x")
        self.entries[key] = entry

    def on_role_change(self, value):
        is_teacher = value == "teacher"
        self.entries["teacher_id"].configure(state="normal" if is_teacher else "disabled")
        self.entries["student_id"].configure(state="disabled" if is_teacher else "normal")
        self.entries["year"].configure(state="disabled" if is_teacher else "normal")
        if is_teacher:
            self.entries["year"].delete(0, "end")
            self.entries["student_id"].delete(0, "end")
        else:
            self.entries["teacher_id"].delete(0, "end")

    def register(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}
        data["role"] = self.role_var.get()
        data["bio"] = self.bio_text.get("1.0", "end-1c").strip()

        required = ["full_name", "username", "email", "password", "confirm_password"]
        missing = [k for k in required if not data.get(k)]
        if missing:
            show_error("Please fill all required fields.", "Missing Data")
            focus_widget(self.entries[missing[0]])
            return

        if data["password"] != data["confirm_password"]:
            show_error("Passwords do not match.", "Password Error")
            focus_widget(self.entries["confirm_password"])
            return

        try:
            data["email"] = validate_email(data["email"])
            data["year"] = parse_int(data.get("year"), "Year")
        except ValueError as error:
            show_error(str(error), "Validation Error")
            return

        if self.db.get_user_by_username(data["username"]):
            show_error("This username already exists.", "Duplicate")
            focus_widget(self.entries["username"])
            return
        if self.db.get_user_by_email(data["email"]):
            show_error("This email already exists.", "Duplicate")
            focus_widget(self.entries["email"])
            return

        payload = {
            "full_name": data["full_name"],
            "username": data["username"],
            "email": data["email"],
            "password": data["password"],
            "role": data["role"],
            "department": data.get("department") or None,
            "major": data.get("major") or None,
            "year": data.get("year"),
            "phone": data.get("phone") or None,
            "student_id": data.get("student_id") or None,
            "teacher_id": data.get("teacher_id") or None,
            "bio": data.get("bio") or None,
        }

        new_id = self.db.register_user(payload)
        if new_id == -1:
            show_error("Could not save the account to the database.", "Registration Failed")
            return

        show_success("Account created successfully. You can login with this account now.")
        if callable(self.on_success):
            self.on_success(payload["username"])
        self.window.destroy()
