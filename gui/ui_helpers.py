import re
from datetime import datetime
from tkinter import messagebox


def show_error(message, title="Error"):
    messagebox.showerror(title, message)


def show_success(message, title="Success"):
    messagebox.showinfo(title, message)


def show_info(message, title="Info"):
    messagebox.showinfo(title, message)


def ask_confirm(message, title="Confirm"):
    return messagebox.askyesno(title, message)


def require_text(value, field_name):
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required")
    return text


def optional_text(value):
    text = (value or "").strip()
    return text or None


def validate_email(email):
    email = require_text(email, "Email")
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(pattern, email):
        raise ValueError("Please enter a valid email address.")
    return email


def parse_int(value, field_name, minimum=None, allow_empty=True):
    text = (value or "").strip()
    if not text:
        return None if allow_empty else 0
    if not text.isdigit():
        raise ValueError(f"{field_name} must be a whole number")
    parsed = int(text)
    if minimum is not None and parsed < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}")
    return parsed


def parse_date(value, field_name, required=False):
    text = (value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field_name} is required")
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be in YYYY-MM-DD format") from exc


def parse_time(value, field_name, required=False):
    text = (value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field_name} is required")
        return None
    try:
        return datetime.strptime(text, "%H:%M").time()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be in HH:MM format") from exc


def focus_widget(widget):
    try:
        widget.focus()
    except Exception:
        pass
