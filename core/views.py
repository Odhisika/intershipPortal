import uuid
import secrets
import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils import timezone
from django.db import models as db_models
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit

from .models import (
    Student, Payment, Cohort, Course, CurriculumWeek, Assignment,
    AttendanceRecord, Announcement, Mentor, Certificate, LearningMaterial,
    PasswordResetToken,
)
from .emails import (
    send_credentials_email, send_password_reset_email,
    send_mentor_credentials_email, send_mentor_password_reset_email,
    send_announcement_email, send_certificate_ready_email,
    send_acceptance_email,
)
from . import paystack
from .pdfs import generate_certificate_pdf, generate_receipt_pdf


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LOGIN_ATTEMPT_LIMIT = 3
LOGIN_LOCKOUT_SECONDS = 3600  # 1 hour


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


def _login_failed_key(login_type, identifier):
    return f"login_attempts:{login_type}:{identifier}"


def _login_lockout_key(login_type, identifier):
    return f"login_lockout:{login_type}:{identifier}"


def check_login_rate_limit(request, login_type, identifier):
    """Returns (is_locked, seconds_remaining). identifier = user id or IP."""
    lockout_key = _login_lockout_key(login_type, identifier)
    lockout_until = cache.get(lockout_key)
    if lockout_until:
        remaining = int(lockout_until - timezone.now().timestamp())
        if remaining > 0:
            return True, remaining
        cache.delete(lockout_key)
    return False, 0


def record_failed_login(request, login_type, identifier):
    """Increment failed attempts. Locks out after LOGIN_ATTEMPT_LIMIT."""
    key = _login_failed_key(login_type, identifier)
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, LOGIN_LOCKOUT_SECONDS)
    if attempts >= LOGIN_ATTEMPT_LIMIT:
        lockout_until = timezone.now().timestamp() + LOGIN_LOCKOUT_SECONDS
        cache.set(
            _login_lockout_key(login_type, identifier),
            lockout_until,
            LOGIN_LOCKOUT_SECONDS,
        )
        cache.delete(key)
        return True
    return False


def clear_login_attempts(login_type, identifier):
    """Clear failed attempts on successful login."""
    cache.delete(_login_failed_key(login_type, identifier))
    cache.delete(_login_lockout_key(login_type, identifier))

def get_logged_in_student(request):
    student_pk = request.session.get('student_pk')
    if not student_pk:
        return None
    return Student.objects.filter(pk=student_pk).first()


def require_login(view_func):
    def wrapper(request, *args, **kwargs):
        student = get_logged_in_student(request)
        if not student:
            messages.error(request, "Please log in to access your portal.")
            return redirect('login')
        return view_func(request, student, *args, **kwargs)
    return wrapper


def get_logged_in_mentor(request):
    mentor_pk = request.session.get('mentor_pk')
    if not mentor_pk:
        return None
    return Mentor.objects.filter(pk=mentor_pk).first()


def require_mentor_login(view_func):
    def wrapper(request, *args, **kwargs):
        mentor = get_logged_in_mentor(request)
        if not mentor:
            messages.error(request, "Please log in to access the mentor portal.")
            return redirect('mentor_login')
        return view_func(request, mentor, *args, **kwargs)
    return wrapper


def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "Please log in as a superuser to access the admin dashboard.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

def home(request):
    config = Cohort.get_default()
    return render(request, 'core/home.html', {'config': config})


def apply(request):
    config = Cohort.get_default()

    if request.method == 'POST':
        if not config.is_registration_open:
            messages.error(request, "Registration is closed. We have reached our intake capacity for this cohort.")
            return redirect('apply')

        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        institution = request.POST.get('institution', '').strip()
        programme = request.POST.get('programme', '').strip()
        level = request.POST.get('level', '')
        duration = request.POST.get('duration', '').strip()
        attachment_letter = request.FILES.get('attachment_letter')
        has_laptop = request.POST.get('has_laptop') == 'on'

        # --- Validations ---
        errors = False

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, "Please enter a valid email address.")
            errors = True

        # Phone: accept +233XXXXXXXXX, 233XXXXXXXXX, or 0XXXXXXXXX (10+ digits)
        phone_digits = re.sub(r'[\s\-]', '', phone)
        phone_match = False
        normalized_phone = ''
        if phone_digits.startswith('+233') and len(phone_digits) >= 13:
            normalized_phone = phone_digits
            phone_match = True
        elif phone_digits.startswith('233') and len(phone_digits) >= 12:
            normalized_phone = '+' + phone_digits
            phone_match = True
        elif phone_digits.startswith('0') and len(phone_digits) >= 10:
            normalized_phone = '+233' + phone_digits[1:]
            phone_match = True
        if not phone_match:
            messages.error(request, "Please enter a valid Ghana phone number (e.g. +233XXXXXXXXX or 0XXXXXXXXX).")
            errors = True

        if not attachment_letter:
            messages.error(request, "Please upload your attachment letter (PDF).")
            errors = True

        if errors:
            return redirect('apply')

        if Student.objects.filter(email=email).exists():
            messages.error(request, "An application with this email already exists. Please log in to your portal.")
            return redirect('apply')

        if Student.objects.filter(phone=normalized_phone).exists():
            messages.error(request, "An application with this phone number already exists. Please log in to your portal.")
            return redirect('apply')

        student = Student.objects.create(
            full_name=full_name,
            email=email,
            phone=normalized_phone,
            institution=institution,
            programme=programme,
            level=level,
            duration=duration,
            attachment_letter=attachment_letter,
            has_laptop=has_laptop,
            cohort=config,
        )

        # Enroll in all active courses
        for course in Course.objects.filter(is_active=True):
            student.courses.add(course)

        send_credentials_email(student)

        return redirect(f"{reverse('apply')}?success=1")

    return render(request, 'core/apply.html', {'config': config})


