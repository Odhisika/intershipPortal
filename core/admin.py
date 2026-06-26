from django.contrib import admin
from .models import (
    Student, Payment, Cohort, Course, CurriculumWeek, Assignment,
    AttendanceRecord, Announcement, Mentor, Certificate,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'duration_weeks', 'total_weeks', 'is_active')
    list_filter = ('is_active',)


@admin.register(CurriculumWeek)
class CurriculumWeekAdmin(admin.ModelAdmin):
    list_display = ('course', 'week_number', 'title')
    list_filter = ('course',)
    ordering = ('course', 'week_number')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'student_id', 'email', 'cohort', 'department', 'attachment_status', 'total_paid', 'created_at')
    search_fields = ('full_name', 'student_id', 'email')
    list_filter = ('cohort', 'department', 'level')
    readonly_fields = ('student_id', 'created_at')
    exclude = ('password',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'reference', 'amount', 'status', 'channel', 'paid_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('reference', 'student__student_id', 'student__full_name')


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_open', 'max_students', 'paid_students_count', 'attachment_fee', 'required_payment_percentage', 'is_default')
    list_filter = ('registration_open', 'is_default')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'week', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'week')
    search_fields = ('student__student_id', 'student__full_name')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'week')
    list_filter = ('status', 'date')
    search_fields = ('student__student_id', 'student__full_name')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'cohort', 'created_at')
    list_filter = ('cohort',)


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'mentor_id', 'email', 'is_active', 'created_at')
    readonly_fields = ('mentor_id', 'created_at')
    exclude = ('password',)
    filter_horizontal = ('courses', 'cohorts')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student', 'issued_at')
    search_fields = ('certificate_id', 'student__student_id', 'student__full_name')
