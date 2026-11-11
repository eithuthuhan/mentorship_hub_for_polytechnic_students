# gui/announcements/create_announcement_page.py
import customtkinter as ctk
from gui.ui_helpers import require_text, show_error, show_success

class CreateAnnouncementPage:
    """Create Announcement Page"""
    
    def __init__(self, parent, user, db):
        self.parent = parent  # parent is AnnouncementsPage
        self.user = user
        self.db = db
        
        # Get the main window from parent
        self.main_window = parent.root if hasattr(parent, 'root') else parent.winfo_toplevel()
        
        self.window = ctk.CTkToplevel(self.main_window)
        self.window.title("Create New Announcement")
        self.window.geometry("600x700")
        
        self.center_window()
        self.setup_ui()
        self.window.grab_set()
    
    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = 600
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup create announcement UI"""
        main = ctk.CTkFrame(self.window, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Title
        ctk.CTkLabel(main, text="Create New Announcement", font=("Arial", 24, "bold"),
                    text_color="#1F3B5B").pack(pady=(0,20))
        
        # Form
        form = ctk.CTkScrollableFrame(main, fg_color="transparent")
        form.pack(fill="both", expand=True)
        
        # Title
        ctk.CTkLabel(form, text="Title *", font=("Arial", 12),
                    text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        self.title_entry = ctk.CTkEntry(form, height=40, font=("Arial", 12))
        self.title_entry.pack(fill="x", pady=(0,10))
        
        # Content
        ctk.CTkLabel(form, text="Content *", font=("Arial", 12),
                    text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        self.content_text = ctk.CTkTextbox(form, height=150, font=("Arial", 12))
        self.content_text.pack(fill="x", pady=(0,10))
        
        # Category
        ctk.CTkLabel(form, text="Category *", font=("Arial", 12),
                    text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        self.category_var = ctk.StringVar(value="general")
        category_combo = ctk.CTkComboBox(form, width=200, height=35,
                                         values=["academic", "event", "opportunity", "general", "emergency"],
                                         variable=self.category_var)
        category_combo.pack(anchor="w", pady=(0,10))
        
        # Priority
        ctk.CTkLabel(form, text="Priority *", font=("Arial", 12),
                    text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        self.priority_var = ctk.StringVar(value="medium")
        priority_frame = ctk.CTkFrame(form, fg_color="transparent")
        priority_frame.pack(anchor="w", pady=(0,10))
        
        priorities = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")]
        for value, text in priorities:
            ctk.CTkRadioButton(priority_frame, text=text, value=value,
                              variable=self.priority_var).pack(side="left", padx=5)
        
        # Target Audience
        ctk.CTkLabel(form, text="Target Audience (leave empty for all)", font=("Arial", 12),
                    text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        
        # Roles
        ctk.CTkLabel(form, text="Roles:", font=("Arial", 11),
                    text_color="#6F8098").pack(anchor="w", pady=(5,2))
        role_frame = ctk.CTkFrame(form, fg_color="transparent")
        role_frame.pack(fill="x", pady=(0,5))
        
        self.role_vars = {}
        roles = ["teacher", "senior_student", "junior_student"]
        role_labels = ["Teachers", "Senior Students", "Junior Students"]
        
        for role, label in zip(roles, role_labels):
            var = ctk.BooleanVar(value=True)
            self.role_vars[role] = var
            ctk.CTkCheckBox(role_frame, text=label, variable=var).pack(side="left", padx=5)
        
        # Departments
        ctk.CTkLabel(form, text="Departments (comma separated):", font=("Arial", 11),
                    text_color="#6F8098").pack(anchor="w", pady=(5,2))
        self.dept_entry = ctk.CTkEntry(form, height=35, font=("Arial", 12))
        self.dept_entry.pack(fill="x", pady=(0,10))
        
        # Years
        ctk.CTkLabel(form, text="Years (comma separated):", font=("Arial", 11),
                    text_color="#6F8098").pack(anchor="w", pady=(5,2))
        self.year_entry = ctk.CTkEntry(form, height=35, font=("Arial", 12))
        self.year_entry.pack(fill="x", pady=(0,10))
        
        # Link URL
        ctk.CTkLabel(form, text="Link URL (optional)", font=("Arial", 12),
                    text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10,5))
        self.link_entry = ctk.CTkEntry(form, height=40, font=("Arial", 12),
                                       placeholder_text="https://...")
        self.link_entry.pack(fill="x", pady=(0,10))
        
        # Options
        options_frame = ctk.CTkFrame(form, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)
        
        self.pin_var = ctk.BooleanVar()
        ctk.CTkCheckBox(options_frame, text="Pin to top", variable=self.pin_var).pack(side="left", padx=5)
        
        self.comments_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="Allow comments", variable=self.comments_var).pack(side="left", padx=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(btn_frame, text="Post Announcement", height=45,
                     fg_color="#7FC8A9", command=self.create_announcement).pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkButton(btn_frame, text="Cancel", height=45,
                     fg_color="#F29B9B", command=self.window.destroy).pack(side="right", padx=5, expand=True, fill="x")
    
    def create_announcement(self):
        """Create announcement"""
        try:
            title = require_text(self.title_entry.get(), "Title")
            content = require_text(self.content_text.get("1.0", "end-1c"), "Content")
        except ValueError as error:
            show_error(str(error))
            return

        announcement_data = {
            'title': title,
            'content': content,
            'announcer_id': self.user['user_id'],
            'category': self.category_var.get(),
            'priority': self.priority_var.get(),
            'is_pinned': self.pin_var.get(),
            'allow_comments': self.comments_var.get(),
            'status': 'published'
        }

        link_url = self.link_entry.get().strip()
        if link_url:
            announcement_data['link_url'] = link_url

        selected_roles = [role for role, var in self.role_vars.items() if var.get()]
        if selected_roles and len(selected_roles) < 3:
            announcement_data['target_roles'] = selected_roles

        depts = [d.strip() for d in self.dept_entry.get().split(',') if d.strip()]
        if depts:
            announcement_data['target_departments'] = depts

        years = [int(y.strip()) for y in self.year_entry.get().split(',') if y.strip().isdigit()]
        if years:
            announcement_data['target_years'] = years

        announcement_id = self.db.create_announcement(announcement_data)

        if announcement_id and announcement_id != -1:
            show_success("Announcement posted successfully!")
            self.refresh_parent()
            self.window.destroy()
        else:
            show_error("Failed to post announcement")
    
    def refresh_parent(self):
        """Refresh the parent announcements page"""
        try:
            if hasattr(self.parent, 'load_announcements'):
                self.parent.load_announcements()
            elif hasattr(self.parent, 'refresh_announcements'):
                self.parent.refresh_announcements()
        except Exception as e:
            print(f"Error refreshing parent: {e}")