# ---------------------------------------------------------------------------
# Login / Logout / Password recovery
# ---------------------------------------------------------------------------

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    if request.method == 'POST':
        ip = _get_client_ip(request)
        is_locked, remaining = check_login_rate_limit(request, 'student', ip)
        if is_locked:
            minutes = remaining // 60
            seconds = remaining % 60
            messages.error(
                request,
                f"Too many failed attempts. Please try again in {minutes}m {seconds}s.",
            )
            return redirect('login')

        student_id = request.POST.get('student_id', '').strip().upper()
        password = request.POST.get('password', '').strip()

        student = Student.objects.filter(student_id=student_id).first()

        if student and student.check_password(password):
            if not student.is_active:
                return redirect(f"{reverse('login')}?suspended=1")
            clear_login_attempts('student', ip)
            request.session.cycle_key()
            request.session['student_pk'] = student.pk
            return redirect('dashboard')

        locked_out = record_failed_login(request, 'student', ip)
        if locked_out:
            messages.error(request, "Too many failed attempts. Your account is locked for 1 hour.")
        else:
            messages.error(request, "Invalid Student ID or Password. Please check your email for your login details.")
        return redirect('login')

    return render(request, 'core/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('home')


@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def forgot_password(request):
    """Email a password reset link with a one-time token."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        student = Student.objects.filter(email=email).first()

        if not student:
            messages.error(
                request,
                "We couldn't find an account with that email address. "
                "Please check your email or register a new account.",
            )
            return render(request, 'core/forgot_password.html', {'submitted': True})

        # Per-email rate limit: max 2 resets per hour
        rate_key = f"password_reset:{email}"
        resets_sent = cache.get(rate_key, 0)
        if resets_sent >= 2:
            messages.error(
                request,
                "You've already requested a reset link twice this hour. "
                "Please wait before trying again.",
            )
            return render(request, 'core/forgot_password.html', {'submitted': True})

        # Invalidate existing unused tokens for this student
        student.reset_tokens.filter(used=False).update(used=True)

        token = secrets.token_urlsafe(48)
        PasswordResetToken.objects.create(
            student=student,
            token=token,
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        reset_url = request.build_absolute_uri(
            reverse('reset_password', kwargs={'token': token})
        )
        send_password_reset_email(student, reset_url)

        cache.set(rate_key, resets_sent + 1, 3600)

        messages.success(
            request,
            "A password reset link has been sent to your email. "
            "Please check your inbox to reset your password."
        )
        return render(request, 'core/forgot_password.html', {'submitted': True})

    return render(request, 'core/forgot_password.html')


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def reset_password(request, token):
    """Verify a reset token and allow the student to set a new password."""
    reset = get_object_or_404(PasswordResetToken, token=token)

    if not reset.is_valid():
        # If expired / already used — redirect but still invalidate to
        # prevent replay of a reused token.
        if not reset.used:
            reset.used = True
            reset.save()
        messages.error(
            request,
            "This password reset link is invalid or has expired. "
            "Please request a new one."
        )
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'core/reset_password.html', {'valid_link': True})

        if new_password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'core/reset_password.html', {'valid_link': True})

        reset.student.set_password(new_password)
        reset.student.save()
        reset.used = True
        reset.save()

        messages.success(
            request,
            "Your password has been reset successfully. You can now log in."
        )
        return redirect('login')

    return render(request, 'core/reset_password.html', {'valid_link': True})


@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def mentor_forgot_password(request):
    """Email a password reset link to a mentor."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        mentor = Mentor.objects.filter(email=email).first()

        if not mentor:
            messages.error(
                request,
                "We couldn't find an account with that email address. "
                "Please check your email or contact the administrator.",
            )
            return render(request, 'core/mentor_forgot_password.html', {'submitted': True})

        # Per-email rate limit: max 2 resets per hour
        rate_key = f"mentor_password_reset:{email}"
        resets_sent = cache.get(rate_key, 0)
        if resets_sent >= 2:
            messages.error(
                request,
                "You've already requested a reset link twice this hour. "
                "Please wait before trying again.",
            )
            return render(request, 'core/mentor_forgot_password.html', {'submitted': True})

        mentor.reset_tokens.filter(used=False).update(used=True)
        token = secrets.token_urlsafe(48)
        PasswordResetToken.objects.create(
            mentor=mentor,
            token=token,
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        reset_url = request.build_absolute_uri(
            reverse('mentor_reset_password', kwargs={'token': token})
        )
        send_mentor_password_reset_email(mentor, reset_url)

        cache.set(rate_key, resets_sent + 1, 3600)

        messages.success(
            request,
            "A password reset link has been sent to your email. "
            "Please check your inbox to reset your password."
        )
        return render(request, 'core/mentor_forgot_password.html', {'submitted': True})

    return render(request, 'core/mentor_forgot_password.html')


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def mentor_reset_password(request, token):
    """Verify a mentor reset token and allow setting a new password."""
    reset = get_object_or_404(PasswordResetToken, token=token)

    if not reset.is_valid():
        if not reset.used:
            reset.used = True
            reset.save()
        messages.error(
            request,
            "This password reset link is invalid or has expired. "
            "Please request a new one."
        )
        return redirect('mentor_forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'core/mentor_reset_password.html', {'valid_link': True})

        if new_password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'core/mentor_reset_password.html', {'valid_link': True})

        reset.user.set_password(new_password)
        reset.user.save()
        reset.used = True
        reset.save()

        messages.success(
            request,
            "Your password has been reset successfully. You can now log in."
        )
        return redirect('mentor_login')

    return render(request, 'core/mentor_reset_password.html', {'valid_link': True})


# ---------------------------------------------------------------------------
# Student portal pages
# ---------------------------------------------------------------------------

@require_login
def dashboard(request, student):
    config = student.config
    announcements = Announcement.objects.filter(
        db_models.Q(cohort=student.cohort) | db_models.Q(cohort__isnull=True)
    )[:5]
    try:
        certificate = student.certificate
    except Certificate.DoesNotExist:
        certificate = None

    context = {
        'student': student,
        'config': config,
        'announcements': announcements,
        'certificate': certificate,
    }
    return render(request, 'core/dashboard.html', context)


@require_login
def payments(request, student):
    config = student.config

    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = float(config.required_amount)

        if amount <= 0:
            messages.error(request, "Please enter a valid payment amount.")
            return redirect('payments')

        reference = f"LIG-{student.student_id}-{uuid.uuid4().hex[:10]}".upper()

        Payment.objects.create(
            student=student,
            reference=reference,
            amount=amount,
            status='pending',
        )

        callback_url = request.build_absolute_uri(reverse('payment_callback'))
        response = paystack.initialize_transaction(
            email=student.email,
            amount_ghs=amount,
            reference=reference,
            callback_url=callback_url,
        )

        if response.get('status') and response.get('data', {}).get('authorization_url'):
            return redirect(response['data']['authorization_url'])

        messages.error(
            request,
            "We couldn't connect to Paystack right now. "
            f"({response.get('message', 'Unknown error')}) Please try again shortly."
        )
        return redirect('payments')

    context = {
        'student': student,
        'config': config,
        'min_payment': config.required_amount,
        'full_balance': config.attachment_fee,
        'fully_paid': student.has_paid_required_amount,
    }
    return render(request, 'core/payments.html', context)


def payment_callback(request):
    """Paystack redirects here after a transaction attempt."""
    reference = request.GET.get('reference') or request.GET.get('trxref')

    if not reference:
        messages.error(request, "No payment reference was provided.")
        return redirect('login')

    payment = Payment.objects.filter(reference=reference).first()
    if not payment:
        messages.error(request, "We could not find that payment record.")
        return redirect('login')

    result = paystack.verify_transaction(reference)

    if result.get('status') and result.get('data', {}).get('status') == 'success':
        data = result['data']
        payment.status = 'success'
        payment.channel = data.get('channel', '')
        paid_at = data.get('paid_at')
        if paid_at:
            payment.paid_at = paid_at
        else:
            payment.paid_at = timezone.now()
        payment.amount = data.get('amount', 0) / 100  # pesewas -> GHS
        payment.save()

        student = payment.student
        if student.has_paid_required_amount and not student.is_approved:
            student.is_approved = True
            student.save()
            send_acceptance_email(student)

        messages.success(request, "Payment successful! Please log in to view your updated dashboard.")
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, "Payment could not be verified. If you were charged, please contact support.")

    return redirect('login')


@require_login
def payment_history(request, student):
    history = student.payments.all()
    config = student.config
    context = {
        'student': student,
        'history': history,
        'config': config,
    }
    return render(request, 'core/payment_history.html', context)


@require_login
def download_receipt(request, student, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, student=student, status='success')
    pdf_bytes = generate_receipt_pdf(student, payment)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.reference}.pdf"'
    return response


