# Mentorship Hub for Polytechnic Students

A practical desktop application developed by applying the knowledge and skills learned in Semester III. This project uses Python, CustomTkinter, and MySQL to provide an academic mentorship platform for Polytechnic students.

## Project Overview

Mentorship Hub for Polytechnic Students is designed to connect students with teachers and senior students for academic guidance, technical skill development, and collaborative learning.

The platform provides a space where students can discover mentors, request mentorship, communicate with other members, and participate in academic activities.

This project was developed as a practical application of the knowledge and skills learned during Semester III.

## Objectives

- Provide accessible academic guidance for Polytechnic students.
- Connect junior students with teachers and senior students.
- Encourage peer-to-peer learning and knowledge sharing.
- Support communication between mentors and mentees.
- Share academic announcements, resources, and events.
- Build a collaborative learning community.

## Main Features

### 1. User and Role Management
- User registration and login.
- Role-based access management.
- User profile management.

### 2. Mentor Discovery
- Browse available mentors.
- Discover teachers and senior students.
- View mentor information and expertise.

### 3. Mentorship Management
- Send mentorship requests.
- Manage mentorship relationships.
- Connect mentors and mentees.

### 4. Messaging
- Communicate with other users.
- Support academic discussions and mentorship communication.

### 5. Events
- View academic and community events.
- Discover learning activities and knowledge-sharing sessions.

### 6. Announcements and Resources
- Share academic announcements.
- Access useful learning resources.
- Keep students informed about important updates.

### 7. Notifications
- Receive relevant application updates and notifications.

### 8. AI-Assisted Learning Support
- Support AI-based learning recommendations and academic assistance where implemented.

## User Roles

| Role | Description |
|---|---|
| Admin | Manages users and application information. |
| Teacher | Provides academic guidance and mentorship. |
| Senior Student | Shares knowledge and mentors junior students. |
| Junior Student | Finds mentors and receives academic support. |

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CustomTkinter | Desktop graphical user interface |
| MySQL | Database management |
| MySQL Connector | Python-MySQL connectivity |
| Pillow | Image processing |
| Tkinter | Desktop GUI support |

## Project Structure

```text
Mentorship-Hub/
│
├── main.py
├── config.py
├── colors.py
├── database.py
├── databasetable.sql
├── i18n.py
├── notification.py
├── utils.py
├── README.md
├── requirements.txt
│
└── gui/
    ├── login_window.py
    ├── register_window.py
    ├── main_window.py
    ├── ui_helpers.py
    ├── about_us_page.py
    │
    ├── dashboard/
    ├── mentorship/
    ├── announcements/
    ├── events/
    └── profile/
```

*Note: The structure above illustrates the main project modules. Refer to the actual source code for the complete folder structure.*

## System Requirements

- Python 3.10 or later
- MySQL Server 8.0 or compatible version
- MySQL Workbench (recommended)
- Windows, macOS, or Linux
- Internet connection for installing dependencies

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/mentorship_hub_for_polytechnic_students.git
```

Navigate to the project directory:

```bash
cd mentorship_hub_for_polytechnic_students
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

1. Start MySQL Server.
2. Open MySQL Workbench.
3. Open the `databasetable.sql` file.
4. Execute the SQL script to create the required database tables.
5. Make sure the database name matches the configuration in the project.

### 5. Configure Database Connection

Open `config.py` and check the MySQL connection settings.

Configure the following values according to your local MySQL setup:

- Host
- Username
- Password
- Database name

Do not publish real database passwords or private credentials on GitHub.

### 6. Run the Application

Run the following command from the project directory:

```bash
python main.py
```

## Demo Accounts

Sample accounts may be provided in the database SQL file for demonstration and testing purposes.

Please refer to the sample account records in `databasetable.sql` if available.

Demo credentials are intended for educational and testing purposes only.

## Future Improvements

- Improved mentor matching and recommendation.
- More advanced AI-assisted learning support.
- Personalized learning roadmaps.
- Enhanced messaging and notifications.
- Additional language support.
- Improved user interface and accessibility.
- More comprehensive testing and security improvements.

## Project Purpose

This project demonstrates the practical application of programming, database management, and software development concepts learned during Semester III.

It aims to encourage academic collaboration, mentorship, and knowledge sharing among Polytechnic students.

## Contributors

Developed as a Semester III practical project by:

- Ei Thu Thu Han
- Mi Aye Chan Mon
- Kaung Myat Zaw
- Kaung Htet Ko Ko

## License

This project is developed for educational and academic purposes.