# Mentorship Hub - Final Setup Guide

## Recommended Setup
Use a **fresh database** for the best experience.

## 1) Create Database
Create a MySQL database, for example:

```sql
CREATE DATABASE mentorship_hub;
```

## 2) Configure Environment
This project reads database settings from environment variables.
Set these before running the app:

- `MENTORSHIP_DB_HOST`
- `MENTORSHIP_DB_USER`
- `MENTORSHIP_DB_PASSWORD`
- `MENTORSHIP_DB_NAME`
- `MENTORSHIP_DB_PORT`

Example values:

- Host: `localhost`
- User: `root`
- Password: your MySQL password
- Database: `mentorship_hub`
- Port: `3306`

## 3) Import Schema and Sample Data
Run `databasetable.sql` against your new database.
It includes:
- tables
- sample users
- teachers
- announcements
- events
- sample mentorship-related data foundations

## 4) Install Requirements
```bash
pip install -r requirements.txt
```

## 5) Run Project
```bash
python main.py
```

## Sample Accounts
### Admin
- Username: `admin`
- Password: `admin123`

### Teachers
- Username: `dr.smith`
- Password: `password123`
- Username: `prof.jones`
- Password: `password123`
- Username: `dr.emily.chen`
- Password: `password123`
- Username: `dr.michael.tan`
- Password: `password123`
- Username: `prof.amara.ko`
- Password: `password123`
- Username: `dr.daniel.owens`
- Password: `password123`

### Senior Students
- Username: `alex.chen`
- Password: `password123`
- Username: `lisa.wong`
- Password: `password123`
- Username: `james.lee`
- Password: `password123`

### Junior Students
- Username: `kevin.ng`
- Password: `password123`
- Username: `nina.singh`
- Password: `password123`

## Languages
The project includes a 3-language foundation:
- English
- Myanmar
- Japanese

The language can be changed from **Settings** and the main navigation/settings experience will reflect that choice.

## Notes
- For the smoothest demo, use a fresh database.
- If your system does not show Myanmar/Japanese perfectly, install fonts that support those scripts.
