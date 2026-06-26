from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/', views.apply, name='apply'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('payments/', views.payments, name='payments'),
    path('payments/callback/', views.payment_callback, name='payment_callback'),
    path('payments/history/', views.payment_history, name='payment_history'),
    path('payments/receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),

    path('course-outline/', views.course_outline, name='course_outline'),
    path('course-outline/submit/<int:week_id>/', views.submit_assignment, name='submit_assignment'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('materials/', views.student_materials, name='student_materials'),
    path('certificate/', views.download_certificate, name='download_certificate'),
    path('settings/', views.student_settings, name='student_settings'),

    # Mentor portal
    path('mentor/login/', views.mentor_login, name='mentor_login'),
    path('mentor/logout/', views.mentor_logout, name='mentor_logout'),
    path('mentor/', views.mentor_dashboard, name='mentor_dashboard'),
    path('mentor/student/<int:student_id>/', views.mentor_student_detail, name='mentor_student_detail'),
    path('mentor/curriculum/', views.mentor_curriculum, name='mentor_curriculum'),
    path('mentor/curriculum/<int:week_id>/', views.mentor_curriculum_edit, name='mentor_curriculum_edit'),
    path('mentor/materials/', views.mentor_materials, name='mentor_materials'),
    path('mentor/materials/upload/', views.mentor_material_upload, name='mentor_material_upload'),
    path('mentor/materials/<int:material_id>/delete/', views.mentor_material_delete, name='mentor_material_delete'),
    path('mentor/settings/', views.mentor_settings, name='mentor_settings'),
    path('mentor/change-password/', views.mentor_change_password, name='mentor_change_password'),
    path('mentor/attendance/', views.mentor_attendance, name='mentor_attendance'),
    path('mentor/attendance/<int:record_id>/approve/', views.mentor_attendance_approve, name='mentor_attendance_approve'),
    path('mentor/attendance/<int:record_id>/reject/', views.mentor_attendance_reject, name='mentor_attendance_reject'),

    # Custom admin dashboard
    path('manage/login/', views.admin_login, name='admin_login'),
    path('manage/logout/', views.admin_logout, name='admin_logout'),
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/attendance/', views.admin_attendance, name='admin_attendance'),
    path('manage/assignments/', views.admin_assignments, name='admin_assignments'),
    path('manage/mentors/', views.admin_mentors, name='admin_mentors'),
    path('manage/cohorts/', views.admin_cohorts, name='admin_cohorts'),
    path('manage/curriculum/', views.admin_curriculum, name='admin_curriculum'),
    path('manage/curriculum/<int:course_id>/', views.admin_curriculum, name='admin_curriculum_course'),
    path('manage/attendance-history/', views.admin_attendance_history, name='admin_attendance_history'),
    path('manage/assignment-history/', views.admin_assignment_history, name='admin_assignment_history'),
    path('manage/payments/', views.admin_payments, name='admin_payments'),
    path('manage/students/', views.admin_students, name='admin_students'),
    path('manage/students/<int:student_id>/', views.admin_student_detail, name='admin_student_detail'),
    path('manage/settings/', views.admin_settings, name='admin_settings'),
    path('manage/announcements/', views.admin_announcements, name='admin_announcements'),
]