# ---------------------------------------------------------------------------
# Course outline, attendance & assignments
# ---------------------------------------------------------------------------

@require_login
def course_outline(request, student):
    courses = student.all_courses
    course_id = request.GET.get('course')
    if course_id:
        course = next((c for c in courses if c.id == int(course_id)), None)
        if not course:
            course = courses[0] if courses else None
    else:
        course = courses[0] if courses else None

    completed_ids = set(student.completed_weeks.values_list('id', flat=True))

    week_data = []
    previous_completed = True  # First week is always open
    if course:
        for week in course.weeks.all():
            is_open = previous_completed
            is_completed = week.id in completed_ids
            assignment = student.assignments.filter(week=week).first()
            week_data.append({
                'week': week,
                'assignment': assignment,
                'is_open': is_open,
                'is_completed': is_completed,
            })
            # Next week opens only when this week is completed
            previous_completed = is_completed

    context = {
        'student': student,
        'courses': courses,
        'course': course,
        'week_data': week_data,
    }
    return render(request, 'core/course_outline.html', context)


@require_login
def attendance_view(request, student):
    """Students can request check-in; mentor must approve."""
    today = timezone.now().date()
    course = student.course
    current_week = course.weeks.first() if course else None

    if request.method == 'POST':
        record, created = AttendanceRecord.objects.get_or_create(
            student=student, date=today,
            defaults={'status': 'pending', 'week': current_week},
        )
        if created:
            messages.success(request, "Check-in request sent! Your mentor will confirm your attendance.")
        else:
            messages.success(request, "You've already requested check-in for today.")
        return redirect('attendance')

    records = student.attendance_records.all()[:30]
    already_checked_in = student.attendance_records.filter(date=today).exists()

    context = {
        'student': student,
        'records': records,
        'already_checked_in': already_checked_in,
        'today': today,
        'attendance_percentage': student.attendance_percentage,
    }
    return render(request, 'core/attendance.html', context)


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------

