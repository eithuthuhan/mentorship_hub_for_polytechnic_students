# config.py
import os


class Config:
    # Database Configuration
    DB_HOST = os.getenv('MENTORSHIP_DB_HOST', 'localhost')
    DB_USER = os.getenv('MENTORSHIP_DB_USER', 'root')
    DB_PASSWORD = os.getenv('MENTORSHIP_DB_PASSWORD', '')
    DB_NAME = os.getenv('MENTORSHIP_DB_NAME', 'mentorship_hub')

    # App Configuration
    APP_NAME = 'Mentorship Hub'
    APP_VERSION = '2.0.0'
    COMPANY = 'Polytechnic University'

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

    # Security
    PASSWORD_MIN_LENGTH = 6
    SESSION_TIMEOUT = 1800  # 30 minutes in seconds
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = 900  # 15 minutes

    # Pagination
    ITEMS_PER_PAGE = 20

    # File Upload
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

    # Email (optional)
    SMTP_SERVER = os.getenv('MENTORSHIP_SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('MENTORSHIP_SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('MENTORSHIP_SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('MENTORSHIP_SMTP_PASSWORD', '')
    FROM_EMAIL = os.getenv('MENTORSHIP_FROM_EMAIL', 'noreply@mentorshiphub.com')
