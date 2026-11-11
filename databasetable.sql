DROP DATABASE IF EXISTS mentorship_hub;
CREATE DATABASE mentorship_hub;
USE mentorship_hub;

-- 1. USERS TABLE (Complete with VARCHAR for text fields that need defaults)
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    reset_token VARCHAR(100),
    reset_token_expiry DATETIME,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('teacher', 'senior_student', 'junior_student', 'admin') NOT NULL DEFAULT 'junior_student',
    profile_pic VARCHAR(255) DEFAULT 'default.jpg',
    cover_pic VARCHAR(255) DEFAULT 'default_cover.jpg',
    
    -- Academic Information
    student_id VARCHAR(50) UNIQUE,
    teacher_id VARCHAR(50) UNIQUE,
    department VARCHAR(50),
    major VARCHAR(100),
    year INT,
    semester INT,
    batch VARCHAR(20),
    roll_number VARCHAR(20),
    cgpa DECIMAL(3,2),
    
    -- Personal Information
    date_of_birth DATE,
    phone VARCHAR(20),
    address TEXT,  -- TEXT can stay, doesn't need default
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'Myanmar',
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    
    -- Professional Information
    bio TEXT,  -- TEXT can stay, doesn't need default
    experience_years INT DEFAULT 0,
    current_position VARCHAR(100),
    company VARCHAR(100),
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    website_url VARCHAR(255),
    
    -- Preferences
    preferred_language VARCHAR(50) DEFAULT 'Myanmar',
    communication_preference ENUM('chat', 'video', 'in-person', 'any') DEFAULT 'any',
    availability TEXT,  -- TEXT can stay, doesn't need default
    
    -- Privacy Settings - Changed from TEXT to VARCHAR to allow default
    privacy_settings VARCHAR(500) DEFAULT '{"profile": "public", "email": "private", "phone": "private"}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_online BOOLEAN DEFAULT FALSE,
    last_login DATETIME,
    last_login_ip VARCHAR(45),
    login_attempts INT DEFAULT 0,
    locked_until DATETIME,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. SKILLS TABLE
