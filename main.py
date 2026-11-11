import customtkinter as ctk

from config import Config
from database import Database


class MentorshipHubApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.db = Database()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.center_window(1000, 600)
        self.show_login()

    def center_window(self, width, height):
        """Center the window on screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def clear_root(self):
        """Remove all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        """Show login window."""
        self.clear_root()
        self.root.title(f"{Config.APP_NAME} - Login")

        from gui.login_window import LoginWindow

        LoginWindow(self.root, self.db, self.on_login_success)

    def on_login_success(self, user):
        """Handle successful login."""
        self.clear_root()
        self.center_window(1300, 750)

        from gui.main_window import MainWindow

        MainWindow(self.root, user, self.db, self.show_login)

    def run(self):
        """Run the application."""
        try:
            self.root.mainloop()
        finally:
            self.db.close()


if __name__ == "__main__":
    app = MentorshipHubApp()
    app.run()