@require_login
def download_certificate(request, student):
    if not student.is_programme_complete:
        messages.error(request, "Your certificate isn't ready yet. Complete all payments and assignments to unlock it.")
        return redirect('course_outline')

    try:
        certificate = student.certificate
    except Certificate.DoesNotExist:
        messages.error(request, "Your certificate hasn't been issued yet. The admin will generate it once your programme completion is verified.")
        return redirect('dashboard')

    pdf_bytes = generate_certificate_pdf(student, certificate)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{student.student_id}.pdf"'
    return response


# ---------------------------------------------------------------------------
# Mentor portal
# ---------------------------------------------------------------------------

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def mentor_login(request):
    if request.method == 'POST':
        ip = _get_client_ip(request)
        is_locked, remaining = check_login_rate_limit(request, 'mentor', ip)
        if is_locked:
            minutes = remaining // 60
            seconds = remaining % 60
            messages.error(
                request,
                f"Too many failed attempts. Please try again in {minutes}m {seconds}s.",
            )
            return redirect('mentor_login')

        mentor_id = request.POST.get('mentor_id', '').strip().upper()
        password = request.POST.get('password', '').strip()

        mentor = Mentor.objects.filter(mentor_id=mentor_id).first()

        if mentor and mentor.check_password(password):
            if not mentor.is_active:
                return redirect(f"{reverse('mentor_login')}?suspended=1")
            clear_login_attempts('mentor', ip)
            request.session.cycle_key()
            request.session['mentor_pk'] = mentor.pk
            return redirect('mentor_dashboard')

        locked_out = record_failed_login(request, 'mentor', ip)
        if locked_out:
            messages.error(request, "Too many failed attempts. Your account is locked for 1 hour.")
        else:
            messages.error(request, "Invalid Mentor ID or Password.")
        return redirect('mentor_login')

    return render(request, 'core/mentor_login.html')


def mentor_logout(request):
    request.session.flush()
    return redirect('mentor_login')


@require_mentor_login
def mentor_dashboard(request, mentor):
    students = mentor.students.all()
    context = {
        'mentor': mentor,
        'students': students,
    }
    return render(request, 'core/mentor_dashboard.html', context)


@require_mentor_login
def mentor_student_detail(request, mentor, student_id):
    course_codes = mentor.courses.values_list('code', flat=True)
    student = get_object_or_404(
        Student.objects.filter(
            db_models.Q(department__in=course_codes) | db_models.Q(courses__code__in=course_codes)
        ).distinct(),
        pk=student_id
    )

    if request.method == 'POST':
        # Week completion toggle
        week_id = request.POST.get('complete_week_id')
        if week_id:
            week = get_object_or_404(CurriculumWeek, pk=week_id, course__mentors=mentor)
            if student.completed_weeks.filter(pk=week.id).exists():
                student.completed_weeks.remove(week)
                messages.success(request, f"Week {week.week_number} marked as incomplete.")
            else:
                student.completed_weeks.add(week)
                messages.success(request, f"Week {week.week_number} marked as complete.")
            return redirect('mentor_student_detail', student_id=student.id)

        assignment_id = request.POST.get('assignment_id')
        feedback = request.POST.get('feedback', '').strip()
        assignment = get_object_or_404(
            Assignment, pk=assignment_id, student=student,
            week__course__in=mentor.courses.all(),
        )
        assignment.feedback = feedback
        assignment.status = 'reviewed'
        assignment.reviewed_at = timezone.now()
        assignment.save()
        messages.success(request, f"Feedback saved for Week {assignment.week.week_number}.")
        return redirect('mentor_student_detail', student_id=student.id)

    mentor_course_ids = mentor.courses.values_list('id', flat=True)
    assignments = student.assignments.filter(week__course__in=mentor_course_ids)
    attendance_records = student.attendance_records.filter(
        week__course__in=mentor_course_ids
    )[:30]
    courses = [c for c in student.all_courses if c.id in mentor_course_ids]
    completed_ids = set(student.completed_weeks.values_list('id', flat=True))

    # Build week data per course
    courses_weeks = []
    for c in courses:
        week_list = []
        for w in c.weeks.all():
            week_list.append({
                'week': w,
                'is_completed': w.id in completed_ids,
            })
        courses_weeks.append({
            'course': c,
            'weeks': week_list,
        })

    context = {
        'mentor': mentor,
        'student': student,
        'assignments': assignments,
        'attendance_records': attendance_records,
        'courses_weeks': courses_weeks,
    }
    return render(request, 'core/mentor_student_detail.html', context)


