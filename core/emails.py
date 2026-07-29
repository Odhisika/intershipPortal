from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime


def _render_email(template_block):
    return render_to_string('emails/base_email.html', {
        'content': template_block,
        'year': datetime.datetime.now().year,
    })


def send_credentials_email(student):
    """Send the generated student ID and password to the student's email."""
    password_display = getattr(student, '_raw_password', None)
    if password_display is None:
        password_display = "(already set — use password reset if forgotten)"

    subject = "Welcome to LuckyTech Innovation Ground — Your Portal Login Details"
    content = f"""
    <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:20px;">Hi {student.first_name},</h2>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      Thank you for registering with <strong>LuckyTech Innovation Ground</strong>.
      Your application has been received and your account is ready.
    </p>

    <div style="background-color:#f8f9fc;border-radius:8px;padding:24px 28px;margin-bottom:24px;border:1px solid #eef0f4;">
      <p style="margin:0 0 12px;color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Your Login Credentials</p>
      <table cellpadding="0" cellspacing="0" style="width:100%;">
        <tr>
          <td style="padding:8px 0;color:#555;font-size:14px;font-weight:600;">Student ID</td>
          <td style="padding:8px 0;color:#1a1a2e;font-size:15px;font-family:monospace;background:#eef0f4;border-radius:4px;padding:8px 12px;text-align:right;">{student.student_id}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#555;font-size:14px;font-weight:600;">Password</td>
          <td style="padding:8px 0;color:#1a1a2e;font-size:15px;font-family:monospace;background:#eef0f4;border-radius:4px;padding:8px 12px;text-align:right;">{password_display}</td>
        </tr>
      </table>
    </div>

    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      Please log in and complete your attachment payment to confirm your placement.
    </p>

    <table cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
      <tr>
        <td style="border-radius:6px;background-color:#1a1a2e;">
          <a href="https://internship.lig.com.gh/login/" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;letter-spacing:0.3px;">Log In to Portal</a>
        </td>
      </tr>
    </table>

    <p style="margin:20px 0 0;color:#888;font-size:13px;line-height:1.6;">
      Best regards,<br>
      <strong style="color:#1a1a2e;">LuckyTech Innovation Ground Team</strong>
    </p>
    """

    html_message = _render_email(content)
    send_mail(
        subject,
        strip_tags(html_message),
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_password_reset_email(student, reset_url):
    """Send a password reset link to the student's email."""
    subject = "LuckyTech Innovation Ground — Password Reset Request"
    content = f"""
    <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:20px;">Hi {student.first_name},</h2>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      You recently requested to reset your password for the
      <strong>LuckyTech Innovation Ground</strong> student portal.
    </p>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      Click the button below to set a new password. This link expires in <strong>1 hour</strong>.
    </p>

    <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td style="border-radius:6px;background-color:#1a1a2e;">
          <a href="{reset_url}" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;letter-spacing:0.3px;">Reset Password</a>
        </td>
      </tr>
    </table>

    <div style="background-color:#fff8f0;border-left:4px solid #f0a030;padding:16px 20px;border-radius:0 6px 6px 0;margin-bottom:24px;">
      <p style="margin:0;color:#886633;font-size:13px;line-height:1.6;">
        If you did not request this, please ignore this email. Your current password will remain unchanged.
      </p>
    </div>

    <p style="margin:20px 0 0;color:#888;font-size:13px;line-height:1.6;">
      Best regards,<br>
      <strong style="color:#1a1a2e;">LuckyTech Innovation Ground Team</strong>
    </p>
    """

    html_message = _render_email(content)
    send_mail(
        subject,
        strip_tags(html_message),
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_mentor_password_reset_email(mentor, reset_url):
    """Send a password reset link to the mentor's email."""
    subject = "LuckyTech Innovation Ground — Password Reset Request"
    content = f"""
    <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:20px;">Hi {mentor.first_name},</h2>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      A password reset has been requested for your
      <strong>LuckyTech Innovation Ground</strong> mentor account.
    </p>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      Click the button below to set a new password. This link expires in <strong>1 hour</strong>.
    </p>

    <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td style="border-radius:6px;background-color:#1a1a2e;">
          <a href="{reset_url}" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;letter-spacing:0.3px;">Reset Password</a>
        </td>
      </tr>
    </table>

    <div style="background-color:#fff8f0;border-left:4px solid #f0a030;padding:16px 20px;border-radius:0 6px 6px 0;margin-bottom:24px;">
      <p style="margin:0;color:#886633;font-size:13px;line-height:1.6;">
        If you did not request this, please ignore this email. Your current password will remain unchanged.
      </p>
    </div>

    <p style="margin:20px 0 0;color:#888;font-size:13px;line-height:1.6;">
      Best regards,<br>
      <strong style="color:#1a1a2e;">LuckyTech Innovation Ground Team</strong>
    </p>
    """

    html_message = _render_email(content)
    send_mail(
        subject,
        strip_tags(html_message),
        settings.DEFAULT_FROM_EMAIL,
        [mentor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_mentor_credentials_email(mentor):
    """Send a mentor their generated login credentials."""
    password_display = getattr(mentor, '_raw_password', None)
    if password_display is None:
        password_display = "(already set — use password reset if forgotten)"

    subject = "LuckyTech Innovation Ground — Your Mentor Portal Login Details"
    content = f"""
    <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:20px;">Hi {mentor.first_name},</h2>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      An account has been created for you on the <strong>LuckyTech Innovation Ground Mentor Portal</strong>.
      You can use the credentials below to log in.
    </p>

    <div style="background-color:#f8f9fc;border-radius:8px;padding:24px 28px;margin-bottom:24px;border:1px solid #eef0f4;">
      <p style="margin:0 0 12px;color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Your Login Credentials</p>
      <table cellpadding="0" cellspacing="0" style="width:100%;">
        <tr>
          <td style="padding:8px 0;color:#555;font-size:14px;font-weight:600;">Mentor ID</td>
          <td style="padding:8px 0;color:#1a1a2e;font-size:15px;font-family:monospace;background:#eef0f4;border-radius:4px;padding:8px 12px;text-align:right;">{mentor.mentor_id}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#555;font-size:14px;font-weight:600;">Password</td>
          <td style="padding:8px 0;color:#1a1a2e;font-size:15px;font-family:monospace;background:#eef0f4;border-radius:4px;padding:8px 12px;text-align:right;">{password_display}</td>
        </tr>
      </table>
    </div>

    <table cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
      <tr>
        <td style="border-radius:6px;background-color:#1a1a2e;">
          <a href="https://internship.lig.com.gh/mentor/login/" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;letter-spacing:0.3px;">Log In to Mentor Portal</a>
        </td>
      </tr>
    </table>

    <p style="margin:20px 0 0;color:#888;font-size:13px;line-height:1.6;">
      Best regards,<br>
      <strong style="color:#1a1a2e;">LuckyTech Innovation Ground Team</strong>
    </p>
    """

    html_message = _render_email(content)
    send_mail(
        subject,
        strip_tags(html_message),
        settings.DEFAULT_FROM_EMAIL,
        [mentor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_announcement_email(announcement, students):
    """Notify a list of students about a new announcement."""
    subject = f"LuckyTech Innovation Ground — {announcement.title}"
    content = f"""
    <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:20px;">New Announcement</h2>
    <div style="background-color:#eef6ff;border-left:4px solid #3b82f6;padding:16px 20px;border-radius:0 6px 6px 0;margin-bottom:24px;">
      <h3 style="margin:0 0 8px;color:#1a1a2e;font-size:16px;">{announcement.title}</h3>
      <p style="margin:0;color:#444;font-size:15px;line-height:1.7;">{announcement.body}</p>
    </div>

    <p style="margin:0 0 0;color:#888;font-size:13px;line-height:1.6;">
      Best regards,<br>
      <strong style="color:#1a1a2e;">LuckyTech Innovation Ground Team</strong>
    </p>
    """

    recipient_list = [s.email for s in students if s.email]
    if not recipient_list:
        return

    html_message = _render_email(content)
    send_mail(
        subject,
        strip_tags(html_message),
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message,
        fail_silently=True,
    )


def send_acceptance_email(student):
    """Send a congratulations email upon acceptance into the LiG programme."""
    subject = "Congratulations! You've Been Accepted into LuckyTech Innovation Ground!"
    content = f"""
    <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:20px;">Hi {student.first_name},</h2>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      We are thrilled to inform you that you have been officially accepted into the
      <strong>LuckyTech Innovation Ground (LiG) Attachment Programme!</strong>
    </p>

    <div style="background-color:#f0fdf4;border-left:4px solid #22c55e;padding:16px 20px;border-radius:0 6px 6px 0;margin-bottom:24px;">
      <p style="margin:0;color:#166534;font-size:15px;line-height:1.7;">
        Congratulations! Your payment has been confirmed and you are now fully enrolled.
        Welcome to the LiG community — we look forward to having you on board!
      </p>
    </div>

    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      Please log in to your student portal to view your dashboard, access learning materials, and track your progress throughout the programme.
    </p>

    <table cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
      <tr>
        <td style="border-radius:6px;background-color:#1a1a2e;">
          <a href="https://internship.lig.com.gh/login/" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;letter-spacing:0.3px;">Log In to Portal</a>
        </td>
      </tr>
    </table>

    <p style="margin:20px 0 0;color:#888;font-size:13px;line-height:1.6;">
      Best regards,<br>
      <strong style="color:#1a1a2e;">LuckyTech Innovation Ground Team</strong>
    </p>
    """

    html_message = _render_email(content)
    send_mail(
        subject,
        strip_tags(html_message),
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_certificate_ready_email(student):
    """Notify a student their certificate is ready for download."""
    subject = "LuckyTech Innovation Ground — Your Certificate is Ready!"
    content = f"""
    <h2 style="margin:0 0 8px;color:#1a1a2e;font-size:20px;">Hi {student.first_name},</h2>
    <p style="margin:0 0 20px;color:#444;font-size:15px;line-height:1.7;">
      Congratulations on completing the <strong>LuckyTech Innovation Ground Attachment Programme!</strong>
    </p>

    <div style="background-color:#f0fdf4;border-left:4px solid #22c55e;padding:16px 20px;border-radius:0 6px 6px 0;margin-bottom:24px;">
      <p style="margin:0;color:#166534;font-size:15px;line-height:1.7;">
        Your certificate of completion is now available for download in your student portal under <strong>Course Outline</strong>.
      </p>
    </div>

    <table cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
      <tr>
        <td style="border-radius:6px;background-color:#1a1a2e;">
          <a href="https://internship.lig.com.gh/student/login/" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;letter-spacing:0.3px;">Download Certificate</a>
        </td>
      </tr>
    </table>

    <p style="margin:20px 0 0;color:#888;font-size:13px;line-height:1.6;">
      Best regards,<br>
      <strong style="color:#1a1a2e;">LuckyTech Innovation Ground Team</strong>
    </p>
    """

    html_message = _render_email(content)
    send_mail(
        subject,
        strip_tags(html_message),
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        html_message=html_message,
        fail_silently=True,
    )
