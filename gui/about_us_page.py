import customtkinter as ctk
from colors import Colors


class AboutUsPage:
    def __init__(self, parent):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("About Mentorship Hub")
        self.window.geometry("560x460")
        self.window.configure(fg_color=Colors.BG_LIGHT)
        self.window.grab_set()
        self.setup_ui()

    def setup_ui(self):
        shell = ctk.CTkFrame(self.window, fg_color=Colors.BG_WHITE, corner_radius=24, border_width=1, border_color=Colors.BORDER)
        shell.pack(fill="both", expand=True, padx=18, pady=18)

        main = ctk.CTkFrame(shell, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=24)

        badge = ctk.CTkFrame(main, fg_color=Colors.BG_SOFT_BLUE, corner_radius=999)
        badge.pack(anchor="center", pady=(0, 14))
        ctk.CTkLabel(badge, text="About Mentorship Hub", font=("Arial", 12, "bold"), text_color=Colors.TEXT_DARK).pack(padx=14, pady=8)

        ctk.CTkLabel(main, text="A cleaner space for student collaboration", font=("Arial", 26, "bold"), text_color=Colors.TEXT_DARK).pack(pady=(0, 12))
        body = (
            "Mentorship Hub is a university project designed to connect junior students, senior students, and teachers in one place.\n\n"
            "Main goals:\n"
            "• real self-registration and persistent login\n"
            "• mentorship matching by role\n"
            "• events, announcements, and profile management\n"
            "• practical learning support for NSPU students\n\n"
            "This version keeps your existing frame structure while refreshing the look with a softer and more modern interface."
        )
        ctk.CTkLabel(main, text=body, justify="left", wraplength=470, font=("Arial", 13), text_color=Colors.TEXT_MUTED).pack(anchor="w")
        ctk.CTkButton(main, text="Close", width=160, height=42, corner_radius=14, fg_color=Colors.SECONDARY, hover_color=Colors.PRIMARY, text_color=Colors.TEXT_DARK, command=self.window.destroy).pack(pady=22)