# ---------------------------------------------------------------------------
# Mentor curriculum (edit weeks for assigned courses)
# ---------------------------------------------------------------------------

@require_mentor_login
def mentor_curriculum(request, mentor):
    courses = mentor.courses.all()
    course = None
    weeks = CurriculumWeek.objects.none()
    if request.GET.get('course'):
        course = get_object_or_404(Course, pk=request.GET['course'], mentors=mentor)
        weeks = course.weeks.all()
    context = {
        'mentor': mentor,
        'courses': courses,
        'course': course,
        'weeks': weeks,
    }
    return render(request, 'core/mentor_curriculum.html', context)


@require_mentor_login
def mentor_curriculum_edit(request, mentor, week_id):
    week = get_object_or_404(CurriculumWeek, pk=week_id, course__mentors=mentor)
    if request.method == 'POST':
        week.title = request.POST.get('title', week.title)
        week.description = request.POST.get('description', week.description)
        week.milestone = request.POST.get('milestone', week.milestone)
        week.save()
        messages.success(request, f"Week {week.week_number} updated.")
        return redirect('mentor_curriculum')
    return redirect('mentor_curriculum')


# ---------------------------------------------------------------------------
# Mentor learning materials
# ---------------------------------------------------------------------------

@require_mentor_login
def mentor_materials(request, mentor):
    courses = mentor.courses.all()
    materials = LearningMaterial.objects.filter(course__in=courses)
    context = {
        'mentor': mentor,
        'materials': materials,
        'courses': courses,
    }
    return render(request, 'core/mentor_materials.html', context)


@require_mentor_login
def mentor_material_upload(request, mentor):
    if request.method == 'POST':
        course_id = request.POST.get('course')
        week_id = request.POST.get('week')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        link = request.POST.get('link', '').strip()
        file = request.FILES.get('file')

        if not title:
            messages.error(request, "Title is required.")
            return redirect('mentor_materials')

        course = get_object_or_404(Course, pk=course_id, mentors=mentor)
        week = CurriculumWeek.objects.filter(pk=week_id, course=course).first() if week_id else None

        LearningMaterial.objects.create(
            course=course, week=week, title=title,
            description=description, link=link, file=file,
            uploaded_by=mentor,
        )
        messages.success(request, f"Material '{title}' uploaded.")
        return redirect('mentor_materials')

    return redirect('mentor_materials')


@require_mentor_login
def mentor_material_delete(request, mentor, material_id):
    material = get_object_or_404(LearningMaterial, pk=material_id, course__mentors=mentor)
    material.file.delete(save=False)
    material.delete()
    messages.success(request, "Material deleted.")
    return redirect('mentor_materials')


# ---------------------------------------------------------------------------
# Mentor change password
# ---------------------------------------------------------------------------

@ratelimit(key='user', rate='5/m', method='POST', block=True)
@require_login
def student_settings(request, student):
    if request.method == 'POST':
        current = request.POST.get('current_password', '').strip()
        new = request.POST.get('new_password', '').strip()
        confirm = request.POST.get('confirm_password', '').strip()
        if not student.check_password(current):
            messages.error(request, "Current password is incorrect.")
        elif not new:
            messages.error(request, "New password cannot be empty.")
        elif new != confirm:
            messages.error(request, "New passwords do not match.")
        elif len(new) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        else:
            student.set_password(new)
            student.save()
            messages.success(request, "Password changed successfully.")
        return redirect('student_settings')
    return render(request, 'core/student_settings.html', {'student': student})


@require_mentor_login
def mentor_settings(request, mentor):
    return render(request, 'core/mentor_settings.html', {'mentor': mentor})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@require_mentor_login
def mentor_change_password(request, mentor):
    if request.method == 'POST':
        current = request.POST.get('current_password', '').strip()
        new = request.POST.get('new_password', '').strip()
        confirm = request.POST.get('confirm_password', '').strip()
        if not mentor.check_password(current):
            messages.error(request, "Current password is incorrect.")
        elif not new:
            messages.error(request, "New password cannot be empty.")
        elif new != confirm:
            messages.error(request, "New passwords do not match.")
        elif len(new) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        else:
            mentor.set_password(new)
            mentor.save()
            messages.success(request, "Password changed successfully.")
        return redirect('mentor_settings')
    return redirect('mentor_settings')


# ---------------------------------------------------------------------------
# Mentor attendance approval
# ---------------------------------------------------------------------------

