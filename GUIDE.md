# LiG Platform - New User Guide

Welcome to the **LiG Student & Mentor Portal**! This guide will help you understand, set up, and work with this Django-based internship management system.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Prerequisites](#prerequisites)
5. [Getting Started](#getting-started)
6. [Environment Variables](#environment-variables)
7. [Project Structure](#project-structure)
8. [Core Concepts](#core-concepts)
9. [User Roles](#user-roles)
10. [Running the Application](#running-the-application)
11. [Development Workflow](#development-workflow)
12. [Testing](#testing)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)
15. [Contributing](#contributing)

---

## Project Overview

The LiG Platform is a **Student Attachment/Internship Management System** for **LuckyTech Innovation Ground (LiG Technology)**, a Ghanaian technology training organisation. The platform manages the full lifecycle of an 8-week industrial attachment programme.

### What It Does

- **Online Application**: Students can apply for the internship programme
- **Payment Processing**: Handle attachment fees via Paystack (GHS)
- **Curriculum Management**: 8-week structured learning programme
- **Attendance Tracking**: Daily check-ins with mentor approval
- **Assignment Submission**: URL-based submission system
- **Certificate Generation**: PDF completion certificates
- **Role-based Access**: Student, Mentor, and Admin portals

### Important Note

> ⚠️ **Security**: This project is intentionally vulnerable for educational purposes. It contains 10 security vulnerabilities for penetration testing practice. See `cyber.md` for details. **Do not deploy as-is in production.**

---

## Key Features

### Public Features
- Landing page with hero section, benefits, and FAQ
- Online application with attachment letter upload
- Role-based authentication system

### Student Portal
- Dashboard with announcements and progress
- Course outline with milestone tracking
- Assignment submission (URL-based)
- Daily attendance check-in
- Payment processing via Paystack
- PDF receipt and certificate downloads
- Learning materials access

### Mentor Portal
- View assigned students
- Review and grade assignments
- Mark week completion
- Approve attendance
- Upload learning materials

### Admin Dashboard
- Registration, payment, and revenue stats
- Manage cohorts, students, mentors
- Approve/suspend/delete accounts
- Issue/revoke certificates
- Post announcements
- View filtered records

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Framework** | Django 5.x |
| **Database** | SQLite3 (dev), PostgreSQL (production) |
| **Payments** | Paystack (GHS) |
| **PDF Generation** | ReportLab 4.x |
| **Email** | Django mail (console in dev, SMTP in prod) |
| **Security** | django-ratelimit, django-csp, session hardening |
| **Config** | python-decouple (.env) |
| **Frontend** | HTML templates, CSS, Font Awesome, Google Fonts |

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **pip** (Python package manager)
- **Git** for version control
- **Virtual environment** support (venv)
- **Paystack account** (for payment integration)
- **PostgreSQL** (for production deployment)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/ligplatform.git
cd ligplatform
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env  # If .env.example exists, otherwise create manually
```

Edit `.env` with your settings (see [Environment Variables](#environment-variables) section).

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Start Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## Environment Variables

Set these in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Enable debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `PAYSTACK_PUBLIC_KEY` | Paystack public key | Required for payments |
| `PAYSTACK_SECRET_KEY` | Paystack secret key | Required for payments |
| `USE_POSTGRES` | Use PostgreSQL instead of SQLite | `False` |
| `DB_NAME` | PostgreSQL database name | Required if USE_POSTGRES=True |
| `DB_USER` | PostgreSQL username | Required if USE_POSTGRES=True |
| `DB_PASSWORD` | PostgreSQL password | Required if USE_POSTGRES=True |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | Email username | Required for email |
| `EMAIL_HOST_PASSWORD` | Email password | Required for email |
| `DEFAULT_FROM_EMAIL` | Default sender email | `LuckyTech <no-reply@lig.com.gh>` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | Empty |

### Generating a Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Project Structure

```
ligplatform/
├── core/                          # Main Django app
│   ├── models.py                  # 11 models (Cohort, Student, Mentor, etc.)
│   ├── views.py                   # All views (1200+ lines)
│   ├── urls.py                    # 59 URL routes
│   ├── emails.py                  # Email notification logic
│   ├── paystack.py                # Paystack API wrapper
│   ├── pdfs.py                    # PDF generation (certificates & receipts)
│   ├── admin.py                   # Django admin configuration
│   ├── templatetags/              # Custom template tags
│   │   └── core_extras.py
│   └── migrations/                # Database migrations
├── ligplatform/                   # Django project config
│   ├── settings.py                # Project settings
│   ├── urls.py                    # Root URL configuration
│   ├── wsgi.py                    # WSGI entry point
│   └── asgi.py                    # ASGI entry point
├── templates/                     # HTML templates
│   └── core/                      # 38 template files
│       ├── base.html              # Base template
│       ├── home.html              # Landing page
│       ├── dashboard.html         # Student dashboard
│       ├── admin_dashboard.html   # Admin dashboard
│       └── ...
├── static/                        # Static files
│   ├── css/                       # Stylesheets
│   ├── js/                        # JavaScript
│   ├── images/                    # Images (logo, etc.)
│   └── docs/                      # Documentation files
├── media/                         # User uploads (gitignored)
├── requirements.txt               # Python dependencies
├── manage.py                      # Django management command
├── deploy.sh                      # Deployment script
├── cyber.md                       # Security vulnerabilities guide
└── .env                           # Environment variables (gitignored)
```

---

## Core Concepts

### Models (Database Schema)

The application uses 11 main models:

#### 1. **Cohort**
- Represents a training cycle (e.g., "Summer 2026 Cohort")
- Controls registration, max students, fees
- One cohort is marked as default for new applicants

#### 2. **Course**
- Training tracks (Software Development, UI/UX, Networking, etc.)
- Each has an 8-week curriculum
- Can be assigned to multiple mentors

#### 3. **CurriculumWeek**
- One week of a course's programme
- Includes title, description, and milestone
- Links to course and has unique week numbers

#### 4. **Student**
- Main user model for interns
- Stores application details, credentials, status
- Tracks courses, completed weeks, payments
- Auto-generates student ID (format: `LIG-YYYY-XXXX`)

#### 5. **Mentor**
- Instructor account
- Assigned to courses and cohorts
- Can view and manage students
- Auto-generates mentor ID (format: `MENTOR-YYYY-XXXX`)

#### 6. **Payment**
- Tracks Paystack transactions
- Stores reference, amount, status, channel
- Links to student

#### 7. **Assignment**
- Tracks student submissions per week
- Status: not_submitted, reviewed
- Includes mentor feedback

#### 8. **AttendanceRecord**
- Daily attendance tracking
- Status: pending, present, absent, excused
- Links to student, date, and week

#### 9. **Announcement**
- Admin-posted notifications
- Can be cohort-scoped or global
- Sent via email to students

#### 10. **LearningMaterial**
- Files or links uploaded by mentors
- Organized by course and week
- Supports various file types

#### 11. **Certificate**
- Generated completion certificates
- Unique certificate ID (format: `LIG-CERT-YYYY-XXXXXX`)
- Stores generated PDF file

### Authentication System

The app uses a **custom authentication system** (not Django's built-in auth):

- **Students**: Login with `student_id` + `password`
- **Mentors**: Login with `mentor_id` + `password`
- **Admins**: Use Django's built-in auth (`is_superuser`)

Session-based authentication with:
- 7-day session timeout
- HTTP-only cookies
- Secure cookies in production
- SameSite=Lax protection

### Payment Flow

1. Student initiates payment on `/payments/`
2. Paystack popup handles payment
3. Callback to `/payments/callback/`
4. Transaction verified via Paystack API
5. Payment record created/updated
6. Student's payment status updated

---

## User Roles

### Student
- **Access**: `/login/`
- **Can**: View dashboard, submit assignments, check in attendance, make payments, download certificates
- **Cannot**: Grade assignments, manage other students, access admin features

### Mentor
- **Access**: `/mentor/login/`
- **Can**: View assigned students, grade assignments, approve attendance, upload materials
- **Cannot**: Make payments, access admin dashboard, modify curriculum

### Admin
- **Access**: `/manage/login/`
- **Can**: Full access to all features, manage users, configure cohorts, view reports
- **Cannot**: (Full access)

---

## Running the Application

### Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python manage.py runserver

# Access at: http://127.0.0.1:8000/
```

### Available URLs

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/apply/` | Student application |
| `/login/` | Student login |
| `/dashboard/` | Student dashboard |
| `/payments/` | Payment page |
| `/course-outline/` | Course outline |
| `/attendance/` | Attendance check-in |
| `/materials/` | Learning materials |
| `/certificate/` | Download certificate |
| `/mentor/login/` | Mentor login |
| `/mentor/` | Mentor dashboard |
| `/manage/login/` | Admin login |
| `/manage/` | Admin dashboard |
| `/admin/` | Django admin |

### Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Collect static files (for production)
python manage.py collectstatic

# Open Django shell
python manage.py shell

# Check for issues
python manage.py check
```

---

## Development Workflow

### Making Model Changes

1. Edit `core/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Update admin if needed: `core/admin.py`

### Adding New Views

1. Add view function in `core/views.py`
2. Add URL pattern in `core/urls.py`
3. Create template in `templates/core/`
4. Test the new endpoint

### Template Structure

- **Base templates**: `base.html`, `portal_base.html`, `admin_base.html`
- **Student templates**: `dashboard.html`, `payments.html`, etc.
- **Mentor templates**: `mentor_dashboard.html`, etc.
- **Admin templates**: `admin_dashboard.html`, etc.

### Static Files

- **CSS**: `static/css/`
- **JavaScript**: `static/js/`
- **Images**: `static/images/`

---

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core

# Run with verbose output
python manage.py test -v 2
```

### Test Coverage

The project includes `core/tests.py` for unit tests. Expand coverage by:

1. Adding test cases in `core/tests.py`
2. Testing models, views, and forms
3. Using Django's test client for HTTP tests

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure PostgreSQL database
- [ ] Set up Paystack production keys
- [ ] Configure email SMTP settings
- [ ] Set `ALLOWED_HOSTS` to production domain
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `CSRF_TRUSTED_ORIGINS`
- [ ] Set up SSL/TLS certificate
- [ ] Configure Apache/Nginx web server
- [ ] Set up static file serving
- [ ] Configure media file uploads

### Quick Deploy (Apache)

See `deployment.md` for detailed instructions.

### Deploy Script

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'django'"
**Solution**: Activate virtual environment and install requirements
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. "OperationalError: no such table"
**Solution**: Run migrations
```bash
python manage.py migrate
```

#### 3. "SECRET_KEY not set"
**Solution**: Create `.env` file with `SECRET_KEY` variable

#### 4. "Paystack payment not working"
**Solution**: Check Paystack keys in `.env` and ensure you're using test keys for development

#### 5. "Email not sending"
**Solution**: In development, emails print to console. For production, configure SMTP settings.

#### 6. "Static files not loading"
**Solution**: Collect static files
```bash
python manage.py collectstatic
```

#### 7. "Permission denied on media files"
**Solution**: Check file permissions
```bash
chmod -R 755 media/
```

### Debug Mode

Enable debug mode for detailed error messages:

```bash
# In .env
DEBUG=True
```

> ⚠️ **Never enable DEBUG in production!**

---

## Contributing

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for complex functions
- Keep functions focused and concise

### Git Workflow

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request with description

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new feature`
- `fix: Fix bug in payment flow`
- `docs: Update documentation`
- `refactor: Improve code structure`

---

## Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Paystack API**: https://paystack.com/docs/api/
- **ReportLab Documentation**: https://www.reportlab.com/docs/
- **Security Guide**: See `cyber.md` for penetration testing vulnerabilities

---

## Support

For issues or questions:
1. Check this guide first
2. Review existing code and comments
3. Check Django documentation
4. Contact the development team

---

**Welcome to the LiG Platform! We're excited to have you contribute.**
