import customtkinter as ctk
from gui.ui_helpers import parse_int, show_error, show_success, validate_email


class EditProfilePage:
    """Edit Profile Page"""

    def __init__(self, parent, user, db, refresh_callback=None):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Edit Profile")
        self.window.geometry("500x600")
        self.user = user
        self.db = db
        self.refresh_callback = refresh_callback

        self.center_window()
        self.window.transient(parent.winfo_toplevel())
        self.window.grab_set()
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after(250, lambda: self.window.attributes("-topmost", False))
        self.window.focus_force()
        self.setup_ui()

    def center_window(self):
        self.window.update_idletasks()
        width = 500
        height = 600
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        self.window.configure(fg_color="#F6FAFF")
        main = ctk.CTkFrame(self.window, fg_color="#F6FAFF")
        main.pack(fill="both", expand=True, padx=30, pady=20)

        hero = ctk.CTkFrame(main, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#D7E6F7")
        hero.pack(fill="x", pady=(0,18))
        ctk.CTkLabel(hero, text="Edit Profile", font=("Arial", 24, "bold"), text_color="#1F3B5B").pack(anchor="w", padx=18, pady=(16,4))
        ctk.CTkLabel(hero, text="Update the details that appear across mentorship, events, and your member profile.", font=("Arial", 12), text_color="#6F8098", wraplength=420, justify="left").pack(anchor="w", padx=18, pady=(0,16))
        form = ctk.CTkScrollableFrame(main, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#D7E6F7")
        form.pack(fill="both", expand=True)

        def add_entry(label, value=""):
            ctk.CTkLabel(form, text=label, font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
            entry = ctk.CTkEntry(form, height=40, font=("Arial", 12), fg_color="#F9FBFF", border_color="#D7E6F7")
            entry.insert(0, value or "")
            entry.pack(fill="x", pady=(0,10))
            return entry

        self.name_entry = add_entry("Full Name", self.user.get('full_name', ''))
        self.email_entry = add_entry("Email", self.user.get('email', ''))
        self.phone_entry = add_entry("Phone", self.user.get('phone', ''))
        self.dept_entry = add_entry("Department", self.user.get('department', ''))
        self.major_entry = add_entry("Major", self.user.get('major', ''))

        ctk.CTkLabel(form, text="Year", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        values = ["", "1", "2", "3", "4", "5"]
        self.year_var = ctk.StringVar(value=str(self.user.get('year') or ""))
        year_spin = ctk.CTkComboBox(form, width=160, height=38, values=values, variable=self.year_var, fg_color="#F9FBFF", border_color="#D7E6F7", button_color="#78AFFF")
        year_spin.pack(anchor="w", pady=(0,10))

        self.city_entry = add_entry("City", self.user.get('city', ''))
        self.country_entry = add_entry("Country", self.user.get('country', 'Myanmar'))

        ctk.CTkLabel(form, text="Bio", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        self.bio_text = ctk.CTkTextbox(form, height=120, font=("Arial", 12), fg_color="#F9FBFF", border_color="#D7E6F7")
        self.bio_text.insert("1.0", self.user.get('bio', ''))
        self.bio_text.pack(fill="x", pady=(0,20))

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="Save Changes", height=46, corner_radius=14, fg_color="#78AFFF", hover_color="#5F97EC", command=self.save_profile).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Cancel", height=46, corner_radius=14, fg_color="#EEF4FF", text_color="#1F3B5B", hover_color="#E1ECFF", command=self.window.destroy).pack(side="right", padx=5, expand=True, fill="x")

    def save_profile(self):
        full_name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not full_name or not email:
            show_error("Full name and email are required.")
            return

        if not validate_email(email):
            show_error("Please enter a valid email address.")
            return

        year_value = self.year_var.get().strip()
        try:
            year = parse_int(year_value, "Year", minimum=1) if year_value else None
        except ValueError as error:
            show_error(str(error))
            return

        data = {
            'full_name': full_name,
            'email': email,
            'phone': self.phone_entry.get().strip(),
            'department': self.dept_entry.get().strip(),
            'major': self.major_entry.get().strip(),
            'year': year,
            'city': self.city_entry.get().strip(),
            'country': self.country_entry.get().strip() or 'Myanmar',
            'bio': self.bio_text.get("1.0", "end-1c").strip(),
        }

        if not self.db.update_user(self.user['user_id'], data):
            show_error("Failed to update profile.")
            return

        refreshed = self.db.get_user_by_id(self.user['user_id'])
        if refreshed:
            self.user.clear()
            self.user.update(refreshed)
        if self.refresh_callback:
            self.refresh_callback()
        show_success("Profile updated successfully!")
        self.window.destroy()