@require_mentor_login
def mentor_attendance(request, mentor):
    """Show all pending attendance records for the mentor's students."""
    students = mentor.students.all()
    pending_records = AttendanceRecord.objects.filter(
        student__in=students, status='pending',
        week__course__in=mentor.courses.all(),
    ).select_related('student', 'week').order_by('-date')

    context = {
        'mentor': mentor,
        'pending_records': pending_records,
    }
    return render(request, 'core/mentor_attendance.html', context)


@require_mentor_login
def mentor_attendance_approve(request, mentor, record_id):
    record = get_object_or_404(
        AttendanceRecord, pk=record_id, status='pending',
        student__in=mentor.students.all(),
        week__course__in=mentor.courses.all(),
    )
    record.status = 'present'
    record.save()
    messages.success(request, f"Attendance approved for {record.student.full_name} on {record.date}.")
    return redirect('mentor_attendance')


@require_mentor_login
def mentor_attendance_reject(request, mentor, record_id):
    record = get_object_or_404(
        AttendanceRecord, pk=record_id, status='pending',
        student__in=mentor.students.all(),
        week__course__in=mentor.courses.all(),
    )
    record.status = 'absent'
    record.save()
    messages.success(request, f"Attendance rejected for {record.student.full_name} on {record.date}.")
    return redirect('mentor_attendance')


# ---------------------------------------------------------------------------
# Student learning materials
# ---------------------------------------------------------------------------

@require_login
def student_materials(request, student):
    if not student.has_paid_required_amount:
        return render(request, 'core/student_materials.html', {
            'student': student,
            'courses': student.all_courses,
            'course': None,
            'materials': None,
            'payment_required': True,
        })

    courses = student.all_courses
    course_id = request.GET.get('course')
    if course_id:
        course = next((c for c in courses if c.id == int(course_id)), None)
        if not course:
            course = courses[0] if courses else None
    else:
        course = courses[0] if courses else None

    materials = LearningMaterial.objects.filter(course=course) if course else LearningMaterial.objects.none()
    context = {
        'student': student,
        'courses': courses,
        'course': course,
        'materials': materials,
        'payment_required': False,
    }
    return render(request, 'core/student_materials.html', context)


# ---------------------------------------------------------------------------
# Admin attendance history
# ---------------------------------------------------------------------------

@require_admin
def admin_attendance_history(request):
    records = AttendanceRecord.objects.select_related('student', 'week').all().order_by('-date')
    context = {
        'active': 'attendance',
        'records': records,
    }
    return render(request, 'core/admin_attendance_history.html', context)


# ---------------------------------------------------------------------------
# Admin assignment history
# ---------------------------------------------------------------------------

@require_admin
def admin_assignment_history(request):
    assignments = Assignment.objects.select_related('student', 'week').all().order_by('-reviewed_at', '-id')
    context = {
        'active': 'assignments',
        'assignments': assignments,
    }
    return render(request, 'core/admin_assignment_history.html', context)


