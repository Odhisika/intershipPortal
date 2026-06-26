import random
import string

from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


def generate_student_id():
    """Generate a unique student ID like LIG-2024-8821"""
    year = timezone.now().year
    while True:
        suffix = ''.join(random.choices(string.digits, k=4))
        candidate = f"LIG-{year}-{suffix}"
        if not Student.objects.filter(student_id=candidate).exists():
            return candidate


def generate_password(length=8):
    """Generate a readable random password e.g. Lg7kQ2pX"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


# ---------------------------------------------------------------------------
# Cohorts
# ---------------------------------------------------------------------------

class Cohort(models.Model):
    """A single intake / training cycle (e.g. 'Summer 2026 Cohort')."""

    name = models.CharField(max_length=150)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    registration_open = models.BooleanField(default=True)
    max_students = models.PositiveIntegerField(default=50)
    attachment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)
    required_payment_percentage = models.PositiveIntegerField(default=50)

    is_default = models.BooleanField(
        default=False,
        help_text="The default cohort new applicants are assigned to."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one cohort is marked default
            Cohort.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_default(cls):
        cohort = cls.objects.filter(is_default=True).first()
        if not cohort:
            cohort = cls.objects.first()
        if not cohort:
            cohort = cls.objects.create(name="General Cohort", is_default=True)
        return cohort

    @property
    def required_amount(self):
        return (self.attachment_fee * self.required_payment_percentage) / 100

    @property
    def paid_students_count(self):
        return self.students.filter(payments__status='success').distinct().count()

    @property
    def is_full(self):
        return self.paid_students_count >= self.max_students

    @property
    def is_registration_open(self):
        return self.registration_open and not self.is_full

    @property
    def slots_remaining(self):
        return max(self.max_students - self.paid_students_count, 0)


# Backwards-compatible alias used by older code/templates
SiteConfig = Cohort


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

class Course(models.Model):
    """A subject/track offered by LuckyTech Innovation Ground (e.g. Software Development).

    Each course has its own 8-week curriculum (CurriculumWeek records) and
    can be assigned to one or more mentors.
    """

    CODE_CHOICES = [
        ('software_development', 'Software Development'),
        ('ui_ux_design', 'UI/UX Design'),
        ('networking', 'Networking'),
        ('cybersecurity', 'Cybersecurity'),
        ('it_support', 'IT Support'),
    ]

    code = models.CharField(max_length=50, choices=CODE_CHOICES, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    duration_weeks = models.PositiveIntegerField(default=8)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_for_department(cls, department_code):
        return cls.objects.filter(code=department_code).first()

    @property
    def total_weeks(self):
        return self.weeks.count()


# ---------------------------------------------------------------------------
# Curriculum: Weeks & Assignments
# ---------------------------------------------------------------------------

class CurriculumWeek(models.Model):
    """One week of a course's programme (e.g. Week 1: Python Fundamentals)."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='weeks')
    week_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    milestone = models.TextField(
        blank=True,
        help_text="The weekend milestone / project for this week."
    )

    class Meta:
        unique_together = ('course', 'week_number')
        ordering = ['course', 'week_number']

    def __str__(self):
        return f"{self.course.name} - Week {self.week_number}: {self.title}"


