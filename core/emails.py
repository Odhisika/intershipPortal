from django.core.mail import send_mail
from django.conf import settings


def send_credentials_email(student):
    """Send the generated student ID and password to the student's email."""
    password_display = getattr(student, '_raw_password', None)
    if password_display is None:
        password_display = "(already set — use password reset if forgotten)"

    subject = "Welcome to LuckyTech Innovation Ground - Your Portal Login Details"
    message = (
        f"Hi {student.first_name},\n\n"
        f"Thank you for registering with LuckyTech Innovation Ground.\n\n"
        f"Your application has been received. You can now log in to your "
        f"student portal using the credentials below:\n\n"
        f"  Student ID: {student.student_id}\n"
        f"  Password:   {password_display}\n\n"
        f"Please log in and complete your attachment payment to confirm "
        f"your placement.\n\n"
        f"Login here: /login/\n\n"
        f"Best regards,\n"
        f"LuckyTech Innovation Ground Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        fail_silently=True,
    )


def send_password_reset_email(student, reset_url):
    """Send a password reset link to the student's email."""
    subject = "LuckyTech Innovation Ground - Password Reset Request"
    message = (
        f"Hi {student.first_name},\n\n"
        f"You recently requested to reset your password for the LuckyTech "
        f"Innovation Ground student portal.\n\n"
        f"Click the link below to set a new password. This link expires "
        f"in 1 hour:\n\n"
        f"  {reset_url}\n\n"
        f"If you did not request this, please ignore this email. Your "
        f"current password will remain unchanged.\n\n"
        f"Best regards,\n"
        f"LuckyTech Innovation Ground Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        fail_silently=True,
    )


def send_mentor_credentials_email(mentor):
    """Send a mentor their generated login credentials."""
    password_display = getattr(mentor, '_raw_password', None)
    if password_display is None:
        password_display = "(already set — use password reset if forgotten)"

    subject = "LuckyTech Innovation Ground - Your Mentor Portal Login Details"
    message = (
        f"Hi {mentor.first_name},\n\n"
        f"An account has been created for you on the LuckyTech Innovation Ground Mentor "
        f"Portal. You can use the credentials below to log in:\n\n"
        f"  Mentor ID: {mentor.mentor_id}\n"
        f"  Password:  {password_display}\n\n"
        f"Login here: /mentor/login/\n\n"
        f"Best regards,\n"
        f"LuckyTech Innovation Ground Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [mentor.email],
        fail_silently=True,
    )


def send_announcement_email(announcement, students):
    """Notify a list of students about a new announcement."""
    subject = f"LuckyTech Innovation Ground Announcement: {announcement.title}"
    message = (
        f"{announcement.body}\n\n"
        f"- LuckyTech Innovation Ground Team"
    )
    recipient_list = [s.email for s in students if s.email]
    if not recipient_list:
        return
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=True,
    )


def send_certificate_ready_email(student):
    """Notify a student their certificate is ready for download."""
    subject = "LuckyTech Innovation Ground - Your Certificate is Ready!"
    message = (
        f"Hi {student.first_name},\n\n"
        f"Congratulations on completing the LuckyTech Innovation Ground Attachment "
        f"Programme!\n\n"
        f"Your certificate of completion is now available for download in "
        f"your student portal under Course Outline.\n\n"
        f"Best regards,\n"
        f"LuckyTech Innovation Ground Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        fail_silently=True,
    )
