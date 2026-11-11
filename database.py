# database.py
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import json
from config import Config
from utils import Utils

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                charset='utf8mb4',
                use_unicode=True,
                autocommit=False
            )
            if self.connection.is_connected():
                print("✅ Database connected successfully")
                self.connection.autocommit = True
                return True
        except Error as e:
            print(f"❌ Database connection error: {e}")
            self.connection = None
        return False

    def _ensure_connection(self):
        if self.connection and self.connection.is_connected():
            return True
        return self.connect()
    
    def execute_query(self, query, params=None, dictionary=True):
        """Execute query and return results"""
        cursor = None
        is_select = query.strip().upper().startswith('SELECT')
        try:
            if not self._ensure_connection():
                return None if is_select else -1
            
            cursor = self.connection.cursor(dictionary=dictionary)
            cursor.execute(query, params or ())
            
            if is_select:
                return cursor.fetchall()

            self.connection.commit()
            if cursor.lastrowid:
                return cursor.lastrowid
            return cursor.rowcount
        except Error as e:
            print(f"❌ Query error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None if is_select else -1
        finally:
            if cursor:
                cursor.close()

    # ==================== USER METHODS ====================
    
    def login_user(self, username, password):
        """User login with username or email."""
        query = """
            SELECT * FROM users
            WHERE (username = %s OR email = %s)
              AND password = %s
              AND is_active = TRUE
            LIMIT 1
        """
        result = self.execute_query(query, (username, username, password))

        if result and len(result) > 0:
            user = result[0]
            self.execute_query(
                "UPDATE users SET last_login = NOW(), is_online = TRUE WHERE user_id = %s",
                (user['user_id'],),
                dictionary=False
            )
            self.log_activity(user['user_id'], 'login', 'User logged in')
            return self.get_user_by_id(user['user_id'])
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE user_id = %s"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        result = self.execute_query(query, (email,))
        return result[0] if result else None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = self.execute_query(query, (username,))
        return result[0] if result else None
    
    def create_user(self, user_data):
        """Create new user and return new user_id."""
        role = user_data.get('role', 'junior_student')
        if self.get_user_by_username(user_data['username']):
            raise ValueError('Username already exists')
        if self.get_user_by_email(user_data['email']):
            raise ValueError('Email already exists')

        student_id = user_data.get('student_id') or None
        teacher_id = user_data.get('teacher_id') or None
        if role == 'teacher' and not teacher_id:
            teacher_id = f"TCH-{user_data['username'][:6].upper()}"
        if role in ('junior_student', 'senior_student') and not student_id:
            student_id = f"STD-{user_data['username'][:6].upper()}"

        query = """
            INSERT INTO users (
                username, password, email, full_name, role,
                student_id, teacher_id, department, major, year,
                phone, bio, city, country, is_active, email_verified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, TRUE)
        """
        params = (
            user_data['username'],
            user_data['password'],
            user_data['email'],
            user_data['full_name'],
            role,
            student_id,
            teacher_id,
            user_data.get('department') or None,
            user_data.get('major') or None,
            user_data.get('year') or None,
            user_data.get('phone') or None,
            user_data.get('bio') or None,
            user_data.get('city') or None,
            user_data.get('country', 'Myanmar') or 'Myanmar'
        )
        user_id = self.execute_query(query, params, dictionary=False)
        if user_id == -1:
            return -1
        self.log_activity(user_id, 'profile_update', 'Account created')
        return user_id

    def register_user(self, user_data):
        """Friendly wrapper for self-registration."""
        try:
            return self.create_user(user_data)
        except ValueError as exc:
            print(f"Registration validation error: {exc}")
            return -1
    
    def update_user(self, user_id, data):
        """Update user profile"""
        query = """
            UPDATE users SET
                full_name = %s,
                email = %s,
                department = %s,
                major = %s,
                year = %s,
                bio = %s,
                phone = %s,
                city = %s,
                country = %s
            WHERE user_id = %s
        """
        params = (
            data.get('full_name', ''),
            data.get('email', ''),
            data.get('department', ''),
            data.get('major', ''),
            data.get('year') or None,
            data.get('bio', ''),
            data.get('phone', ''),
            data.get('city', ''),
            data.get('country', 'Myanmar'),
            user_id
        )
        result = self.execute_query(query, params, dictionary=False)
        if result != -1:
            self.log_activity(user_id, 'profile_update', 'Profile updated')
            return True
        return False
    
    def update_profile_picture(self, user_id, picture_path):
        """Update profile picture"""
        query = "UPDATE users SET profile_pic = %s WHERE user_id = %s"
        result = self.execute_query(query, (picture_path, user_id), dictionary=False)
        return result != -1 and result > 0
    
    def get_new_user_welcome_state(self, user_id):
        """Return dashboard welcome metadata for a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return {'is_new': False, 'created_at': None, 'activity_count': 0}

        activity_rows = self.execute_query(
            "SELECT COUNT(*) as count FROM user_activities WHERE user_id = %s",
            (user_id,),
        ) or [{'count': 0}]
        activity_count = activity_rows[0].get('count', 0) or 0

        created_at = user.get('created_at')
        is_new = activity_count <= 1
        if created_at:
            try:
                age_seconds = (datetime.now() - created_at).total_seconds()
                if age_seconds <= 60 * 60 * 24 * 14:
                    is_new = True
            except Exception:
                pass

        return {
            'is_new': bool(is_new),
            'created_at': created_at,
            'activity_count': activity_count,
        }

    def get_user_created_events(self, user_id, include_past=True):
        """Get events created by a specific user."""
        query = """
            SELECT e.*,
                   (SELECT COUNT(*) FROM event_participants ep WHERE ep.event_id = e.event_id AND ep.status = 'registered') AS registered_count
            FROM events e
            WHERE e.organizer_id = %s
        """
        params = [user_id]

        if not include_past:
            query += " AND e.status = 'upcoming' AND e.start_date >= CURDATE()"

        query += " ORDER BY e.start_date ASC, e.start_time ASC"
        return self.execute_query(query, params) or []

    def get_all_users(self, role=None, department=None, year=None):
        """Get all users with filters"""
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        
        if role:
            query += " AND role = %s"
            params.append(role)
        if department:
            query += " AND department = %s"
            params.append(department)
        if year:
            query += " AND year = %s"
            params.append(year)
        
        query += " ORDER BY full_name"
        return self.execute_query(query, params)
    
    def search_users(self, search_term):
        """Search users by name, username, email"""
        query = """
            SELECT * FROM users 
            WHERE full_name LIKE %s 
               OR username LIKE %s 
               OR email LIKE %s
            ORDER BY full_name
            LIMIT 50
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern, search_pattern))
    
    def deactivate_user(self, user_id):
        """Deactivate user account"""
        query = "UPDATE users SET is_active = FALSE WHERE user_id = %s"
        result = self.execute_query(query, (user_id,), dictionary=False)
        return result != -1
    
    def activate_user(self, user_id):
        """Activate user account"""
        query = "UPDATE users SET is_active = TRUE WHERE user_id = %s"
        result = self.execute_query(query, (user_id,), dictionary=False)
        return result != -1

    def verify_user_password(self, user_id, password):
        """Check whether the provided password matches the current user password."""
        query = """
            SELECT user_id FROM users
            WHERE user_id = %s AND password = %s AND is_active = TRUE
            LIMIT 1
        """
        result = self.execute_query(query, (user_id, password))
        return bool(result)

    def update_user_password(self, user_id, current_password, new_password):
        """Update a user's password after verifying the current password."""
        if not self.verify_user_password(user_id, current_password):
            return False

        query = "UPDATE users SET password = %s WHERE user_id = %s"
        result = self.execute_query(query, (new_password, user_id), dictionary=False)
        if result == -1:
            return False

        self.log_activity(user_id, 'profile_update', 'Password changed')
        return True

    def update_user_settings(self, user_id, settings):
        """Save supported profile/privacy settings for a user."""
        privacy = {
            'profile': settings.get('profile_visibility', 'public'),
            'email': 'public' if settings.get('show_email') else 'private',
            'phone': 'public' if settings.get('show_phone') else 'private',
        }
        query = """
            UPDATE users SET
                full_name = %s,
                preferred_language = %s,
                privacy_settings = %s
            WHERE user_id = %s
        """
        params = (
            settings.get('display_name') or '',
            settings.get('preferred_language') or 'English',
            json.dumps(privacy),
            user_id,
        )
        result = self.execute_query(query, params, dictionary=False)
        if result == -1:
            return False

        self.log_activity(user_id, 'profile_update', 'Settings updated')
        return True

    def soft_delete_user(self, user_id, password):
        """Deactivate a user account after password verification."""
        if not self.verify_user_password(user_id, password):
            return False

        query = """
            UPDATE users SET
                is_active = FALSE,
                is_online = FALSE,
                deleted_at = NOW()
            WHERE user_id = %s
        """
        result = self.execute_query(query, (user_id,), dictionary=False)
        if result == -1:
            return False

        self.log_activity(user_id, 'logout', 'Account deactivated by user')
        return True
    
    # ==================== SKILLS METHODS ====================
    
    def get_all_skills(self):
        """Get all skills"""
        query = "SELECT * FROM skills ORDER BY skill_name"
        return self.execute_query(query)
    
    def get_user_skills(self, user_id):
        """Get user's skills with proficiency"""
        query = """
            SELECT s.*, us.proficiency_level, us.years_experience, us.endorsed_count
            FROM skills s
            JOIN user_skills us ON s.skill_id = us.skill_id
            WHERE us.user_id = %s
            ORDER BY us.proficiency_level DESC
        """
        return self.execute_query(query, (user_id,))
    
    def add_user_skill(self, user_id, skill_id, proficiency_level, years_experience=0):
        """Add skill to user"""
        query = """
            INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience)
            VALUES (%s, %s, %s, %s)
        """
        result = self.execute_query(query, (user_id, skill_id, proficiency_level, years_experience), dictionary=False)
        return result != -1
    
    def remove_user_skill(self, user_id, skill_id):
        """Remove skill from user"""
        query = "DELETE FROM user_skills WHERE user_id = %s AND skill_id = %s"
        result = self.execute_query(query, (user_id, skill_id), dictionary=False)
        return result != -1
    

    def create_or_get_skill(self, skill_name, category='other', description=None):
        """Create skill if missing and return skill_id"""
        query = "SELECT skill_id FROM skills WHERE LOWER(skill_name) = LOWER(%s) LIMIT 1"
        result = self.execute_query(query, (skill_name,))
        if result:
            return result[0]['skill_id']
        insert = "INSERT INTO skills (skill_name, category, description) VALUES (%s, %s, %s)"
        skill_id = self.execute_query(insert, (skill_name, category, description), dictionary=False)
        return skill_id if skill_id != -1 else None

    def add_or_update_user_skill(self, user_id, skill_name, proficiency_level, years_experience=0, category='other'):
        """Add a new skill or update if it already exists for the user."""
        skill_id = self.create_or_get_skill(skill_name, category)
        if not skill_id:
            return False
        exists = self.execute_query(
            "SELECT user_skill_id FROM user_skills WHERE user_id = %s AND skill_id = %s LIMIT 1",
            (user_id, skill_id)
        )
        if exists:
            query = "UPDATE user_skills SET proficiency_level = %s, years_experience = %s WHERE user_id = %s AND skill_id = %s"
            result = self.execute_query(query, (proficiency_level, years_experience, user_id, skill_id), dictionary=False)
        else:
            query = "INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_experience) VALUES (%s, %s, %s, %s)"
            result = self.execute_query(query, (user_id, skill_id, proficiency_level, years_experience), dictionary=False)
        return result != -1

    def update_user_skill(self, user_id, old_skill_id, new_skill_name, proficiency_level, years_experience=0, category='other'):
        """Update an existing user skill, optionally changing the skill name."""
        new_skill_id = self.create_or_get_skill(new_skill_name, category)
        if not new_skill_id:
            return False
        query = "UPDATE user_skills SET skill_id = %s, proficiency_level = %s, years_experience = %s WHERE user_id = %s AND skill_id = %s"
        result = self.execute_query(query, (new_skill_id, proficiency_level, years_experience, user_id, old_skill_id), dictionary=False)
        return result != -1

    def endorse_skill(self, user_id, skill_id):
        """Endorse a user's skill"""
        query = "UPDATE user_skills SET endorsed_count = endorsed_count + 1 WHERE user_id = %s AND skill_id = %s"
        result = self.execute_query(query, (user_id, skill_id), dictionary=False)
        return result != -1
    
    # ==================== INTERESTS METHODS ====================
    
    def get_all_interests(self):
        """Get all interests"""
        query = "SELECT * FROM interests ORDER BY interest_name"
        return self.execute_query(query)
    
    def get_user_interests(self, user_id):
        """Get user's interests"""
        query = """
            SELECT i.*, ui.level
            FROM interests i
            JOIN user_interests ui ON i.interest_id = ui.interest_id
            WHERE ui.user_id = %s
            ORDER BY ui.level DESC
        """
        return self.execute_query(query, (user_id,))
    
    def add_user_interest(self, user_id, interest_id, level=3):
        """Add interest to user"""
        query = """
            INSERT INTO user_interests (user_id, interest_id, level)
            VALUES (%s, %s, %s)
        """
        result = self.execute_query(query, (user_id, interest_id, level), dictionary=False)
        return result != -1
    
    def remove_user_interest(self, user_id, interest_id):
        """Remove interest from user"""
        query = "DELETE FROM user_interests WHERE user_id = %s AND interest_id = %s"
        result = self.execute_query(query, (user_id, interest_id), dictionary=False)
        return result != -1
    
    # ==================== PROJECTS METHODS ====================
    
    def get_user_projects(self, user_id):
        """Get user's projects"""
        query = "SELECT * FROM projects WHERE user_id = %s ORDER BY start_date DESC"
        return self.execute_query(query, (user_id,))
    
    def create_project(self, user_id, project_data):
        """Create new project"""
        query = """
            INSERT INTO projects (
                user_id, project_name, description, technologies,
                role, project_url, github_url, start_date, end_date,
                is_current, achievements, team_size
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            project_data['project_name'],
            project_data.get('description', ''),
            project_data.get('technologies', ''),
            project_data.get('role', ''),
            project_data.get('project_url', ''),
            project_data.get('github_url', ''),
            project_data.get('start_date'),
            project_data.get('end_date'),
            project_data.get('is_current', False),
            project_data.get('achievements', ''),
            project_data.get('team_size', 1)
        )
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    def update_project(self, project_id, project_data):
        """Update project"""
        query = """
            UPDATE projects SET
                project_name = %s,
                description = %s,
                technologies = %s,
                role = %s,
                project_url = %s,
                github_url = %s,
                start_date = %s,
                end_date = %s,
                is_current = %s,
                achievements = %s,
                team_size = %s
            WHERE project_id = %s
        """
        params = (
            project_data['project_name'],
            project_data.get('description', ''),
            project_data.get('technologies', ''),
            project_data.get('role', ''),
            project_data.get('project_url', ''),
            project_data.get('github_url', ''),
            project_data.get('start_date'),
            project_data.get('end_date'),
            project_data.get('is_current', False),
            project_data.get('achievements', ''),
            project_data.get('team_size', 1),
            project_id
        )
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    def delete_project(self, project_id):
        """Delete project"""
        query = "DELETE FROM projects WHERE project_id = %s"
        result = self.execute_query(query, (project_id,), dictionary=False)
        return result != -1
    
    # ==================== CERTIFICATIONS METHODS ====================
    
    def get_user_certifications(self, user_id):
        """Get user's certifications"""
        query = "SELECT * FROM certifications WHERE user_id = %s ORDER BY issue_date DESC"
        return self.execute_query(query, (user_id,))
    
    def create_certification(self, user_id, cert_data):
        """Create new certification"""
        query = """
            INSERT INTO certifications (
                user_id, cert_name, issuing_organization,
                issue_date, expiry_date, credential_id,
                credential_url, cert_file, skills_gained
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            cert_data['cert_name'],
            cert_data['issuing_organization'],
            cert_data['issue_date'],
            cert_data.get('expiry_date'),
            cert_data.get('credential_id'),
            cert_data.get('credential_url'),
            cert_data.get('cert_file'),
            cert_data.get('skills_gained', '')
        )
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    def delete_certification(self, cert_id):
        """Delete certification"""
        query = "DELETE FROM certifications WHERE cert_id = %s"
        result = self.execute_query(query, (cert_id,), dictionary=False)
        return result != -1
    

    def update_certification(self, cert_id, cert_data):
        """Update certification"""
        query = """
            UPDATE certifications SET
                cert_name = %s,
                issuing_organization = %s,
                issue_date = %s,
                expiry_date = %s,
                credential_id = %s,
                credential_url = %s,
                cert_file = %s,
                skills_gained = %s
            WHERE cert_id = %s
        """
        params = (
            cert_data['cert_name'],
            cert_data['issuing_organization'],
            cert_data['issue_date'],
            cert_data.get('expiry_date'),
            cert_data.get('credential_id'),
            cert_data.get('credential_url'),
            cert_data.get('cert_file'),
            cert_data.get('skills_gained', ''),
            cert_id
        )
        result = self.execute_query(query, params, dictionary=False)
        return result != -1

    # ==================== EXPERIENCE METHODS ====================
    
    def get_user_experiences(self, user_id):
        """Get user's work experiences"""
        query = "SELECT * FROM experiences WHERE user_id = %s ORDER BY start_date DESC"
        return self.execute_query(query, (user_id,))
    
    def create_experience(self, user_id, exp_data):
        """Create new work experience"""
        query = """
            INSERT INTO experiences (
                user_id, company, position, start_date, end_date,
                is_current, description, technologies, supervisor_name,
                supervisor_contact, cert_file
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            exp_data['company'],
            exp_data['position'],
            exp_data['start_date'],
            exp_data.get('end_date'),
            exp_data.get('is_current', False),
            exp_data.get('description', ''),
            exp_data.get('technologies', ''),
            exp_data.get('supervisor_name', ''),
            exp_data.get('supervisor_contact', ''),
            exp_data.get('cert_file', '')
        )
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    def update_experience(self, exp_id, exp_data):
        """Update work experience"""
        query = """
            UPDATE experiences SET
                company = %s,
                position = %s,
                start_date = %s,
                end_date = %s,
                is_current = %s,
                description = %s,
                technologies = %s,
                supervisor_name = %s,
                supervisor_contact = %s,
                cert_file = %s
            WHERE exp_id = %s
        """
        params = (
            exp_data['company'],
            exp_data['position'],
            exp_data['start_date'],
            exp_data.get('end_date'),
            exp_data.get('is_current', False),
            exp_data.get('description', ''),
            exp_data.get('technologies', ''),
            exp_data.get('supervisor_name', ''),
            exp_data.get('supervisor_contact', ''),
            exp_data.get('cert_file', ''),
            exp_id
        )
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    def delete_experience(self, exp_id):
        """Delete work experience"""
        query = "DELETE FROM experiences WHERE exp_id = %s"
        result = self.execute_query(query, (exp_id,), dictionary=False)
        return result != -1
    
    # ==================== MENTORSHIP METHODS ====================
    
    # def get_mentors(self, user_id, search=None, department=None, skill=None):
    #     """Get available mentors"""
    #     query = """
    #         SELECT DISTINCT u.*,
    #             (SELECT COUNT(*) FROM mentorship_requests 
    #              WHERE mentor_id = u.user_id AND status = 'completed') as mentee_count,
    #             (SELECT AVG(mentee_rating) FROM mentorship_requests 
    #              WHERE mentor_id = u.user_id AND mentee_rating IS NOT NULL) as avg_rating
    #         FROM users u
    #         WHERE u.role IN ('teacher', 'senior_student')
    #         AND u.user_id != %s
    #         AND u.is_active = TRUE
    #     """
    #     params = [user_id]
        
    #     if search:
    #         query += " AND (u.full_name LIKE %s OR u.bio LIKE %s)"
    #         params.extend([f"%{search}%", f"%{search}%"])
        
    #     if department:
    #         query += " AND u.department = %s"
    #         params.append(department)
        
    #     if skill:
    #         query += """
    #             AND u.user_id IN (
    #                 SELECT user_id FROM user_skills us
    #                 JOIN skills s ON us.skill_id = s.skill_id
    #                 WHERE s.skill_name LIKE %s
    #             )
    #         """
    #         params.append(f"%{skill}%")
        
    #     query += " ORDER BY avg_rating DESC NULLS LAST, u.full_name"
    #     return self.execute_query(query, params)

    def get_mentors(self, user_id, search=None, department=None, skill=None):
        """Get role-aware mentors from database while preserving UI card data."""
        current_user = self.get_user_by_id(user_id)
        if not current_user:
            return []

        if current_user['role'] == 'junior_student':
            role_filter = ['teacher', 'senior_student']
        elif current_user['role'] == 'senior_student':
            role_filter = ['teacher']
        elif current_user['role'] == 'teacher':
            role_filter = ['senior_student']
        else:
            role_filter = ['teacher', 'senior_student', 'junior_student']

        placeholders = ', '.join(['%s'] * len(role_filter))
        query = f"""
            SELECT u.*,
                   COALESCE((
                       SELECT GROUP_CONCAT(s.skill_name SEPARATOR ', ')
                       FROM user_skills us
                       JOIN skills s ON s.skill_id = us.skill_id
                       WHERE us.user_id = u.user_id
                   ), 'Not specified') AS skills,
                   (SELECT COUNT(*) FROM mentorship_requests
                    WHERE mentor_id = u.user_id AND status = 'accepted') AS mentee_count,
                   (SELECT AVG(mentee_rating) FROM mentorship_requests
                    WHERE mentor_id = u.user_id AND mentee_rating IS NOT NULL) AS avg_rating
            FROM users u
            WHERE u.user_id != %s
              AND u.is_active = TRUE
              AND u.role IN ({placeholders})
        """
        params = [user_id] + role_filter

        if search and search.strip():
            like = f"%{search.strip()}%"
            query += " AND (u.full_name LIKE %s OR u.bio LIKE %s OR u.major LIKE %s)"
            params.extend([like, like, like])

        if department and department != 'All':
            query += " AND u.department = %s"
            params.append(department)

        if skill and str(skill).strip():
            skill_like = f"%{str(skill).strip()}%"
            query += " AND u.user_id IN (SELECT us.user_id FROM user_skills us JOIN skills s ON s.skill_id = us.skill_id WHERE s.skill_name LIKE %s)"
            params.append(skill_like)

        query += " ORDER BY avg_rating DESC, u.full_name ASC"
        return self.execute_query(query, params) or []


    def get_available_mentor_departments(self, user_id):
        """Return distinct departments visible in the mentor directory for the current user."""
        current_user = self.get_user_by_id(user_id)
        if not current_user:
            return []

        if current_user['role'] == 'junior_student':
            role_filter = ['teacher', 'senior_student']
        elif current_user['role'] == 'senior_student':
            role_filter = ['teacher']
        elif current_user['role'] == 'teacher':
            role_filter = ['senior_student']
        else:
            role_filter = ['teacher', 'senior_student', 'junior_student']

        placeholders = ', '.join(['%s'] * len(role_filter))
        query = f"""
            SELECT DISTINCT COALESCE(NULLIF(TRIM(department), ''), 'General') AS department
            FROM users
            WHERE user_id != %s
              AND is_active = TRUE
              AND role IN ({placeholders})
            ORDER BY department ASC
        """
        rows = self.execute_query(query, [user_id] + role_filter) or []
        return [row['department'] for row in rows if row.get('department')]

    def create_mentorship_request(self, mentor_id, mentee_id, subject, message, goals=None, duration=3):
        """Create mentorship request and prevent duplicate or invalid requests."""
        subject = (subject or '').strip()
        message = (message or '').strip()
        goals = (goals or '').strip() or None
        if not mentor_id or not mentee_id or mentor_id == mentee_id or not subject or not message:
            return -1

        mentor = self.get_user_by_id(mentor_id)
        mentee = self.get_user_by_id(mentee_id)
        if not mentor or not mentee:
            return -1
        if not mentor.get('is_active') or not mentee.get('is_active'):
            return -1
        if mentor.get('role') not in ('teacher', 'senior_student'):
            return -1
        if mentee.get('role') not in ('junior_student', 'senior_student'):
            return -1

        duplicate_query = """
            SELECT request_id FROM mentorship_requests
            WHERE mentor_id = %s AND mentee_id = %s AND status IN ('pending', 'accepted')
            LIMIT 1
        """
        existing = self.execute_query(duplicate_query, (mentor_id, mentee_id))
        if existing:
            return -1

        query = """
            INSERT INTO mentorship_requests (
                mentor_id, mentee_id, subject, message, goals, duration_months
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        result = self.execute_query(query, (mentor_id, mentee_id, subject, message, goals, duration), dictionary=False)

        if result != -1:
            self.log_activity(mentee_id, 'mentorship_request_sent', f"Request to mentor {mentor_id}")
            self.create_notification(
                mentor_id,
                'mentorship_request',
                'New Mentorship Request',
                f"You have a new mentorship request from {mentee['full_name']}",
                f"/mentorship/requests/{result}"
            )
        return result
    
    def get_mentorship_requests(self, user_id, role, status=None):
        """Get mentorship requests for a user as mentor or mentee with explicit role support."""
        normalized_role = (role or '').strip().lower()
        mentor_aliases = {'mentor', 'teacher', 'as_mentor'}
        mentee_aliases = {'mentee', 'junior_student', 'student', 'as_mentee'}

        if normalized_role in mentor_aliases:
            join_user_column = 'r.mentee_id'
            where_column = 'r.mentor_id'
            my_side = 'mentor'
        elif normalized_role in mentee_aliases:
            join_user_column = 'r.mentor_id'
            where_column = 'r.mentee_id'
            my_side = 'mentee'
        else:
            user = self.get_user_by_id(user_id)
            user_role = (user or {}).get('role', '')
            if user_role == 'teacher':
                join_user_column = 'r.mentee_id'
                where_column = 'r.mentor_id'
                my_side = 'mentor'
            else:
                join_user_column = 'r.mentor_id'
                where_column = 'r.mentee_id'
                my_side = 'mentee'

        query = f"""
            SELECT r.*, 
                   u.full_name as other_name, 
                   u.username as other_username,
                   u.profile_pic as other_pic,
                   u.department as other_dept,
                   u.major as other_major,
                   u.role as other_role,
                   '{my_side}' as my_side
            FROM mentorship_requests r
            JOIN users u ON {join_user_column} = u.user_id
            WHERE {where_column} = %s
        """
        params = [user_id]

        if status:
            query += " AND r.status = %s"
            params.append(status)

        query += " ORDER BY r.created_at DESC"
        return self.execute_query(query, params) or []

    def get_mentorship_request_by_id(self, request_id):
        """Get mentorship request by ID with related user names when available."""
        query = """
            SELECT r.*, 
                   mentor.full_name AS mentor_name,
                   mentee.full_name AS mentee_name
            FROM mentorship_requests r
            LEFT JOIN users mentor ON mentor.user_id = r.mentor_id
            LEFT JOIN users mentee ON mentee.user_id = r.mentee_id
            WHERE r.request_id = %s
            LIMIT 1
        """
        result = self.execute_query(query, (request_id,))
        return result[0] if result else None

    def get_relationship_request(self, user_id, other_user_id):
        """Return the latest mentorship request between two users with joined names."""
        query = """
            SELECT r.*,
                   mentor.full_name AS mentor_name,
                   mentee.full_name AS mentee_name,
                   CASE
                       WHEN r.mentor_id = %s THEN mentee.full_name
                       ELSE mentor.full_name
                   END AS other_name,
                   CASE
                       WHEN r.mentor_id = %s THEN 'mentor'
                       ELSE 'mentee'
                   END AS my_side
            FROM mentorship_requests r
            JOIN users mentor ON mentor.user_id = r.mentor_id
            JOIN users mentee ON mentee.user_id = r.mentee_id
            WHERE (r.mentor_id = %s AND r.mentee_id = %s)
               OR (r.mentor_id = %s AND r.mentee_id = %s)
            ORDER BY r.created_at DESC
            LIMIT 1
        """
        rows = self.execute_query(query, (user_id, user_id, user_id, other_user_id, other_user_id, user_id))
        return rows[0] if rows else None

    def get_mentorship_summary(self, user_id):
        """Get mentorship summary counts for dashboard and mentorship header cards."""
        summary = {
            'incoming_pending': 0,
            'outgoing_pending': 0,
            'my_mentees': 0,
            'my_mentors': 0,
            'completed_as_mentor': 0,
            'completed_as_mentee': 0,
            'active_chats': 0,
        }
        rows = self.execute_query(
            """
            SELECT
                SUM(CASE WHEN mentor_id = %s AND status = 'pending' THEN 1 ELSE 0 END) AS incoming_pending,
                SUM(CASE WHEN mentee_id = %s AND status = 'pending' THEN 1 ELSE 0 END) AS outgoing_pending,
                SUM(CASE WHEN mentor_id = %s AND status = 'accepted' THEN 1 ELSE 0 END) AS my_mentees,
                SUM(CASE WHEN mentee_id = %s AND status = 'accepted' THEN 1 ELSE 0 END) AS my_mentors,
                SUM(CASE WHEN mentor_id = %s AND status = 'completed' THEN 1 ELSE 0 END) AS completed_as_mentor,
                SUM(CASE WHEN mentee_id = %s AND status = 'completed' THEN 1 ELSE 0 END) AS completed_as_mentee
            FROM mentorship_requests
            WHERE mentor_id = %s OR mentee_id = %s
            """,
            (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id)
        ) or [summary]
        row = rows[0]
        for key in ('incoming_pending', 'outgoing_pending', 'my_mentees', 'my_mentors', 'completed_as_mentor', 'completed_as_mentee'):
            summary[key] = int(row.get(key, 0) or 0)

        chat_rows = self.execute_query(
            """
            SELECT COUNT(*) AS count
            FROM mentorship_requests
            WHERE (mentor_id = %s OR mentee_id = %s)
              AND status IN ('accepted', 'completed')
            """,
            (user_id, user_id)
        ) or [{'count': 0}]
        summary['active_chats'] = int(chat_rows[0].get('count', 0) or 0)
        return summary

    def get_unread_message_counts_by_request(self, user_id):
        """Return unread message counts grouped by request."""
        rows = self.execute_query(
            """
            SELECT m.request_id, COUNT(*) AS unread_count
            FROM messages m
            JOIN mentorship_requests r ON r.request_id = m.request_id
            WHERE (r.mentor_id = %s OR r.mentee_id = %s)
              AND m.sender_id != %s
              AND m.is_read = FALSE
              AND m.is_deleted = FALSE
            GROUP BY m.request_id
            """,
            (user_id, user_id, user_id)
        ) or []
        return {row['request_id']: int(row.get('unread_count', 0) or 0) for row in rows}
    
    def update_request_status(self, request_id, status,user_id=None, reason=None):
        """Update mentorship request status"""
        query = """
            UPDATE mentorship_requests 
            SET status = %s, 
                rejection_reason = %s,
                accepted_at = CASE WHEN %s = 'accepted' THEN NOW() ELSE accepted_at END,
                completed_at = CASE WHEN %s = 'completed' THEN NOW() ELSE completed_at END
            WHERE request_id = %s
        """
        result = self.execute_query(query, (status, reason, status, status, request_id), dictionary=False)
        
        if result != -1 and result > 0:
            request = self.get_mentorship_request_by_id(request_id)
            if request:
                # Notify the other party
                if status == 'accepted':
                    notify_user = request['mentee_id'] if request['mentor_id'] == user_id else request['mentor_id']
                    self.create_notification(
                        notify_user,
                        'mentorship_accepted',
                        'Mentorship Request Accepted',
                        'Your mentorship request has been accepted!',
                        f"/mentorship/chat/{request_id}"
                    )
        
        return result != -1
    
    def rate_mentorship(self, request_id, rating, review, is_mentor_rating):
        """Rate mentorship experience after completion and only once per side."""
        if rating < 1 or rating > 5:
            return False

        request = self.get_mentorship_request_by_id(request_id)
        if not request or request.get('status') != 'completed':
            return False

        if is_mentor_rating:
            if request.get('mentor_rating') is not None or (request.get('mentor_review') or '').strip():
                return False
            query = "UPDATE mentorship_requests SET mentor_rating = %s, mentor_review = %s WHERE request_id = %s"
        else:
            if request.get('mentee_rating') is not None or (request.get('mentee_review') or '').strip():
                return False
            query = "UPDATE mentorship_requests SET mentee_rating = %s, mentee_review = %s WHERE request_id = %s"

        result = self.execute_query(query, (rating, review, request_id), dictionary=False)
        return result and result > 0
    
    # ==================== MESSAGES METHODS ====================
    
    def get_conversation_list(self, user_id, search=None):
        """Return live conversation summaries with latest message and unread counts."""
        query = """
            SELECT
                r.request_id,
                r.subject,
                r.status,
                r.created_at,
                CASE
                    WHEN r.mentor_id = %s THEN mentee.user_id
                    ELSE mentor.user_id
                END AS other_user_id,
                CASE
                    WHEN r.mentor_id = %s THEN mentee.full_name
                    ELSE mentor.full_name
                END AS other_name,
                CASE
                    WHEN r.mentor_id = %s THEN mentee.username
                    ELSE mentor.username
                END AS other_username,
                CASE
                    WHEN r.mentor_id = %s THEN mentee.profile_pic
                    ELSE mentor.profile_pic
                END AS other_pic,
                latest.message AS last_message,
                latest.created_at AS last_message_time,
                latest.sender_id AS last_message_sender_id,
                COALESCE(unread.unread_count, 0) AS unread_count
            FROM mentorship_requests r
            JOIN users mentor ON mentor.user_id = r.mentor_id
            JOIN users mentee ON mentee.user_id = r.mentee_id
            LEFT JOIN messages latest ON latest.message_id = (
                SELECT m2.message_id
                FROM messages m2
                WHERE m2.request_id = r.request_id AND m2.is_deleted = FALSE
                ORDER BY m2.created_at DESC, m2.message_id DESC
                LIMIT 1
            )
            LEFT JOIN (
                SELECT m.request_id, COUNT(*) AS unread_count
                FROM messages m
                JOIN mentorship_requests r2 ON r2.request_id = m.request_id
                WHERE (r2.mentor_id = %s OR r2.mentee_id = %s)
                  AND m.sender_id != %s
                  AND m.is_read = FALSE
                  AND m.is_deleted = FALSE
                GROUP BY m.request_id
            ) unread ON unread.request_id = r.request_id
            WHERE (r.mentor_id = %s OR r.mentee_id = %s)
        """
        params = [user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id]

        if search and str(search).strip():
            like = f"%{str(search).strip()}%"
            query += " AND (r.subject LIKE %s OR mentor.full_name LIKE %s OR mentee.full_name LIKE %s OR latest.message LIKE %s)"
            params.extend([like, like, like, like])

        query += " ORDER BY COALESCE(latest.created_at, r.created_at) DESC, r.request_id DESC"
        return self.execute_query(query, params) or []

    def send_message(self, request_id, sender_id, message, msg_type='text', file_url=None):
        """Send message in mentorship chat only for allowed participants."""
        message = (message or '').strip()
        if not message:
            return -1

        request = self.get_mentorship_request_by_id(request_id)
        if not request:
            return -1
        if sender_id not in (request.get('mentor_id'), request.get('mentee_id')):
            return -1
        if request.get('status') not in ('accepted', 'completed'):
            return -1

        query = """
            INSERT INTO messages (request_id, sender_id, message, message_type, file_url)
            VALUES (%s, %s, %s, %s, %s)
        """
        result = self.execute_query(query, (request_id, sender_id, message, msg_type, file_url), dictionary=False)

        if result != -1:
            self.log_activity(sender_id, 'message_sent', f"Message in request {request_id}")
            recipient_id = request['mentee_id'] if request['mentor_id'] == sender_id else request['mentor_id']
            self.create_notification(
                recipient_id,
                'message',
                'New Message',
                f"You have a new message in your mentorship chat",
                f"/mentorship/chat/{request_id}"
            )

        return result
    
    def get_messages(self, request_id, limit=200):
        """Get messages for a mentorship request in chronological order."""
        query = """
            SELECT m.*, m.created_at AS sent_at, u.full_name as sender_name, u.profile_pic as sender_pic
            FROM messages m
            JOIN users u ON m.sender_id = u.user_id
            WHERE m.request_id = %s AND m.is_deleted = FALSE
            ORDER BY m.created_at ASC, m.message_id ASC
            LIMIT %s
        """
        return self.execute_query(query, (request_id, limit)) or []
    
    def mark_messages_as_read(self, request_id, user_id):
        """Mark messages as read"""
        query = """
            UPDATE messages 
            SET is_read = TRUE, read_at = NOW()
            WHERE request_id = %s AND sender_id != %s AND is_read = FALSE
        """
        result = self.execute_query(query, (request_id, user_id), dictionary=False)
        return result != -1
    
    def get_unread_message_count(self, user_id):
        """Get count of unread messages"""
        query = """
            SELECT COUNT(*) as count
            FROM messages m
            JOIN mentorship_requests r ON m.request_id = r.request_id
            WHERE (r.mentor_id = %s OR r.mentee_id = %s)
            AND m.sender_id != %s
            AND m.is_read = FALSE
        """
        result = self.execute_query(query, (user_id, user_id, user_id))
        return result[0]['count'] if result else 0
    
    # ==================== MENTORSHIP SESSIONS METHODS ====================
    
    def create_session(self, request_id, session_date, duration=None, agenda=None):
        """Schedule a mentorship session with basic validation."""
        request = self.get_mentorship_request_by_id(request_id)
        if not request or request.get('status') != 'accepted':
            return -1

        if not isinstance(session_date, datetime):
            return -1
        if session_date < datetime.now() - timedelta(minutes=1):
            return -1
        if duration is not None and int(duration) <= 0:
            return -1

        query = """
            INSERT INTO mentorship_sessions (request_id, session_date, duration_minutes, agenda)
            VALUES (%s, %s, %s, %s)
        """
        result = self.execute_query(query, (request_id, session_date, duration, agenda), dictionary=False)

        if result != -1:
            self.create_notification(
                request['mentor_id'],
                'session_scheduled',
                'Session Scheduled',
                'A mentorship session has been scheduled',
                f"/mentorship/sessions/{result}"
            )
            self.create_notification(
                request['mentee_id'],
                'session_scheduled',
                'Session Scheduled',
                'A mentorship session has been scheduled',
                f"/mentorship/sessions/{result}"
            )

        return result
    
    def get_sessions(self, request_id):
        """Get sessions for a mentorship request"""
        query = "SELECT * FROM mentorship_sessions WHERE request_id = %s ORDER BY session_date DESC"
        return self.execute_query(query, (request_id,))
    
    def update_session_status(self, session_id, status, attendance_mentor=None, attendance_mentee=None):
        """Update session status and attendance"""
        query = "UPDATE mentorship_sessions SET status = %s"
        params = [status]
        
        if attendance_mentor is not None:
            query += ", attendance_mentor = %s"
            params.append(attendance_mentor)
        if attendance_mentee is not None:
            query += ", attendance_mentee = %s"
            params.append(attendance_mentee)
        
        query += " WHERE session_id = %s"
        params.append(session_id)
        
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    # ==================== MENTORSHIP GOALS METHODS ====================
    
    def create_goal(self, request_id, goal_text, target_date=None):
        """Create mentorship goal"""
        query = """
            INSERT INTO mentorship_goals (request_id, goal_text, target_date)
            VALUES (%s, %s, %s)
        """
        result = self.execute_query(query, (request_id, goal_text, target_date), dictionary=False)
        return result
    
    def get_goals(self, request_id):
        """Get goals for a mentorship request"""
        query = "SELECT * FROM mentorship_goals WHERE request_id = %s ORDER BY target_date"
        return self.execute_query(query, (request_id,))
    
    def update_goal_progress(self, goal_id, progress, status=None):
        """Update goal progress"""
        query = "UPDATE mentorship_goals SET progress = %s"
        params = [progress]
        
        if status:
            query += ", status = %s"
            params.append(status)
        
        if progress >= 100:
            query += ", status = 'achieved', achieved_at = NOW()"
        
        query += " WHERE goal_id = %s"
        params.append(goal_id)
        
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    # ==================== EVENTS METHODS ====================
    
    def get_events(self, filters=None):
        """Get events with optional filters and participant-aware metadata."""
        query = """
            SELECT e.*, u.full_name as organizer_name,
                   (SELECT COUNT(*) FROM event_participants ep WHERE ep.event_id = e.event_id AND ep.status IN ('registered', 'attended')) as registered_count
            FROM events e
            JOIN users u ON e.organizer_id = u.user_id
            WHERE 1=1
        """
        params = []

        filters = filters or {}
        include_all_statuses = bool(filters.get('include_all_statuses'))
        search = (filters.get('search') or '').strip()
        participant_user_id = filters.get('participant_user_id')

        if not include_all_statuses:
            query += " AND e.status IN ('upcoming', 'ongoing')"
        if filters.get('organizer_id'):
            query += " AND e.organizer_id = %s"
            params.append(filters['organizer_id'])
        if filters.get('event_type'):
            query += " AND e.event_type = %s"
            params.append(filters['event_type'])
        if filters.get('mode'):
            query += " AND e.mode = %s"
            params.append(filters['mode'])
        if filters.get('start_date'):
            query += " AND e.start_date >= %s"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND e.start_date <= %s"
            params.append(filters['end_date'])
        if participant_user_id:
            query += " AND EXISTS (SELECT 1 FROM event_participants ep WHERE ep.event_id = e.event_id AND ep.user_id = %s AND ep.status != 'cancelled')"
            params.append(participant_user_id)
        if search:
            like = f"%{search}%"
            query += " AND (e.title LIKE %s OR e.description LIKE %s OR u.full_name LIKE %s OR COALESCE(e.location, '') LIKE %s OR COALESCE(e.platform, '') LIKE %s)"
            params.extend([like, like, like, like, like])

        query += " ORDER BY e.start_date ASC, e.start_time ASC, e.event_id DESC"
        return self.execute_query(query, params) or []

    def get_event_by_id(self, event_id):
        """Get event by ID"""
        query = """
            SELECT e.*, u.full_name as organizer_name,
                   (SELECT COUNT(*) FROM event_participants WHERE event_id = e.event_id AND status = 'registered') as registered_count
            FROM events e
            JOIN users u ON e.organizer_id = u.user_id
            WHERE e.event_id = %s
        """
        result = self.execute_query(query, (event_id,))
        return result[0] if result else None
    

    def get_event_registration_status(self, event_id, user_id):
        """Return the current participant row for a user on an event, if any."""
        query = """
            SELECT event_id, user_id, status, registered_at, feedback_rating, feedback_comment,
                   certificate_generated, certificate_url, check_in_time
            FROM event_participants
            WHERE event_id = %s AND user_id = %s
            LIMIT 1
        """
        result = self.execute_query(query, (event_id, user_id))
        return result[0] if result else None

    def get_event_participants(self, event_id, statuses=None):
        """Return event participants with user details."""
        query = """
            SELECT ep.*, u.full_name, u.username, u.role, u.department, u.major
            FROM event_participants ep
            JOIN users u ON ep.user_id = u.user_id
            WHERE ep.event_id = %s
        """
        params = [event_id]
        if statuses:
            placeholders = ', '.join(['%s'] * len(statuses))
            query += f" AND ep.status IN ({placeholders})"
            params.extend(statuses)
        query += " ORDER BY ep.registered_at DESC"
        return self.execute_query(query, params) or []

    def create_event(self, event_data):
        """Create new event"""
        query = """
            INSERT INTO events (
                title, description, event_type, mode, organizer_id,
                start_date, start_time, end_date, end_time,
                max_participants, location, platform, prerequisites,
                target_audience, registration_deadline, price, is_paid,
                tags, agenda, banner_image
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        params = (
            event_data['title'],
            event_data['description'],
            event_data['event_type'],
            event_data.get('mode', 'online'),
            event_data['organizer_id'],
            event_data['start_date'],
            event_data['start_time'],
            event_data.get('end_date'),
            event_data.get('end_time'),
            event_data.get('max_participants', 0),
            event_data.get('location'),
            event_data.get('platform'),
            event_data.get('prerequisites'),
            event_data.get('target_audience'),
            event_data.get('registration_deadline'),
            event_data.get('price', 0),
            event_data.get('is_paid', False),
            json.dumps(event_data.get('tags', [])),
            json.dumps(event_data.get('agenda', {})),
            event_data.get('banner_image')
        )
        result = self.execute_query(query, params, dictionary=False)
        
        if result != -1:
            self.log_activity(event_data['organizer_id'], 'event_created', f"Created event: {event_data['title']}")
        
        return result
    
    def update_event(self, event_id, event_data):
        """Update event"""
        query = """
            UPDATE events SET
                title = %s,
                description = %s,
                event_type = %s,
                mode = %s,
                start_date = %s,
                start_time = %s,
                end_date = %s,
                end_time = %s,
                max_participants = %s,
                location = %s,
                platform = %s,
                prerequisites = %s,
                target_audience = %s,
                registration_deadline = %s,
                price = %s,
                is_paid = %s,
                tags = %s,
                agenda = %s,
                banner_image = %s,
                status = %s
            WHERE event_id = %s
        """
        params = (
            event_data['title'],
            event_data['description'],
            event_data['event_type'],
            event_data.get('mode', 'online'),
            event_data['start_date'],
            event_data['start_time'],
            event_data.get('end_date'),
            event_data.get('end_time'),
            event_data.get('max_participants', 0),
            event_data.get('location'),
            event_data.get('platform'),
            event_data.get('prerequisites'),
            event_data.get('target_audience'),
            event_data.get('registration_deadline'),
            event_data.get('price', 0),
            event_data.get('is_paid', False),
            json.dumps(event_data.get('tags', [])),
            json.dumps(event_data.get('agenda', {})),
            event_data.get('banner_image'),
            event_data.get('status', 'upcoming'),
            event_id
        )
        result = self.execute_query(query, params, dictionary=False)
        return result != -1
    
    def register_for_event(self, event_id, user_id):
        """Register user for event with capacity, deadline, and re-registration checks."""
        event = self.get_event_by_id(event_id)
        if not event:
            return False, "Event not found"

        if event.get('status') != 'upcoming':
            return False, "This event is no longer open for registration"

        today = datetime.now().date()
        event_date = event.get('start_date')
        if hasattr(event_date, 'date'):
            event_date = event_date.date()
        if event_date and event_date < today:
            return False, "This event has already started or ended"

        deadline = event.get('registration_deadline')
        if hasattr(deadline, 'date'):
            deadline = deadline.date()
        if deadline and deadline < today:
            return False, "Registration deadline has passed"

        check_query = "SELECT * FROM event_participants WHERE event_id = %s AND user_id = %s"
        existing = self.execute_query(check_query, (event_id, user_id))
        if existing:
            current = existing[0]
            status = current.get('status')
            if status == 'cancelled':
                restore_query = """
                    UPDATE event_participants
                    SET status = 'registered', registered_at = NOW()
                    WHERE event_id = %s AND user_id = %s
                """
                restored = self.execute_query(restore_query, (event_id, user_id), dictionary=False)
                if restored != -1:
                    self.log_activity(user_id, 'event_joined', f"Re-registered for event {event_id}")
                    return True, "Successfully registered"
                return False, "Registration failed"
            return False, "Already registered"

        if event.get('max_participants', 0) > 0 and event.get('registered_count', 0) >= event['max_participants']:
            return False, "Event is full"

        query = """
            INSERT INTO event_participants (event_id, user_id)
            VALUES (%s, %s)
        """
        result = self.execute_query(query, (event_id, user_id), dictionary=False)

        if result != -1:
            self.log_activity(user_id, 'event_joined', f"Joined event {event_id}")
            return True, "Successfully registered"

        return False, "Registration failed"
    
    def cancel_event_registration(self, event_id, user_id):
        """Cancel event registration when the event has not started yet."""
        event = self.get_event_by_id(event_id)
        if not event:
            return False
        event_date = event.get('start_date')
        if hasattr(event_date, 'date'):
            event_date = event_date.date()
        if event_date and event_date < datetime.now().date():
            return False
        query = "UPDATE event_participants SET status = 'cancelled' WHERE event_id = %s AND user_id = %s AND status != 'cancelled'"
        result = self.execute_query(query, (event_id, user_id), dictionary=False)
        return bool(result and result > 0)
    
    def get_user_events(self, user_id):
        """Get events a user has registered for with organizer metadata."""
        query = """
            SELECT e.*, u.full_name as organizer_name,
                   ep.status as registration_status, ep.registered_at,
                   ep.feedback_rating, ep.feedback_comment,
                   (ep.feedback_rating IS NOT NULL OR NULLIF(TRIM(COALESCE(ep.feedback_comment, '')), '') IS NOT NULL) AS feedback_submitted,
                   ep.certificate_generated, ep.certificate_generated AS certificate_ready, ep.certificate_url, ep.check_in_time,
                   (SELECT COUNT(*) FROM event_participants ep2 WHERE ep2.event_id = e.event_id AND ep2.status IN ('registered', 'attended')) as registered_count
            FROM events e
            JOIN users u ON e.organizer_id = u.user_id
            JOIN event_participants ep ON e.event_id = ep.event_id
            WHERE ep.user_id = %s AND ep.status != 'cancelled'
            ORDER BY e.start_date ASC, e.start_time ASC
        """
        return self.execute_query(query, (user_id,)) or []

    def get_event_dashboard_payload(self, user_id):
        """Return created and registered events for event pages and dashboards."""
        return {
            'created_events': self.get_user_created_events(user_id, include_past=True),
            'registered_events': self.get_user_events(user_id),
        }

    def check_in_event(self, event_id, user_id, method='manual'):
        """Check in user to event"""
        query = """
            UPDATE event_participants 
            SET status = 'attended', check_in_time = NOW(), check_in_method = %s
            WHERE event_id = %s AND user_id = %s
        """
        result = self.execute_query(query, (method, event_id, user_id), dictionary=False)
        return result != -1
    
    def submit_event_feedback(self, event_id, user_id, rating, comment):
        """Submit event feedback only for attended or past events and prevent blank no-op saves."""
        if rating < 1 or rating > 5:
            return False
        if not (comment or '').strip():
            return False

        participant_query = """
            SELECT ep.status, ep.feedback_rating, ep.feedback_comment, e.start_date
            FROM event_participants ep
            JOIN events e ON e.event_id = ep.event_id
            WHERE ep.event_id = %s AND ep.user_id = %s
            LIMIT 1
        """
        participant = self.execute_query(participant_query, (event_id, user_id))
        if not participant:
            return False

        record = participant[0]
        event_date = record.get('start_date')
        if hasattr(event_date, 'date'):
            event_date = event_date.date()
        can_review = record.get('status') == 'attended' or (event_date and event_date < datetime.now().date())
        if not can_review:
            return False

        query = """
            UPDATE event_participants 
            SET feedback_rating = %s, feedback_comment = %s
            WHERE event_id = %s AND user_id = %s
        """
        result = self.execute_query(query, (rating, comment.strip(), event_id, user_id), dictionary=False)
        return bool(result and result > 0)

    def mark_event_certificate_ready(self, event_id, user_id, certificate_url=None):
        """Mark certificate as available only after attendance is recorded."""
        participant = self.execute_query(
            "SELECT status, certificate_generated FROM event_participants WHERE event_id = %s AND user_id = %s LIMIT 1",
            (event_id, user_id)
        )
        if not participant:
            return False
        record = participant[0]
        if record.get('status') != 'attended' or record.get('certificate_generated'):
            return False

        query = """
            UPDATE event_participants
            SET certificate_generated = TRUE, certificate_url = %s
            WHERE event_id = %s AND user_id = %s
        """
        result = self.execute_query(query, (certificate_url, event_id, user_id), dictionary=False)
        return bool(result and result > 0)
    
    # ==================== ANNOUNCEMENTS METHODS ====================
    
    def get_announcements(self, user_role=None, user_department=None, user_year=None):
        """Get announcements for user"""
        query = """
            SELECT a.*, u.full_name as announcer_name, u.role as announcer_role
            FROM announcements a
            JOIN users u ON a.announcer_id = u.user_id
            WHERE a.status = 'published'
        """
        params = []

        if user_role:
            query += " AND (a.target_roles IS NULL OR JSON_CONTAINS(a.target_roles, %s))"
            params.append(json.dumps(user_role))
        if user_department:
            query += " AND (a.target_departments IS NULL OR JSON_CONTAINS(a.target_departments, %s))"
            params.append(json.dumps(user_department))
        if user_year is not None:
            query += " AND (a.target_years IS NULL OR JSON_CONTAINS(a.target_years, %s))"
            params.append(json.dumps(user_year))

        query += " ORDER BY a.is_pinned DESC, a.priority DESC, a.published_at DESC"
        return self.execute_query(query, params)

    def get_announcement_by_id(self, announcement_id):
        """Get announcement by ID"""
        query = """
            SELECT a.*, u.full_name as announcer_name
            FROM announcements a
            JOIN users u ON a.announcer_id = u.user_id
            WHERE a.announcement_id = %s
        """
        result = self.execute_query(query, (announcement_id,))
        return result[0] if result else None
    
    def create_announcement(self, announcement_data):
        """Create new announcement"""
        query = """
            INSERT INTO announcements (
                title, content, announcer_id, event_id, category,
                priority, target_roles, target_departments, target_years,
                attachments, link_url, is_pinned, allow_comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            announcement_data['title'],
            announcement_data['content'],
            announcement_data['announcer_id'],
            announcement_data.get('event_id'),
            announcement_data.get('category', 'general'),
            announcement_data.get('priority', 'medium'),
            json.dumps(announcement_data.get('target_roles', [])),
            json.dumps(announcement_data.get('target_departments', [])),
            json.dumps(announcement_data.get('target_years', [])),
            json.dumps(announcement_data.get('attachments', [])),
            announcement_data.get('link_url'),
            announcement_data.get('is_pinned', False),
            announcement_data.get('allow_comments', True)
        )
        result = self.execute_query(query, params, dictionary=False)
        
        if result != -1:
            self.log_activity(announcement_data['announcer_id'], 'announcement_created', f"Created announcement: {announcement_data['title']}")
        
        return result
    
    def increment_announcement_view(self, announcement_id):
        """Increment announcement view count"""
        query = "UPDATE announcements SET views = views + 1 WHERE announcement_id = %s"
        self.execute_query(query, (announcement_id,), dictionary=False)
    
    def add_announcement_comment(self, announcement_id, user_id, comment, parent_id=None):
        """Add comment to announcement"""
        query = """
            INSERT INTO announcement_comments (announcement_id, user_id, comment, parent_id)
            VALUES (%s, %s, %s, %s)
        """
        result = self.execute_query(query, (announcement_id, user_id, comment, parent_id), dictionary=False)
        
        if result != -1:
            announcement = self.get_announcement_by_id(announcement_id)
            if announcement and announcement['announcer_id'] != user_id:
                self.create_notification(
                    announcement['announcer_id'],
                    'comment',
                    'New Comment',
                    f"Someone commented on your announcement: {announcement['title']}",
                    f"/announcements/{announcement_id}"
                )
        
        return result
    
    def get_announcement_comments(self, announcement_id):
        """Get comments for announcement"""
        query = """
            SELECT c.*, u.full_name as user_name, u.profile_pic as user_pic
            FROM announcement_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.announcement_id = %s AND c.is_deleted = FALSE
            ORDER BY c.created_at ASC
        """
        return self.execute_query(query, (announcement_id,))
    
    # ==================== NOTIFICATIONS METHODS ====================
    
    def create_notification(self, user_id, notif_type, title, content, link=None, priority='medium'):
        """Create notification for user"""
        query = """
            INSERT INTO notifications (user_id, type, title, content, link, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, notif_type, title, content, link, priority), dictionary=False)
    
    def get_user_notifications(self, user_id, limit=20, unread_only=False):
        """Get user notifications"""
        query = """
            SELECT * FROM notifications
            WHERE user_id = %s
        """
        params = [user_id]
        
        if unread_only:
            query += " AND is_read = FALSE"
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        return self.execute_query(query, params)
    
    def mark_notification_as_read(self, notification_id):
        """Mark notification as read"""
        query = "UPDATE notifications SET is_read = TRUE, read_at = NOW() WHERE notification_id = %s"
        result = self.execute_query(query, (notification_id,), dictionary=False)
        return result != -1
    
    def mark_all_notifications_as_read(self, user_id):
        """Mark all user notifications as read"""
        query = "UPDATE notifications SET is_read = TRUE, read_at = NOW() WHERE user_id = %s AND is_read = FALSE"
        result = self.execute_query(query, (user_id,), dictionary=False)
        return result != -1
    
    def get_unread_notification_count(self, user_id):
        """Get count of unread notifications"""
        query = "SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE"
        result = self.execute_query(query, (user_id,))
        return result[0]['count'] if result else 0
    
    # ==================== ACTIVITY METHODS ====================
    
    def log_activity(self, user_id, activity_type, activity_data, ip_address=None, user_agent=None):
        """Log user activity"""
        query = """
            INSERT INTO user_activities (user_id, activity_type, activity_data, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
        """
        data_json = json.dumps({'message': activity_data}) if isinstance(activity_data, str) else json.dumps(activity_data)
        self.execute_query(query, (user_id, activity_type, data_json, ip_address, user_agent), dictionary=False)
    
    def get_user_activities(self, user_id, limit=20):
        """Get user activities"""
        query = """
            SELECT * FROM user_activities
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (user_id, limit))
    
    def get_recent_activities(self, limit=50):
        """Get recent activities across platform"""
        query = """
            SELECT a.*, u.full_name as user_name, u.role as user_role
            FROM user_activities a
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.created_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))


    def get_recent_users(self, limit=5):
        """Get recently registered active users for admin dashboard previews."""
        query = """
            SELECT user_id, full_name, username, email, role, department, year, is_active, created_at
            FROM users
            WHERE deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))

    def get_recent_mentorship_requests(self, limit=5, statuses=None):
        """Get recent mentorship requests with both participant names for admin previews."""
        query = """
            SELECT r.*,
                   mentor.full_name AS mentor_name,
                   mentor.role AS mentor_role,
                   mentor.department AS mentor_department,
                   mentee.full_name AS mentee_name,
                   mentee.role AS mentee_role,
                   mentee.department AS mentee_department
            FROM mentorship_requests r
            JOIN users mentor ON r.mentor_id = mentor.user_id
            JOIN users mentee ON r.mentee_id = mentee.user_id
        """
        params = []
        if statuses:
            placeholders = ', '.join(['%s'] * len(statuses))
            query += f" WHERE r.status IN ({placeholders})"
            params.extend(statuses)
        query += " ORDER BY r.created_at DESC LIMIT %s"
        params.append(limit)
        return self.execute_query(query, tuple(params))

    def get_recent_events(self, limit=5, include_cancelled=False):
        """Get recent events with organizer names for admin previews."""
        query = """
            SELECT e.*,
                   u.full_name AS organizer_name,
                   (SELECT COUNT(*) FROM event_participants ep
                    WHERE ep.event_id = e.event_id AND ep.status IN ('registered', 'attended')) AS registered_count
            FROM events e
            JOIN users u ON e.organizer_id = u.user_id
        """
        params = []
        if not include_cancelled:
            query += " WHERE e.status <> 'cancelled'"
        query += " ORDER BY e.created_at DESC LIMIT %s"
        params.append(limit)
        return self.execute_query(query, tuple(params))
    
    # ==================== STATISTICS METHODS ====================
    
    def get_user_stats(self, user_id):
        """Get user statistics."""
        def scalar(query, params):
            rows = self.execute_query(query, params) or [{'count': 0}]
            row = rows[0]
            return row.get('count', 0) or row.get('avg_rating', 0) or 0

        stats = {}
        stats['mentor_count'] = scalar(
            "SELECT COUNT(*) as count FROM mentorship_requests WHERE mentor_id = %s AND status = 'accepted'", (user_id,)
        )
        stats['mentee_count'] = scalar(
            "SELECT COUNT(*) as count FROM mentorship_requests WHERE mentee_id = %s AND status = 'accepted'", (user_id,)
        )
        stats['event_count'] = scalar(
            "SELECT COUNT(*) as count FROM event_participants WHERE user_id = %s AND status IN ('registered','attended')", (user_id,)
        )
        stats['login_count'] = scalar(
            "SELECT COUNT(*) as count FROM user_activities WHERE user_id = %s AND activity_type = 'login'", (user_id,)
        )
        stats['message_count'] = scalar(
            "SELECT COUNT(*) as count FROM messages WHERE sender_id = %s", (user_id,)
        )
        stats['profile_views'] = scalar(
            "SELECT COUNT(*) as count FROM user_activities WHERE user_id = %s AND activity_type = 'profile_view'", (user_id,)
        )
        rating_rows = self.execute_query(
            "SELECT AVG(mentee_rating) as avg_rating FROM mentorship_requests WHERE mentor_id = %s AND mentee_rating IS NOT NULL", (user_id,)
        ) or [{'avg_rating': 0}]
        stats['avg_rating'] = float(rating_rows[0].get('avg_rating') or 0)
        return stats
    
    def get_platform_stats(self):
        """Get overall platform statistics."""
        def scalar(query, params=None):
            rows = self.execute_query(query, params or ()) or [{'count': 0}]
            return rows[0].get('count', 0) or 0

        stats = {}

        # User counts
        stats['total_users'] = scalar("SELECT COUNT(*) as count FROM users")
        stats['teachers'] = scalar("SELECT COUNT(*) as count FROM users WHERE role = 'teacher'")
        stats['senior_students'] = scalar("SELECT COUNT(*) as count FROM users WHERE role = 'senior_student'")
        stats['junior_students'] = scalar("SELECT COUNT(*) as count FROM users WHERE role = 'junior_student'")

        # Mentorship stats
        stats['total_mentorships'] = scalar("SELECT COUNT(*) as count FROM mentorship_requests")
        stats['active_mentorships'] = scalar("SELECT COUNT(*) as count FROM mentorship_requests WHERE status = 'accepted'")
        stats['completed_mentorships'] = scalar("SELECT COUNT(*) as count FROM mentorship_requests WHERE status = 'completed'")
        stats['pending_mentorships'] = scalar("SELECT COUNT(*) as count FROM mentorship_requests WHERE status = 'pending'")

        # Event stats
        stats['total_events'] = scalar("SELECT COUNT(*) as count FROM events")
        stats['upcoming_events'] = scalar(
            "SELECT COUNT(*) as count FROM events WHERE start_date >= CURDATE() AND status = 'upcoming'"
        )
        stats['completed_events'] = scalar(
            "SELECT COUNT(*) as count FROM events WHERE start_date < CURDATE() OR status = 'completed'"
        )

        # Message stats
        stats['total_messages'] = scalar("SELECT COUNT(*) as count FROM messages")

        return stats
    
    # ==================== ACHIEVEMENTS METHODS ====================
    
    def get_all_achievements(self):
        """Get all achievements"""
        query = "SELECT * FROM achievements ORDER BY points ASC"
        return self.execute_query(query)
    
    def get_user_achievements(self, user_id):
        """Get user achievements"""
        query = """
            SELECT a.*, ua.progress, ua.unlocked_at
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.achievement_id = ua.achievement_id AND ua.user_id = %s
            ORDER BY a.points ASC
        """
        return self.execute_query(query, (user_id,))
    
    def check_and_unlock_achievements(self, user_id):
        """Check and unlock achievements for user"""
        achievements = self.get_all_achievements()
        user_stats = self.get_user_stats(user_id)
        
        unlocked = []
        
        for achievement in achievements:
            # Check if already unlocked
            check = self.execute_query(
                "SELECT * FROM user_achievements WHERE user_id = %s AND achievement_id = %s",
                (user_id, achievement['achievement_id'])
            )
            if check:
                continue
            
            criteria = json.loads(achievement['criteria']) if achievement['criteria'] else {}
            progress = 0
            
            # Calculate progress based on criteria
            if 'event_count' in criteria and user_stats['event_count'] >= criteria['event_count']:
                progress = 100
            elif 'mentee_count' in criteria and user_stats['mentee_count'] >= criteria['mentee_count']:
                progress = 100
            elif 'message_count' in criteria and user_stats['message_count'] >= criteria['message_count']:
                progress = 100
            
            if progress >= 100:
                # Unlock achievement
                self.execute_query(
                    "INSERT INTO user_achievements (user_id, achievement_id, progress, unlocked_at) VALUES (%s, %s, 100, NOW())",
                    (user_id, achievement['achievement_id']),
                    dictionary=False
                )
                unlocked.append(achievement['name'])
                
                # Create notification
                self.create_notification(
                    user_id,
                    'achievement',
                    'Achievement Unlocked!',
                    f"You've unlocked the '{achievement['name']}' achievement!",
                    "/profile/achievements"
                )
        
        return unlocked
    
    # ==================== RESOURCES METHODS ====================
    
    def get_resources(self, filters=None):
        """Get learning resources"""
        query = "SELECT * FROM resources WHERE is_approved = TRUE"
        params = []
        
        if filters:
            if filters.get('resource_type'):
                query += " AND resource_type = %s"
                params.append(filters['resource_type'])
            if filters.get('difficulty'):
                query += " AND difficulty = %s"
                params.append(filters['difficulty'])
            if filters.get('skill_id'):
                query += " AND JSON_CONTAINS(skill_ids, %s)"
                params.append(json.dumps(filters['skill_id']))
        
        query += " ORDER BY view_count DESC"
        return self.execute_query(query, params)
    
    def get_resource_by_id(self, resource_id):
        """Get resource by ID"""
        query = "SELECT * FROM resources WHERE resource_id = %s"
        result = self.execute_query(query, (resource_id,))
        if result:
            # Increment view count
            self.execute_query("UPDATE resources SET view_count = view_count + 1 WHERE resource_id = %s", (resource_id,), dictionary=False)
            return result[0]
        return None
    
    def create_resource(self, resource_data):
        """Create new resource"""
        query = """
            INSERT INTO resources (
                title, description, resource_type, url, file_path,
                thumbnail, tags, skill_ids, difficulty, duration_minutes,
                author, source, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            resource_data['title'],
            resource_data['description'],
            resource_data['resource_type'],
            resource_data.get('url'),
            resource_data.get('file_path'),
            resource_data.get('thumbnail'),
            json.dumps(resource_data.get('tags', [])),
            json.dumps(resource_data.get('skill_ids', [])),
            resource_data.get('difficulty', 'beginner'),
            resource_data.get('duration_minutes'),
            resource_data.get('author'),
            resource_data.get('source'),
            resource_data.get('created_by')
        )
        return self.execute_query(query, params, dictionary=False)
    
    def save_resource_for_user(self, user_id, resource_id):
        """Save resource for user"""
        query = """
            INSERT INTO user_resources (user_id, resource_id)
            VALUES (%s, %s)
        """
        result = self.execute_query(query, (user_id, resource_id), dictionary=False)
        return result != -1
    
    def get_user_saved_resources(self, user_id):
        """Get user's saved resources"""
        query = """
            SELECT r.*, ur.status, ur.progress
            FROM resources r
            JOIN user_resources ur ON r.resource_id = ur.resource_id
            WHERE ur.user_id = %s
            ORDER BY ur.created_at DESC
        """
        return self.execute_query(query, (user_id,))
    

    def get_profile_bundle(self, user_id):
        """Return user + related profile collections for profile screens."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        return {
            'user': user,
            'skills': self.get_user_skills(user_id),
            'projects': self.get_user_projects(user_id),
            'certifications': self.get_user_certifications(user_id),
        }

    # ==================== CLOSE CONNECTION ====================
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")