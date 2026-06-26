# LiG Student & Mentor Portal

A Django-based **Student Attachment/Internship Management System** for **LuckyTech Innovation Ground (LiG Technology)**, a Ghanaian technology training organisation. The platform manages the full lifecycle of an 8-week industrial attachment programme — from online application and payment through curriculum delivery, mentor oversight, attendance tracking, assignment submission, and PDF certificate generation.

The project also doubles as a **penetration testing lab** with 10 intentionally introduced security vulnerabilities for educational purposes (see [`cyber.md`](cyber.md)).

---

## Features

### Public
- Landing page with hero, benefits, specialisations, FAQ
- Online application with attachment letter upload
- Role-based authentication (Student / Mentor / Admin)

### Student Portal
- Dashboard with announcements and progress summary
- Course outline with milestone-based week progression
- Assignment submission (URL-based)
- Daily attendance check-in (mentor-approved)
- Payment processing via **Paystack** (GHS)
- Download payment receipts (PDF) and completion certificates (PDF)
- Access learning materials
- Password management

### Mentor Portal
- View and manage assigned students
- Review and grade assignment submissions
- Mark week completion and approve attendance
- Manage curriculum weeks and upload learning materials

### Admin Dashboard
- Dashboard with registration, payment, and revenue stats
- Manage cohorts, students, mentors, and curriculum
- Approve / suspend / delete student accounts
- Issue and revoke certificates
- Post announcements (optionally cohort-scoped)
- View and filter payments, attendance, and assignment records

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 5.x |
| **Database** | SQLite3 (dev), PostgreSQL (production) |
| **Payments** | Paystack (GHS) |
| **PDF Generation** | ReportLab 4.x |
| **Email** | Django mail (console backend in dev, Gmail SMTP in prod) |
| **Security** | django-ratelimit, django-csp, session hardening |
| **Config** | python-decouple (.env) |
| **Frontend** | HTML templates, CSS, Font Awesome, Google Fonts |

## Quick Start

```bash
# Clone
git clone https://github.com/<your-org>/ligplatform.git
cd ligplatform

# Set up venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env   # (create one if missing — see settings.py for keys)

# Migrate & run
python manage.py migrate
python manage.py runserver
```

Create a superuser to access the admin dashboard at `/manage/`:

```bash
python manage.py createsuperuser
```

### Environment Variables

Set these in `.env`:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development |
| `PAYSTACK_PUBLIC_KEY` | Paystack public key |
| `PAYSTACK_SECRET_KEY` | Paystack secret key |
| `USE_POSTGRES` | Set `True` to use PostgreSQL |
| `EMAIL_HOST_USER` | Gmail address for email notifications |
| `EMAIL_HOST_PASSWORD` | Gmail app password |

---

## Project Structure

```
ligplatform/
├── core/                  # Main Django app
│   ├── models.py          # 11 models (Cohort, Course, Student, Mentor, etc.)
│   ├── views.py           # All views (student, mentor, admin, public)
│   ├── urls.py            # 59 URL routes
│   ├── emails.py          # Email notification logic
│   ├── paystack.py        # Paystack API wrapper
│   └── pdfs.py            # PDF generation (certificates & receipts)
├── ligplatform/           # Django project config
│   ├── settings.py
│   └── urls.py
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── media/                 # Uploaded files (gitignored)
├── cyber.md               # Penetration testing lab guide
├── requirements.txt
└── manage.py
```

---

## Penetration Testing Lab

This project is intentionally vulnerable for educational purposes. [`cyber.md`](cyber.md) documents **10 security vulnerabilities** (from stored XSS to session fixation) with step-by-step exploitation guides and recommended fixes. It is designed for beginners learning web application security.

> **Do not deploy this project as-is in production.** Review `cyber.md` and apply the mitigations first.

---

## License

Educational / internal use. See `LICENSE` if present.
