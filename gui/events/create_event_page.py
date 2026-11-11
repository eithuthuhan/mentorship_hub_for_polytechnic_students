# gui/events/create_event_page.py
import customtkinter as ctk
from datetime import datetime

from gui.ui_helpers import parse_date, parse_int, parse_time, require_text, show_error, show_success


class CreateEventPage:
    """Create Event Page"""

    def __init__(self, parent, user, db, on_created=None):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Create New Event")
        self.window.geometry("600x700")
        self.user = user
        self.db = db
        self.on_created = on_created

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
        """Setup create event UI"""
        main = ctk.CTkFrame(self.window, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(main, text="Create New Event", font=("Arial", 24, "bold"), text_color="#1F3B5B").pack(pady=(0, 20))

        form = ctk.CTkScrollableFrame(main, fg_color="transparent")
        form.pack(fill="both", expand=True)

        ctk.CTkLabel(form, text="Event Title *", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.title_entry = ctk.CTkEntry(form, height=40, font=("Arial", 12))
        self.title_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Description *", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.desc_text = ctk.CTkTextbox(form, height=100, font=("Arial", 12))
        self.desc_text.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Event Type *", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.type_var = ctk.StringVar(value="workshop")
        type_combo = ctk.CTkComboBox(
            form,
            width=200,
            height=35,
            values=["workshop", "seminar", "hackathon", "webinar", "career_fair"],
            variable=self.type_var,
        )
        type_combo.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(form, text="Mode *", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.mode_var = ctk.StringVar(value="online")
        mode_frame = ctk.CTkFrame(form, fg_color="transparent")
        mode_frame.pack(anchor="w", pady=(0, 10))

        for value, text in [("online", "Online"), ("offline", "Offline"), ("hybrid", "Hybrid")]:
            ctk.CTkRadioButton(mode_frame, text=text, value=value, variable=self.mode_var).pack(side="left", padx=5)

        ctk.CTkLabel(form, text="Location/Platform *", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.location_entry = ctk.CTkEntry(form, height=40, font=("Arial", 12), placeholder_text="e.g., Zoom, Room 101, Auditorium")
        self.location_entry.pack(fill="x", pady=(0, 10))

        date_frame = ctk.CTkFrame(form, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 10))
        date_frame.grid_columnconfigure(0, weight=1)
        date_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(date_frame, text="Start Date *", font=("Arial", 12), text_color="#1F3B5B").grid(row=0, column=0, sticky="w", pady=(10, 5))
        self.start_date = ctk.CTkEntry(date_frame, height=35, font=("Arial", 12), placeholder_text="YYYY-MM-DD")
        self.start_date.grid(row=1, column=0, padx=(0, 5), sticky="ew")
        self.start_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkLabel(date_frame, text="Start Time *", font=("Arial", 12), text_color="#1F3B5B").grid(row=0, column=1, sticky="w", pady=(10, 5))
        self.start_time = ctk.CTkEntry(date_frame, height=35, font=("Arial", 12), placeholder_text="HH:MM")
        self.start_time.grid(row=1, column=1, padx=(5, 0), sticky="ew")
        self.start_time.insert(0, "09:00")

        ctk.CTkLabel(date_frame, text="End Date (optional)", font=("Arial", 12), text_color="#1F3B5B").grid(row=2, column=0, sticky="w", pady=(10, 5))
        self.end_date = ctk.CTkEntry(date_frame, height=35, font=("Arial", 12), placeholder_text="YYYY-MM-DD")
        self.end_date.grid(row=3, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkLabel(date_frame, text="End Time (optional)", font=("Arial", 12), text_color="#1F3B5B").grid(row=2, column=1, sticky="w", pady=(10, 5))
        self.end_time = ctk.CTkEntry(date_frame, height=35, font=("Arial", 12), placeholder_text="HH:MM")
        self.end_time.grid(row=3, column=1, padx=(5, 0), sticky="ew")

        ctk.CTkLabel(form, text="Max Participants (0 for unlimited)", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.max_entry = ctk.CTkEntry(form, height=40, font=("Arial", 12))
        self.max_entry.pack(fill="x", pady=(0, 10))
        self.max_entry.insert(0, "0")

        ctk.CTkLabel(form, text="Registration Deadline (optional)", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.deadline_entry = ctk.CTkEntry(form, height=40, font=("Arial", 12), placeholder_text="YYYY-MM-DD")
        self.deadline_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Prerequisites (optional)", font=("Arial", 12), text_color="#1F3B5B", anchor="w").pack(fill="x", pady=(10, 5))
        self.prereq_text = ctk.CTkTextbox(form, height=60, font=("Arial", 12))
        self.prereq_text.pack(fill="x", pady=(0, 10))

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)

        ctk.CTkButton(btn_frame, text="Create Event", height=45, fg_color="#7FC8A9", command=self.create_event).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Cancel", height=45, fg_color="#F29B9B", command=self.window.destroy).pack(side="right", padx=5, expand=True, fill="x")

    def create_event(self):
        """Validate and create event in database."""
        try:
            title = require_text(self.title_entry.get(), "Event title")
            description = require_text(self.desc_text.get("1.0", "end-1c"), "Description")
            venue_text = require_text(self.location_entry.get(), "Location/Platform")
            start_date = parse_date(self.start_date.get(), "Start date")
            start_time = parse_time(self.start_time.get(), "Start time")
            max_participants = parse_int(self.max_entry.get() or "0", "Max participants", minimum=0)
        except ValueError as error:
            show_error(str(error))
            return

        end_date_input = self.end_date.get().strip()
        end_time_input = self.end_time.get().strip()
        deadline_input = self.deadline_entry.get().strip()

        try:
            end_date = parse_date(end_date_input, "End date") if end_date_input else None
            end_time = parse_time(end_time_input, "End time") if end_time_input else None
            deadline = parse_date(deadline_input, "Registration deadline") if deadline_input else None
        except ValueError as error:
            show_error(str(error))
            return

        if bool(end_date_input) != bool(end_time_input):
            show_error("End date and end time must be provided together.")
            return

        if end_date and end_time:
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)
            if end_dt <= start_dt:
                show_error("End date/time must be later than start date/time.")
                return

        if deadline and deadline > start_date:
            show_error("Registration deadline cannot be after the event start date.")
            return

        mode = self.mode_var.get()
        location = venue_text if mode in ("offline", "hybrid") else None
        platform = venue_text if mode in ("online", "hybrid") else None
        prerequisites = self.prereq_text.get("1.0", "end-1c").strip() or None

        event_data = {
            'title': title,
            'description': description,
            'event_type': self.type_var.get(),
            'mode': mode,
            'organizer_id': self.user['user_id'],
            'start_date': start_date,
            'start_time': start_time,
            'end_date': end_date,
            'end_time': end_time,
            'max_participants': max_participants,
            'location': location,
            'platform': platform,
            'prerequisites': prerequisites,
            'registration_deadline': deadline,
        }

        event_id = self.db.create_event(event_data)
        if not event_id or event_id == -1:
            show_error("Failed to create event.")
            return

        show_success("Event created successfully!")
        if callable(self.on_created):
            self.on_created()
        self.window.destroy()