CREATE TABLE skills (
    skill_id INT PRIMARY KEY AUTO_INCREMENT,
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    category ENUM('programming', 'design', 'soft_skill', 'language', 'other') NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. USER_SKILLS TABLE
CREATE TABLE user_skills (
    user_skill_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('beginner', 'intermediate', 'advanced', 'expert') NOT NULL,
    years_experience INT DEFAULT 0,
    endorsed_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_skill (user_id, skill_id)
);

-- 4. INTERESTS TABLE
CREATE TABLE interests (
    interest_id INT PRIMARY KEY AUTO_INCREMENT,
    interest_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. USER_INTERESTS TABLE
CREATE TABLE user_interests (
    user_interest_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    interest_id INT NOT NULL,
    level INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(interest_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_interest (user_id, interest_id)
);

-- 6. PROJECTS TABLE
CREATE TABLE projects (
    project_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    description TEXT,
    technologies TEXT,
    role VARCHAR(100),
    project_url VARCHAR(255),
    github_url VARCHAR(255),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    achievements TEXT,
    team_size INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 7. PROJECT_SCREENSHOTS TABLE
CREATE TABLE project_screenshots (
    screenshot_id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    caption VARCHAR(255),
    display_order INT DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 8. CERTIFICATIONS TABLE
CREATE TABLE certifications (
    cert_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    cert_name VARCHAR(200) NOT NULL,
    issuing_organization VARCHAR(200) NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE,
    credential_id VARCHAR(100),
    credential_url VARCHAR(255),
    cert_file VARCHAR(255),
    skills_gained TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 9. EXPERIENCE TABLE
CREATE TABLE experiences (
    exp_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    company VARCHAR(200) NOT NULL,
    position VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    technologies TEXT,
    supervisor_name VARCHAR(100),
    supervisor_contact VARCHAR(100),
    cert_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 10. MENTORSHIP_REQUESTS TABLE
CREATE TABLE mentorship_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_id INT NOT NULL,
    mentee_id INT NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    goals TEXT,
    duration_months INT DEFAULT 3,
    preferred_schedule TEXT,
    communication_mode ENUM('chat', 'video', 'in-person', 'any') DEFAULT 'any',
    urgency ENUM('low', 'medium', 'high') DEFAULT 'medium',
    status ENUM('pending', 'accepted', 'rejected', 'completed', 'cancelled', 'expired') DEFAULT 'pending',
    rejection_reason TEXT,
    accepted_at DATETIME,
    completed_at DATETIME,
    mentor_rating DECIMAL(2,1),
    mentee_rating DECIMAL(2,1),
    mentor_review TEXT,
    mentee_review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (mentee_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_mentor_status (mentor_id, status),
    INDEX idx_mentee_status (mentee_id, status)
);

-- 11. MESSAGES TABLE
CREATE TABLE messages (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL,
    sender_id INT NOT NULL,
    message TEXT NOT NULL,
    message_type ENUM('text', 'image', 'file', 'code') DEFAULT 'text',
    file_url VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at DATETIME,
    is_deleted BOOLEAN DEFAULT FALSE,
    reply_to_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES mentorship_requests(request_id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reply_to_id) REFERENCES messages(message_id) ON DELETE SET NULL,
    INDEX idx_request (request_id, created_at)
);

-- 12. MENTORSHIP_SESSIONS TABLE
CREATE TABLE mentorship_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL,
    session_date DATETIME NOT NULL,
    duration_minutes INT,
    agenda TEXT,
    notes TEXT,
    materials TEXT,
    recording_url VARCHAR(255),
    status ENUM('scheduled', 'completed', 'cancelled', 'rescheduled') DEFAULT 'scheduled',
    attendance_mentor BOOLEAN DEFAULT FALSE,
    attendance_mentee BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES mentorship_requests(request_id) ON DELETE CASCADE
);

-- 13. MENTORSHIP_GOALS TABLE
CREATE TABLE mentorship_goals (
    goal_id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL,
    goal_text VARCHAR(500) NOT NULL,
    target_date DATE,
    progress INT DEFAULT 0,
    status ENUM('pending', 'in_progress', 'achieved', 'cancelled') DEFAULT 'pending',
    achieved_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES mentorship_requests(request_id) ON DELETE CASCADE
);

-- 14. EVENTS TABLE
CREATE TABLE events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    event_type ENUM(
        'knowledge_session', 'workshop', 'competition', 'hackathon',
        'seminar', 'webinar', 'panel_discussion', 'networking',
        'career_fair', 'social', 'study_group'
    ) NOT NULL,
    mode ENUM('online', 'offline', 'hybrid') NOT NULL,
    platform VARCHAR(100),
    location VARCHAR(200),
    organizer_id INT NOT NULL,
    speakers TEXT,
    start_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_date DATE,
    end_time TIME,
    duration_hours DECIMAL(4,2),
    max_participants INT DEFAULT 0,
    current_participants INT DEFAULT 0,
    waitlist_count INT DEFAULT 0,
    prerequisites TEXT,
    target_audience VARCHAR(500),
    registration_deadline DATETIME,
    price DECIMAL(10,2) DEFAULT 0.00,
    is_paid BOOLEAN DEFAULT FALSE,
    tags TEXT,
    agenda TEXT,
    resources TEXT,
    banner_image VARCHAR(255),
    status ENUM('upcoming', 'ongoing', 'completed', 'cancelled', 'postponed') DEFAULT 'upcoming',
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_date_status (start_date, status),
    FULLTEXT INDEX idx_search (title, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. EVENT_PARTICIPANTS TABLE
CREATE TABLE event_participants (
    participant_id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    registration_type ENUM('individual', 'group') DEFAULT 'individual',
    group_name VARCHAR(100),
    registration_answers TEXT,
    status ENUM('registered', 'attended', 'absent', 'cancelled', 'waitlisted') DEFAULT 'registered',
    check_in_time DATETIME,
    check_in_method VARCHAR(50),
    feedback_rating DECIMAL(2,1),
    feedback_comment TEXT,
    certificate_generated BOOLEAN DEFAULT FALSE,
    certificate_url VARCHAR(255),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at DATETIME,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_event_user (event_id, user_id),
    INDEX idx_event_status (event_id, status)
);

-- 16. ANNOUNCEMENTS TABLE
CREATE TABLE announcements (
    announcement_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    announcer_id INT NOT NULL,
    event_id INT NULL,
    category ENUM('academic', 'event', 'opportunity', 'general', 'emergency', 'achievement') DEFAULT 'general',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    target_roles TEXT,
    target_departments TEXT,
    target_years TEXT,
    attachments TEXT,
    link_url VARCHAR(255),
    is_pinned BOOLEAN DEFAULT FALSE,
    allow_comments BOOLEAN DEFAULT TRUE,
    views INT DEFAULT 0,
    clicks INT DEFAULT 0,
    expiry_date DATE,
    status ENUM('draft', 'published', 'archived') DEFAULT 'published',
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (announcer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE SET NULL,
    INDEX idx_priority_date (priority, published_at DESC)
);

-- 17. ANNOUNCEMENT_COMMENTS TABLE
CREATE TABLE announcement_comments (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    announcement_id INT NOT NULL,
    user_id INT NOT NULL,
    comment TEXT NOT NULL,
    parent_id INT NULL,
    likes INT DEFAULT 0,
    is_edited BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (announcement_id) REFERENCES announcements(announcement_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES announcement_comments(comment_id) ON DELETE CASCADE
);

-- 18. NOTIFICATIONS TABLE
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM(
        'mentorship_request', 'mentorship_accepted', 'message', 'event_reminder', 
        'announcement', 'achievement', 'feedback', 'system', 'mention'
    ) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    link VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME,
    is_clicked BOOLEAN DEFAULT FALSE,
    image_url VARCHAR(255),
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    expires_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, is_read, created_at DESC)
);

-- 19. USER_ACTIVITIES TABLE
CREATE TABLE user_activities (
    activity_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    activity_type ENUM(
        'login', 'logout', 'profile_view', 'profile_update',
        'mentorship_request_sent', 'mentorship_request_received',
        'mentorship_accepted', 'mentorship_rejected',
        'message_sent', 'message_read',
        'event_created', 'event_joined', 'event_cancelled',
        'announcement_view', 'announcement_created',
        'search_performed', 'resource_viewed',
        'feedback_given', 'certificate_downloaded'
    ) NOT NULL,
    activity_data TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(100),
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_time (user_id, created_at DESC)
);

-- 21. ACHIEVEMENTS TABLE
CREATE TABLE achievements (
    achievement_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(50),
    category ENUM('mentorship', 'event', 'engagement', 'skill', 'special') NOT NULL,
    criteria TEXT,
    points INT DEFAULT 10,
    badge_image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 22. USER_ACHIEVEMENTS TABLE
CREATE TABLE user_achievements (
    user_achievement_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    achievement_id INT NOT NULL,
    progress INT DEFAULT 0,
    unlocked_at DATETIME,
    is_notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(achievement_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_achievement (user_id, achievement_id)
);

-- 23. RESOURCES TABLE
CREATE TABLE resources (
    resource_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    resource_type ENUM('video', 'article', 'book', 'course', 'tool', 'template') NOT NULL,
    url VARCHAR(500),
    file_path VARCHAR(255),
    thumbnail VARCHAR(255),
    tags TEXT,
    skill_ids TEXT,
    difficulty ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    duration_minutes INT,
    author VARCHAR(100),
    source VARCHAR(100),
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    is_approved BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 24. USER_RESOURCES TABLE
CREATE TABLE user_resources (
    user_resource_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    status ENUM('saved', 'in_progress', 'completed') DEFAULT 'saved',
    progress INT DEFAULT 0,
    notes TEXT,
    completed_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_resource (user_id, resource_id)
);

-- 25. SYSTEM_LOGS TABLE
CREATE TABLE system_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    log_type ENUM('info', 'warning', 'error', 'security') NOT NULL,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_data TEXT,
    response_data TEXT,
    duration_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type_time (log_type, created_at DESC),
    INDEX idx_user (user_id)
);

-- =====================================================
-- INSERT SAMPLE DATA
-- =====================================================

-- 1. Insert Skills
INSERT INTO skills (skill_name, category, description) VALUES
('Python', 'programming', 'Python programming language'),
('Java', 'programming', 'Java programming language'),
('JavaScript', 'programming', 'JavaScript for web development'),
('React', 'programming', 'React.js framework'),
('Node.js', 'programming', 'Node.js runtime'),
('MySQL', 'programming', 'MySQL database'),
('Communication', 'soft_skill', 'Verbal and written communication'),
('Leadership', 'soft_skill', 'Team leadership and management'),
('English', 'language', 'English language');

-- 2. Insert Interests
INSERT INTO interests (interest_name, category) VALUES
('Artificial Intelligence', 'technology'),
('Machine Learning', 'technology'),
('Web Development', 'technology'),
('Mobile App Development', 'technology'),
('Cyber Security', 'technology'),
('Data Science', 'technology');

-- 3. Insert Achievements
INSERT INTO achievements (name, description, category, points) VALUES
('First Login', 'Log in to the platform for the first time', 'engagement', 5),
('Profile Complete', 'Complete your profile 100%', 'engagement', 10),
('First Event', 'Join your first event', 'event', 10),
('First Request', 'Send your first mentorship request', 'mentorship', 10),
('Skill Collector', 'Add 5 skills to your profile', 'skill', 15);

-- 4. Insert Users
-- Admin user (password: admin123)
INSERT INTO users (username, password, email, full_name, role, is_active) VALUES
('admin', 'admin123', 'admin@mentorship.edu', 'System Administrator', 'admin', TRUE);

-- Teachers
INSERT INTO users (username, password, email, full_name, role, department, major, bio) VALUES
('dr.smith', 'password123', 'dr.smith@polytechnic.edu', 'Dr. John Smith', 'teacher', 'CS', 'Computer Science', 'Professor of Computer Science with 15 years of software development and mentoring experience.'),
('prof.jones', 'password123', 'prof.jones@polytechnic.edu', 'Prof. Sarah Jones', 'teacher', 'IT', 'Information Technology', 'Head of IT Department. Specializes in Cybersecurity.');

-- Senior Students
INSERT INTO users (username, password, email, full_name, role, department, major, year, bio) VALUES
('alex.chen', 'password123', 'alex.chen@student.edu', 'Alex Chen', 'senior_student', 'CS', 'Computer Science', 4, 'Final year CS student. President of Coding Club. Intern at Google.'),
('lisa.wong', 'password123', 'lisa.wong@student.edu', 'Lisa Wong', 'senior_student', 'CS', 'Computer Science', 4, 'Data and software enthusiast. Research assistant in the university lab.'),
('james.lee', 'password123', 'james.lee@student.edu', 'James Lee', 'senior_student', 'IT', 'Information Technology', 4, 'Cybersecurity specialist. CTF team captain.');

-- Junior Students
INSERT INTO users (username, password, email, full_name, role, department, major, year, bio) VALUES
('kevin.ng', 'password123', 'kevin.ng@student.edu', 'Kevin Ng', 'junior_student', 'CS', 'Computer Science', 2, 'Second year CS student. Learning Python and web development.'),
('nina.singh', 'password123', 'nina.singh@student.edu', 'Nina Singh', 'junior_student', 'IT', 'Information Technology', 1, 'Freshman IT student. Excited to learn programming.');

-- Additional Teachers with different majors
INSERT INTO users (username, password, email, full_name, role, department, major, bio) VALUES
('dr.emily.chen', 'password123', 'emily.chen@polytechnic.edu', 'Dr. Emily Chen', 'teacher', 'SE', 'Software Engineering', 'Senior lecturer in Software Engineering. Focuses on maintainable systems, clean architecture, project planning, and collaborative development practices.'),
('dr.michael.tan', 'password123', 'michael.tan@polytechnic.edu', 'Dr. Michael Tan', 'teacher', 'DS', 'Data Science', 'Data Science educator with strong interest in analytics, visualization, practical machine learning, and student research mentoring.'),
('prof.amara.ko', 'password123', 'amara.ko@polytechnic.edu', 'Prof. Amara Ko', 'teacher', 'CY', 'Cyber Security', 'Professor of Cyber Security who teaches secure systems, ethical awareness, threat prevention, and digital safety best practices.'),
('dr.daniel.owens', 'password123', 'daniel.owens@polytechnic.edu', 'Dr. Daniel Owens', 'teacher', 'IS', 'Information Systems', 'Information Systems specialist experienced in business systems analysis, requirements gathering, process improvement, and practical student project guidance.');

-- 5. Insert sample events
INSERT INTO events (title, description, event_type, mode, organizer_id, start_date, start_time, max_participants, location, platform, target_audience) VALUES
('Python Workshop for Beginners', 'Learn Python from scratch in this hands-on workshop. The session starts with programming basics, then moves into problem-solving, functions, and mini practice tasks. Participants will leave with a simple project, clearer coding habits, and confidence to continue learning independently. The facilitator will also explain how beginners can continue practicing after the workshop and which small exercises are best for building daily confidence.', 'workshop', 'online', 2, DATE_ADD(CURDATE(), INTERVAL 7 DAY), '14:00:00', 50, NULL, 'Zoom Room A', 'junior_student'),
('Web Development Bootcamp', 'An intensive web development session covering HTML structure, responsive CSS, JavaScript fundamentals, and how these pieces work together in a real student project. This event is designed for learners who want practical guidance and hands-on examples. Students will see how simple pages evolve into more complete interfaces through design, layout, and interactive behavior.', 'workshop', 'offline', 3, DATE_ADD(CURDATE(), INTERVAL 10 DAY), '10:00:00', 30, 'Lab 201', NULL, 'all'),
('Software Engineering Seminar', 'A career-focused seminar on software engineering principles, teamwork, project planning, version control, testing, and professional growth. Students will hear practical examples from academic and industry-style projects and learn how to prepare for larger team collaborations. The session also includes tips on handling documentation, deadlines, and communication within project groups.', 'seminar', 'hybrid', 2, DATE_ADD(CURDATE(), INTERVAL 14 DAY), '15:30:00', 100, 'Auditorium A', 'Google Meet Link will be shared', 'all'),
('Data Science Study Circle', 'This study circle introduces data cleaning, visualization, and entry-level machine learning thinking. It is a discussion-friendly session where students can ask questions about datasets, tools, and the learning path for data-related careers. Participants are encouraged to bring curiosity, small ideas, and questions they want to explore with peers and mentors.', 'study_group', 'offline', 4, DATE_ADD(CURDATE(), INTERVAL 16 DAY), '13:30:00', 40, 'Innovation Room 3', NULL, 'junior_student'),
('Career Readiness for Tech Students', 'A focused session on resume writing, interview preparation, portfolio building, internship readiness, and how to present project work effectively. Students will receive practical advice that can directly support future job or internship applications. Example resumes, project summaries, and preparation strategies will be discussed in a student-friendly way.', 'seminar', 'offline', 2, DATE_ADD(CURDATE(), INTERVAL 18 DAY), '11:00:00', 80, 'Conference Hall', NULL, 'all'),
('Cyber Security Awareness Forum', 'An awareness forum discussing digital safety, account security, phishing, privacy, and safe online practices for university members. The content is accessible to beginners while still useful for students interested in deeper cyber security topics. The event also covers practical habits that members can apply immediately to protect their personal and academic accounts.', 'seminar', 'hybrid', 3, DATE_ADD(CURDATE(), INTERVAL 20 DAY), '09:30:00', 120, 'IT Hall', 'Teams Meeting Link', 'all'),
('Senior-to-Junior Mentorship Mixer', 'A networking event where junior students can meet senior students, ask questions, and discover possible mentorship matches. The format is friendly, structured, and intended to help first-time members feel comfortable joining the platform community. Members will rotate through short conversations and leave with a clearer idea of who they may want to connect with later.', 'networking', 'offline', 4, DATE_ADD(CURDATE(), INTERVAL 24 DAY), '16:00:00', 60, 'Student Center', NULL, 'junior_student'),
('UI and Product Design Clinic', 'This clinic explores user experience, interface structure, color usage, layout consistency, and practical ways to improve the look and clarity of student applications. Participants can bring ideas or existing screens and receive constructive guidance. The session is especially useful for teams that want more polished project presentations and stronger design thinking.', 'workshop', 'online', 5, DATE_ADD(CURDATE(), INTERVAL 26 DAY), '15:00:00', 45, NULL, 'Zoom Design Studio', 'all'),
('Tech Seminar: Building Real Projects', 'A modern seminar on how to turn classroom knowledge into complete working systems using planning, database design, interfaces, and iterative improvement. This session is especially useful for students preparing major assignments or capstone-style work. Real examples will be used to show how ideas are refined into reliable, presentable applications.', 'seminar', 'hybrid', 2, DATE_ADD(CURDATE(), INTERVAL 28 DAY), '14:30:00', 90, 'Main Auditorium', 'Google Meet Link will be shared', 'all'),
('University Hackathon Showcase', 'A project showcase and light competition where teams present useful software ideas, prototypes, and complete builds. The event encourages collaboration, presentation practice, and exposure to practical problem solving in a supportive university environment. Judges and guests will focus on useful feedback, creativity, and execution rather than pressure alone.', 'hackathon', 'offline', 3, DATE_ADD(CURDATE(), INTERVAL 32 DAY), '09:00:00', 200, 'Sports Complex', NULL, 'all'),
('Database Design Masterclass', 'This masterclass focuses on schema planning, relationships, normalization, practical query design, and how database structure influences application quality. Students will see how real project requirements turn into tables, keys, and safe update patterns. It is ideal for members who want stronger back-end confidence before final project submission.', 'workshop', 'hybrid', 2, DATE_ADD(CURDATE(), INTERVAL 35 DAY), '13:00:00', 70, 'Computer Lab B', 'Google Meet Link will be shared', 'all'),
('Frontend Polish and UI Review Session', 'A focused review session for students who want to improve the visual quality of their dashboards, forms, cards, and details pages. The facilitator will discuss spacing, alignment, hierarchy, colors, and usability so that participants can make their interfaces feel more modern and complete. Students can observe examples and compare different design decisions.', 'workshop', 'online', 5, DATE_ADD(CURDATE(), INTERVAL 38 DAY), '17:00:00', 55, NULL, 'Zoom UI Review Room', 'all'),
('Project Documentation and Presentation Clinic', 'This clinic helps students prepare README files, documentation notes, report sections, and short demo explanations for university presentations. Clear structure, screenshots, feature summaries, and limitation notes will all be covered. The goal is to help teams present their work with confidence and clarity during review or viva sessions.', 'seminar', 'offline', 2, DATE_ADD(CURDATE(), INTERVAL 41 DAY), '10:30:00', 65, 'Seminar Room 2', NULL, 'all'),
('Cloud and Deployment Essentials', 'An introduction to deployment thinking for student projects, including environments, configuration, hosting basics, file structure, and what teams should verify before sharing a system publicly. Even if students are not deploying yet, this session helps them understand why stable setup, requirements, and configuration matter in real software work.', 'seminar', 'hybrid', 3, DATE_ADD(CURDATE(), INTERVAL 44 DAY), '14:00:00', 75, 'Innovation Hall', 'Meet link will be shared', 'senior_student'),
('Peer Code Review Circle', 'A collaborative review circle where members bring snippets of their current project and receive constructive feedback on readability, structure, naming, validation, and maintainability. The session is designed to be supportive, practical, and useful for teams that want fewer bugs and cleaner code before submission.', 'study_group', 'offline', 4, DATE_ADD(CURDATE(), INTERVAL 47 DAY), '15:00:00', 35, 'Library Collaboration Room', NULL, 'all');

-- 6. Insert sample announcements
INSERT INTO announcements (title, content, announcer_id, category, priority, is_pinned) VALUES
('Welcome to Mentorship Hub Community', 'Welcome to Mentorship Hub, a space created to help students and teachers connect with purpose, confidence, and a strong sense of academic community. Whether you are just starting your university journey or already preparing larger projects, this platform is here to support meaningful mentorship, practical event participation, and stronger collaboration across departments.

Over the coming weeks, members are encouraged to complete their profiles, explore available mentors, read announcements regularly, and join upcoming sessions that match their interests. Even a small first step, such as updating your profile or sending your first mentorship request, can open the door to valuable guidance and long-term growth.

We hope every member uses this platform not only as a tool, but as a community where questions are welcomed, progress is celebrated, and shared learning becomes part of everyday university life.', 1, 'general', 'high', TRUE),
('Academic Advising Week for New Members', 'Academic Advising Week is now open for students who want clearer direction on study planning, module selection, time management, and realistic semester goals. New members are especially encouraged to attend, because early planning often reduces stress and helps students stay focused on what matters most.

During this advising week, teachers and senior mentors will share practical suggestions on how to balance coursework, skill building, project work, and personal development. Students may also ask questions about common first-year challenges, subject difficulty, and how to seek help early instead of waiting until deadlines become overwhelming.

Please watch the events page for advising-related sessions and reserve your place early if you are interested. The goal is to help members begin the term with more clarity, stronger confidence, and a better sense of direction.', 2, 'academic', 'high', FALSE),
('Python Workshop Registration Open', 'Registration is now open for our upcoming Python Workshop, designed especially for students who want a stronger foundation in programming. The session will move carefully through essential concepts such as variables, control flow, loops, functions, and simple problem-solving strategies.

Beyond the technical content, the workshop will also show members how to keep practicing after the session ends. Students will hear practical advice about daily coding habits, small challenge routines, and how to approach mistakes without losing motivation. This makes the event especially useful for members who are still building confidence.

Seats are limited to keep the workshop interactive and beginner-friendly, so interested members should register as early as possible. If you have been waiting for a good place to start with Python, this is an excellent opportunity.', 2, 'event', 'medium', FALSE),
('Mentor Matching Window Now Active', 'The mentor matching window is now active, and members can begin exploring suitable mentor and mentee connections based on shared interests, majors, departments, and goals. This is a great time for junior students to reach out thoughtfully and for senior students or teachers to begin welcoming new requests.

When sending a request, please introduce yourself clearly and explain what kind of support you are looking for. Requests that mention learning goals, project interests, or specific areas of difficulty tend to receive better responses because they help mentors understand how to guide you effectively.

We encourage all members to use this period to build respectful and productive mentorship connections. A good mentorship relationship often begins with one clear message, one honest question, and a willingness to learn consistently over time.', 4, 'opportunity', 'high', TRUE),
('Cyber Safety Awareness Reminder', 'As more academic work, communication, and project collaboration move online, members are reminded to take cyber safety seriously. Please protect your accounts by using strong passwords, avoiding suspicious links, and verifying unfamiliar requests before responding.

Simple habits can prevent bigger problems. Keep your login details private, update passwords when needed, and be careful when downloading files from unknown sources. Students working in groups should also remember that security and trust are part of professional teamwork, not just technical topics for specialists.

A secure digital environment helps everyone learn and collaborate more confidently. Further cyber awareness sessions will be announced soon for members who want practical guidance on safe online behavior.', 3, 'emergency', 'urgent', FALSE),
('Portfolio and Resume Review Opportunity', 'Students preparing for internships, attachments, project showcases, or future job applications are invited to take part in our portfolio and resume review opportunity. This announcement is especially relevant for members who want stronger feedback on how to present their skills, projects, and growth in a professional way.

Reviewers will pay attention not only to formatting, but also to clarity, relevance, and the story your work tells. A resume becomes far more effective when it communicates real effort, real learning, and real impact. Students with GitHub links, project screenshots, presentations, or documentation drafts are encouraged to bring them along.

Thoughtful preparation now can make future applications much stronger. Members who start organizing their achievements early usually feel more confident when formal opportunities arrive.', 10, 'opportunity', 'medium', FALSE),
('Upcoming UI Review and Project Polish Session', 'A special UI Review and Project Polish session will be held soon for students who want their applications to feel more modern, clear, and presentation-ready. This is ideal for teams or individuals who already have a working project but want help improving visual quality, layout consistency, user flow, and the overall impression of the system.

The session will discuss common design problems such as weak spacing, unclear hierarchy, inconsistent colors, and overly crowded screens. It will also highlight simple but effective improvements that can make dashboards, forms, cards, and detail pages look more refined without changing the entire structure of the application.

Members are strongly encouraged to attend with an open mindset and a willingness to refine their work. Small visual improvements often make a very big difference during project demonstrations, evaluations, and final presentations.', 9, 'event', 'high', FALSE);


INSERT INTO announcements (title, content, announcer_id, category, priority, is_pinned) VALUES
('Cross-Major Collaboration Week', 'Cross-Major Collaboration Week will bring together students from different majors so they can exchange ideas, compare project approaches, and discover how multidisciplinary teamwork improves real systems. Members from Computer Science, Information Technology, Software Engineering, Data Science, Cyber Security, and Information Systems are all encouraged to participate with curiosity and openness.

This initiative is especially useful for students who have mostly worked inside their own major and want to understand how other disciplines think about planning, usability, infrastructure, analytics, or security. Strong projects are rarely built from one perspective alone, and this week is designed to help members experience that reality in a practical and welcoming way.

Throughout the week, there will be short discussion circles, mentor-led guidance moments, and informal networking opportunities. Members should come prepared to introduce themselves clearly, describe what they are currently learning, and share the type of collaboration they are hoping to find.', 2, 'general', 'medium', FALSE),
('Capstone Readiness Checkpoint', 'Students preparing for larger final-year or capstone-style work are encouraged to treat this period as an important readiness checkpoint. Before projects become too deep to adjust comfortably, members should review whether their title, scope, features, database plan, and testing strategy are all realistic and aligned.

This announcement is meant to encourage calm, early review rather than last-minute pressure. Teams that verify structure, responsibilities, and documentation early often save themselves a great deal of confusion later. Members should also think carefully about presentation quality, not just code completeness, because communication is part of professional software work.

If you are unsure whether your current direction is strong enough, speak with a teacher or mentor, compare your scope to the time you actually have, and make small improvements now while they are still easy to manage.', 5, 'academic', 'high', FALSE),
('Mentorship Etiquette Reminder', 'As the number of mentorship requests grows, all members are reminded to communicate respectfully, clearly, and professionally. A good request should briefly introduce who you are, what you want help with, and why you believe the person you are contacting is a suitable mentor. Messages that are thoughtful and specific are far more likely to lead to a positive response.

Mentors are encouraged to respond honestly and kindly, even when they are unavailable. Mentees are encouraged to be patient, avoid repeated spam-like messages, and remain open to learning over time instead of expecting instant solutions. Mutual respect creates the kind of environment where genuine progress becomes possible.

This platform works best when communication reflects maturity, curiosity, and academic responsibility. Every message is a small reflection of the kind of collaboration culture we want to build together.', 3, 'general', 'high', FALSE);

-- 7. Insert sample user_skills
INSERT INTO user_skills (user_id, skill_id, proficiency_level) VALUES
(2, 1, 'expert'),  -- Dr. Smith - Python expert
(2, 4, 'advanced'), -- Dr. Smith - AI
(3, 6, 'expert'), -- Prof. Jones - Security
(4, 1, 'advanced'), -- Alex Chen - Python
(4, 3, 'advanced'), -- Alex Chen - JavaScript
(5, 1, 'advanced'), -- Lisa Wong - Python
(5, 4, 'intermediate'), -- Lisa Wong - AI
(6, 6, 'intermediate'), -- James Lee - Security
(7, 1, 'beginner'), -- Kevin Ng - Python
(8, 9, 'beginner'); -- Nina Singh - English

-- 8. Insert sample user_interests
INSERT INTO user_interests (user_id, interest_id, level) VALUES
(4, 3, 5), -- Alex Chen - Web Dev
(4, 1, 4), -- Alex Chen - AI
(5, 1, 5), -- Lisa Wong - AI
(5, 2, 5), -- Lisa Wong - ML
(6, 5, 5), -- James Lee - Security
(7, 3, 4), -- Kevin Ng - Web Dev
(8, 5, 3); -- Nina Singh - Security

-- 9. Insert sample mentorship requests
INSERT INTO mentorship_requests (mentor_id, mentee_id, subject, message, status) VALUES
(2, 7, 'Help with Python basics', 'I am a beginner in Python and would love to learn from you. Can you help me understand loops and functions?', 'pending'),
(3, 8, 'Cybersecurity career advice', 'I am interested in cybersecurity. Can you guide me on learning path and certifications?', 'accepted'),
(4, 7, 'Web development mentorship', 'Want to become a web developer. Need guidance on where to start.', 'pending');

-- 10. Insert sample messages
INSERT INTO messages (request_id, sender_id, message) VALUES
(2, 3, 'Hi! I saw your request about cybersecurity. What specific areas are you interested in?'),
(2, 8, 'I am interested in ethical hacking and network security. Where should I start?'),
(2, 3, 'Great! Start with networking basics, then learn Python for scripting.');

-- =====================================================
-- VERIFY DATA
-- =====================================================
SELECT 'USERS' as section;
SELECT user_id, username, full_name, role, email FROM users;

SELECT 'SKILLS' as section;
SELECT * FROM skills;

SELECT 'EVENTS' as section;
SELECT event_id, title, event_type, start_date FROM events;

SELECT 'ANNOUNCEMENTS' as section;
SELECT announcement_id, title, priority FROM announcements;

SELECT 'MENTORSHIP REQUESTS' as section;
SELECT * FROM mentorship_requests;

-- မူရင်း ENUM တန်ဖိုးတွေကိုကြည့်မယ်
SHOW COLUMNS FROM user_activities LIKE 'activity_type';

-- ENUM ကိုပြင်မယ် (view_dashboard ထည့်မယ်)
ALTER TABLE user_activities 
MODIFY COLUMN activity_type ENUM(
    'login', 'logout', 'profile_view', 'profile_update',
    'mentorship_request_sent', 'mentorship_request_received',
    'mentorship_accepted', 'mentorship_rejected',
    'message_sent', 'message_read',
    'event_created', 'event_joined', 'event_cancelled',
    'announcement_view', 'announcement_created',
    'search_performed', 'resource_viewed',
    'feedback_given', 'certificate_downloaded',
    'view_dashboard'  -- ဒါကိုထည့်လိုက်
) NOT NULL;
