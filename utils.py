# utils.py
import re
import hashlib
import secrets
from datetime import datetime, timedelta
from tkinter import messagebox
import os

class Utils:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate Myanmar phone number"""
        pattern = r'^(09|\+?959)\d{7,9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def hash_password(password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}"
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        salt, hash_value = hashed.split('$')
        hash_obj = hashlib.sha256((password + salt).encode())
        return hash_obj.hexdigest() == hash_value
    
    @staticmethod
    def generate_token():
        """Generate random token for email verification"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def format_datetime(dt):
        """Format datetime for display"""
        if not dt:
            return ''
        return dt.strftime('%Y-%m-%d %H:%M')
    
    @staticmethod
    def format_date(d):
        """Format date for display"""
        if not d:
            return ''
        return d.strftime('%Y-%m-%d')
    
    @staticmethod
    def time_ago(dt):
        """Convert datetime to 'time ago' format"""
        if not dt:
            return ''
        
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    
    @staticmethod
    def truncate_text(text, max_length=100):
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def safe_int(value, default=0):
        """Safely convert to integer"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_float(value, default=0.0):
        """Safely convert to float"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def show_error(title, message):
        """Show error message box"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_info(title, message):
        """Show info message box"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(title, message):
        """Show warning message box"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def ask_yes_no(title, message):
        """Ask yes/no question"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def is_allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed"""
        ext = Utils.get_file_extension(filename)
        return ext[1:] in allowed_extensions if ext else False