# ---------------------------------------------------------------------------
# Custom admin dashboard
# ---------------------------------------------------------------------------

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def admin_login(request):
    if request.method == 'POST':
        ip = _get_client_ip(request)
        is_locked, remaining = check_login_rate_limit(request, 'admin', ip)
        if is_locked:
            minutes = remaining // 60
            seconds = remaining % 60
            messages.error(
                request,
                f"Too many failed attempts. Please try again in {minutes}m {seconds}s.",
            )
            return redirect('admin_login')

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            clear_login_attempts('admin', ip)
            login(request, user)
            return redirect('admin_dashboard')

        locked_out = record_failed_login(request, 'admin', ip)
        if locked_out:
            messages.error(request, "Too many failed attempts. Your account is locked for 1 hour.")
        else:
            messages.error(request, "Invalid superuser credentials.")
        return redirect('admin_login')
    return render(request, 'core/admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@require_admin
def admin_dashboard(request):
    cohort = Cohort.get_default()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'announcement':
            title = request.POST.get('title', '').strip()
            body = request.POST.get('body', '').strip()
            cohort_id = request.POST.get('announcement_cohort') or None
            target_cohort = Cohort.objects.filter(pk=cohort_id).first() if cohort_id else None

            if title and body:
                announcement = Announcement.objects.create(
                    title=title, body=body, cohort=target_cohort
                )
                if target_cohort:
                    students = Student.objects.filter(cohort=target_cohort)
                else:
                    students = Student.objects.all()
                send_announcement_email(announcement, students)
                messages.success(request, "Announcement posted and emailed to students.")

        return redirect('admin_dashboard')

    students = Student.objects.all().order_by('-created_at')

    total_registered = students.count()
    paid_students = students.filter(payments__status='success').distinct()
    total_paid_students = paid_students.count()
    pending_students = total_registered - total_paid_students

    total_revenue = Payment.objects.filter(status='success').aggregate(
        total=db_models.Sum('amount')
    )['total'] or 0

    cohorts = Cohort.objects.all()
    announcements = Announcement.objects.all()[:10]

    context = {
        'active': 'dashboard',
        'config': cohort,
        'cohort': cohort,
        'cohorts': cohorts,
        'students': students,
        'total_registered': total_registered,
        'total_paid_students': total_paid_students,
        'pending_students': pending_students,
        'total_revenue': total_revenue,
        'slots_remaining': cohort.slots_remaining,
        'announcements': announcements,
    }
    return render(request, 'core/admin_dashboard.html', context)


@require_admin
def admin_attendance(request):
    """Redirect to attendance history — mentors handle attendance now."""
    return redirect('admin_attendance_history')


@require_admin
def admin_assignments(request):
    """Redirect to assignment history — mentors handle reviews now."""
    return redirect('admin_assignment_history')


@require_admin
def admin_mentors(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        course_ids = request.POST.getlist('courses')

        if full_name and email:
            if Mentor.objects.filter(email=email).exists():
                messages.error(request, "A mentor with this email already exists.")
            else:
                mentor = Mentor.objects.create(full_name=full_name, email=email)
                if course_ids:
                    mentor.courses.set(course_ids)
                send_mentor_credentials_email(mentor)
                messages.success(request, f"Mentor {mentor.full_name} created and credentials sent.")

        return redirect('admin_mentors')

    mentors = Mentor.objects.all()
    courses = Course.objects.all()
    context = {'active': 'mentors', 'mentors': mentors, 'courses': courses}
    return render(request, 'core/admin_mentors.html', context)


@require_admin
def admin_mentor_detail(request, mentor_id):
    mentor = get_object_or_404(Mentor, id=mentor_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'reset_password':
            mentor.reset_tokens.filter(used=False).update(used=True)
            token = secrets.token_urlsafe(48)
            PasswordResetToken.objects.create(
                mentor=mentor,
                token=token,
                expires_at=timezone.now() + timezone.timedelta(hours=1),
            )
            reset_url = request.build_absolute_uri(
                reverse('mentor_reset_password', kwargs={'token': token})
            )
            send_mentor_password_reset_email(mentor, reset_url)
            messages.success(request, f"Password reset link has been sent to {mentor.email}.")
        elif action == 'deactivate':
            mentor.is_active = False
            mentor.save()
            messages.info(request, f"{mentor.full_name} has been deactivated.")
        elif action == 'reactivate':
            mentor.is_active = True
            mentor.save()
            messages.success(request, f"{mentor.full_name} has been reactivated.")
        elif action == 'delete':
            mentor.delete()
            messages.success(request, f"Mentor {mentor.full_name} has been deleted.")
            return redirect('admin_mentors')
        return redirect('admin_mentor_detail', mentor_id=mentor.id)

    context = {
        'active': 'mentors',
        'mentor': mentor,
    }
    return render(request, 'core/admin_mentor_detail.html', context)


@require_admin
def admin_cohorts(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Cohort.objects.create(
                name=request.POST.get('name', '').strip() or "New Cohort",
                start_date=request.POST.get('start_date') or None,
                end_date=request.POST.get('end_date') or None,
                max_students=int(request.POST.get('max_students', 50)),
                attachment_fee=request.POST.get('attachment_fee', 300),
                required_payment_percentage=int(request.POST.get('required_payment_percentage', 50)),
                registration_open=True,
            )
            messages.success(request, "New cohort created.")

        elif action == 'set_default':
            cohort_id = request.POST.get('cohort_id')
            cohort = get_object_or_404(Cohort, pk=cohort_id)
            cohort.is_default = True
            cohort.save()
            messages.success(request, f"{cohort.name} is now the default cohort for new applicants.")

        return redirect('admin_cohorts')

    cohorts = Cohort.objects.all()
    context = {'active': 'cohorts', 'cohorts': cohorts}
    return render(request, 'core/admin_cohorts.html', context)


@require_admin
def admin_curriculum(request, course_id=None):
    """Read-only curriculum view — mentors manage weeks."""
    courses = Course.objects.all()

    if course_id:
        course = get_object_or_404(Course, pk=course_id)
    else:
        course = courses.first()

    weeks = course.weeks.all() if course else []
    context = {'active': 'curriculum', 'weeks': weeks, 'courses': courses, 'course': course}
    return render(request, 'core/admin_curriculum.html', context)


# ---------------------------------------------------------------------------
# Admin payments
# ---------------------------------------------------------------------------

@require_admin
def admin_payments(request):
    filter_param = request.GET.get('filter', 'all')
    today = timezone.now().date()
    payments = Payment.objects.select_related('student').all()

    if filter_param == 'week':
        start = today - timezone.timedelta(days=today.weekday())
        payments = payments.filter(created_at__date__gte=start)
    elif filter_param == 'month':
        payments = payments.filter(created_at__month=today.month, created_at__year=today.year)

    # Defaulters: students who haven't met required payment
    defaulters = []
    for s in Student.objects.all():
        if not s.has_paid_required_amount:
            defaulters.append(s)

    total_revenue = Payment.objects.filter(status='success').aggregate(
        total=db_models.Sum('amount')
    )['total'] or 0

    context = {
        'active': 'payments',
        'payments': payments,
        'defaulters': defaulters,
        'total_revenue': total_revenue,
        'filter': filter_param,
    }
    return render(request, 'core/admin_payments.html', context)


# ---------------------------------------------------------------------------
# Admin settings
# ---------------------------------------------------------------------------

@require_admin
def admin_settings(request):
    cohort = Cohort.get_default()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'cohort_settings':
            cohort.max_students = int(request.POST.get('max_students', cohort.max_students))
            cohort.registration_open = request.POST.get('registration_open') == 'on'
            cohort.attachment_fee = request.POST.get('attachment_fee', cohort.attachment_fee)
            cohort.required_payment_percentage = int(
                request.POST.get('required_payment_percentage', cohort.required_payment_percentage)
            )
            cohort.save()
            messages.success(request, "Cohort settings updated successfully.")

        return redirect('admin_settings')

    students = Student.objects.all()
    paid_students = students.filter(payments__status='success').distinct()
    total_paid_students = paid_students.count()
    slots_remaining = max(cohort.max_students - total_paid_students, 0)

    context = {
        'active': 'settings',
        'cohort': cohort,
        'total_paid_students': total_paid_students,
        'slots_remaining': slots_remaining,
    }
    return render(request, 'core/admin_settings.html', context)


# ---------------------------------------------------------------------------
# Admin students
# ---------------------------------------------------------------------------

@require_admin
def admin_students(request):
    cohort_id = request.GET.get('cohort')
    status_filter = request.GET.get('status')

    students = Student.objects.all().order_by('-created_at')
    if cohort_id:
        students = students.filter(cohort_id=cohort_id)
    if status_filter == 'approved':
        students = [s for s in students if s.attachment_status == 'APPROVED']
    elif status_filter == 'pending':
        students = [s for s in students if s.attachment_status == 'PENDING']

    cohorts = Cohort.objects.all()
    context = {
        'active': 'students',
        'students': students,
        'cohorts': cohorts,
        'filter_cohort': cohort_id,
        'filter_status': status_filter,
    }
    return render(request, 'core/admin_students.html', context)


# ---------------------------------------------------------------------------
# Admin announcements
# ---------------------------------------------------------------------------

@require_admin
def admin_student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    payments = student.payments.all().order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            student.is_approved = True
            student.save()
            send_acceptance_email(student)
            messages.success(request, f"{student.full_name} has been approved. Acceptance email sent.")
        elif action == 'unapprove':
            student.is_approved = False
            student.save()
            messages.info(request, f"{student.full_name} approval has been revoked.")
        elif action == 'suspend':
            student.is_active = False
            student.save()
            messages.info(request, f"{student.full_name} has been suspended.")
        elif action == 'reinstate':
            student.is_active = True
            student.save()
            messages.success(request, f"{student.full_name} has been reinstated.")
        elif action == 'delete':
            student.delete()
            messages.success(request, "Student and all associated records have been deleted.")
            return redirect('admin_students')
        elif action == 'issue_certificate':
            if hasattr(student, 'certificate'):
                messages.info(request, f"{student.full_name} already has a certificate issued.")
            else:
                certificate = Certificate(student=student)
                certificate.save()
                pdf_bytes = generate_certificate_pdf(student, certificate)
                certificate.file.save(
                    f"certificate_{student.student_id}.pdf",
                    ContentFile(pdf_bytes),
                )
                certificate.save()
                send_certificate_ready_email(student)
                messages.success(request, f"Certificate issued to {student.full_name} successfully.")
        elif action == 'revoke_certificate':
            if hasattr(student, 'certificate'):
                student.certificate.delete()
                messages.info(request, f"Certificate revoked for {student.full_name}.")
            else:
                messages.info(request, f"{student.full_name} has no certificate to revoke.")
        elif action == 'reset_password':
            student.reset_tokens.filter(used=False).update(used=True)
            token = secrets.token_urlsafe(48)
            PasswordResetToken.objects.create(
                student=student,
                token=token,
                expires_at=timezone.now() + timezone.timedelta(hours=1),
            )
            reset_url = request.build_absolute_uri(
                reverse('reset_password', kwargs={'token': token})
            )
            send_password_reset_email(student, reset_url)
            messages.success(request, f"Password reset link has been sent to {student.email}.")
        return redirect('admin_student_detail', student_id=student.id)

    try:
        certificate = student.certificate
    except Certificate.DoesNotExist:
        certificate = None

    context = {
        'active': 'students',
        'student': student,
        'payments': payments,
        'certificate': certificate,
    }
    return render(request, 'core/admin_student_detail.html', context)


@require_admin
def admin_announcements(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        cohort_id = request.POST.get('announcement_cohort') or None
        target_cohort = Cohort.objects.filter(pk=cohort_id).first() if cohort_id else None

        if title and body:
            announcement = Announcement.objects.create(
                title=title, body=body, cohort=target_cohort
            )
            if target_cohort:
                students = Student.objects.filter(cohort=target_cohort)
            else:
                students = Student.objects.all()
            send_announcement_email(announcement, students)
            messages.success(request, "Announcement posted and emailed to students.")
        return redirect('admin_announcements')

    announcements = Announcement.objects.all()[:50]
    cohorts = Cohort.objects.all()
    context = {
        'active': 'announcements',
        'announcements': announcements,
        'cohorts': cohorts,
    }
    return render(request, 'core/admin_announcements.html', context)