class Assignment(models.Model):
    """A student's submission for a given curriculum week."""

    STATUS_CHOICES = [
        ('not_submitted', 'Not Submitted'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='assignments')
    week = models.ForeignKey(CurriculumWeek, on_delete=models.CASCADE, related_name='assignments')
    submission_url = models.URLField(blank=True, help_text="Link to GitHub repo, live demo, etc.")
    notes = models.TextField(blank=True, help_text="Any notes from the student about their submission.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_submitted')
    feedback = models.TextField(blank=True, help_text="Mentor/admin feedback.")
    submitted_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'week')
        ordering = ['week__week_number']

    def __str__(self):
        return f"{self.student.student_id} - Week {self.week.week_number}"


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

class AttendanceRecord(models.Model):
    """A student's attendance for a given date."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    week = models.ForeignKey(CurriculumWeek, on_delete=models.SET_NULL, blank=True, null=True, related_name='attendance_records')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.student_id} - {self.date} ({self.status})"


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------

class Announcement(models.Model):
    """Admin-posted announcement, optionally scoped to a cohort."""

    title = models.CharField(max_length=200)
    body = models.TextField()
    cohort = models.ForeignKey(
        Cohort, on_delete=models.CASCADE, related_name='announcements',
        blank=True, null=True,
        help_text="Leave blank to show to all students across all cohorts."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# Mentors
# ---------------------------------------------------------------------------

class Mentor(models.Model):
    """A mentor/instructor account with read access to students taking
    their assigned course(s)."""

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mentor_id = models.CharField(max_length=20, unique=True, editable=False)
    password = models.CharField(max_length=128, editable=False)
    courses = models.ManyToManyField(Course, related_name='mentors', blank=True)
    cohorts = models.ManyToManyField(Cohort, related_name='mentors', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if not self.mentor_id:
            year = timezone.now().year
            while True:
                suffix = ''.join(random.choices(string.digits, k=4))
                candidate = f"MENTOR-{year}-{suffix}"
                if not Mentor.objects.filter(mentor_id=candidate).exists():
                    self.mentor_id = candidate
                    break
        if not self.password:
            raw = generate_password()
            self._raw_password = raw
            self.password = make_password(raw)
        elif not self.password.startswith(('pbkdf2_', 'bcrypt', 'argon2', 'scrypt')):
            self._raw_password = self.password
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.mentor_id})"

    @property
    def first_name(self):
        return self.full_name.split(' ')[0]

    @property
    def students(self):
        """All students enrolled in any of this mentor's assigned courses."""
        course_codes = self.courses.values_list('code', flat=True)
        return Student.objects.filter(
            courses__in=self.courses.all()
        ).distinct() | Student.objects.filter(
            department__in=list(course_codes)
        ).distinct()


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------

class Student(models.Model):
    LEVEL_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
    ]

    DEPARTMENT_CHOICES = [
        ('software_development', 'Software Development'),
        ('ui_ux_design', 'UI/UX Design'),
        ('networking', 'Networking'),
        ('cybersecurity', 'Cybersecurity'),
        ('it_support', 'IT Support'),
    ]

    # Application details
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    institution = models.CharField(max_length=150)
    programme = models.CharField(max_length=150)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    duration = models.CharField(max_length=100)
    attachment_letter = models.FileField(upload_to='attachment_letters/', blank=True, null=True)

    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, related_name='students', blank=True, null=True)

    # Selected courses (multi-select)
    courses = models.ManyToManyField(Course, blank=True, related_name='students_enrolled')

    # Track which weeks the student has completed (mentor marks as done)
    completed_weeks = models.ManyToManyField(CurriculumWeek, blank=True, related_name='completed_by')

    # Generated credentials
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    password = models.CharField(max_length=128, editable=False)

    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = generate_student_id()
        if not self.password:
            raw = generate_password()
            self._raw_password = raw
            self.password = make_password(raw)
        elif not self.password.startswith(('pbkdf2_', 'bcrypt', 'argon2', 'scrypt')):
            self._raw_password = self.password
            self.password = make_password(self.password)
        if not self.cohort_id:
            self.cohort = Cohort.get_default()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"

    @property
    def first_name(self):
        return self.full_name.split(' ')[0]

    @property
    def course(self):
        """The first enrolled Course (fallback to department mapping)."""
        first = self.courses.first()
        if first:
            return first
        if self.department:
            return Course.get_for_department(self.department)
        return None

    @property
    def all_courses(self):
        """All enrolled courses."""
        courses = list(self.courses.all())
        if not courses and self.department:
            c = Course.get_for_department(self.department)
            if c:
                courses = [c]
        return courses

    @property
    def config(self):
        """The cohort this student belongs to (or the default cohort)."""
        return self.cohort or Cohort.get_default()

    @property
    def total_paid(self):
        total = self.payments.filter(status='success').aggregate(
            total=models.Sum('amount')
        )['total']
        return total or 0

    @property
    def has_paid_required_amount(self):
        return self.total_paid >= self.config.required_amount

    @property
    def outstanding_balance(self):
        balance = self.config.attachment_fee - self.total_paid
        return balance if balance > 0 else 0

    @property
    def attachment_status(self):
        return "APPROVED" if self.has_paid_required_amount else "PENDING"

    @property
    def progress_percentage(self):
        fee = self.config.attachment_fee
        if fee == 0:
            return 0
        pct = (self.total_paid / fee) * 100
        return min(int(pct), 100)

    @property
    def attendance_percentage(self):
        total = self.attendance_records.exclude(status='pending').count()
        if total == 0:
            return 0
        present = self.attendance_records.filter(status='present').count()
        return int((present / total) * 100)

    @property
    def assignments_completed_count(self):
        return self.assignments.filter(status__in=['submitted', 'reviewed']).count()

    @property
    def is_programme_complete(self):
        for c in self.all_courses:
            if c.weeks.count() == 0:
                return False
        return self.has_paid_required_amount


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    channel = models.CharField(max_length=50, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.student_id} - {self.amount} GHS ({self.status})"


# ---------------------------------------------------------------------------
# Learning Materials
# ---------------------------------------------------------------------------

class LearningMaterial(models.Model):
    """Files or links uploaded by mentors for a specific course week."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    week = models.ForeignKey(CurriculumWeek, on_delete=models.CASCADE, related_name='materials', blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='learning_materials/', blank=True, null=True)
    link = models.URLField(blank=True, help_text="External link (e.g. YouTube, Google Doc)")
    uploaded_by = models.ForeignKey('Mentor', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# Password Reset Tokens
# ---------------------------------------------------------------------------

class PasswordResetToken(models.Model):
    """One-time use token for password reset, expires after 1 hour."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and self.expires_at > timezone.now()

    class Meta:
        ordering = ['-created_at']


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------

class Certificate(models.Model):
    """A generated completion certificate for a student."""

    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='certificate')
    certificate_id = models.CharField(max_length=30, unique=True, editable=False)
    file = models.FileField(upload_to='certificates/', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            year = timezone.now().year
            while True:
                suffix = ''.join(random.choices(string.digits, k=6))
                candidate = f"LIG-CERT-{year}-{suffix}"
                if not Certificate.objects.filter(certificate_id=candidate).exists():
                    self.certificate_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.certificate_id} - {self.student.full_name}"
