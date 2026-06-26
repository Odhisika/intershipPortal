from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from .models import (
    Course, CurriculumWeek, Cohort, Student, Mentor,
    LearningMaterial, Payment, AttendanceRecord, Assignment,
)

WEEKS_BY_COURSE = {
    'software_development': [
        ("Python Fundamentals", "Intro to Python syntax, variables, and data types.", "Build a CLI calculator"),
        ("Control Flow & Functions", "Loops, conditionals, and writing reusable functions.", "Build a to-do list app"),
        ("Data Structures", "Lists, dicts, sets, tuples — when to use what.", "Implement a phonebook"),
        ("OOP Basics", "Classes, objects, inheritance, and encapsulation.", "Build a library management system"),
        ("File I/O & Modules", "Reading/writing files, importing modules, pip.", "Build a note-taking app with save/load"),
    ],
    'ui_ux_design': [
        ("Design Fundamentals", "Color theory, typography, layout principles.", "Redesign a landing page"),
        ("User Research", "Interviews, surveys, personas.", "Conduct 5 user interviews"),
        ("Wireframing", "Low-fidelity wireframes and information architecture.", "Wireframe a mobile app"),
        ("Prototyping", "High-fidelity prototypes with Figma.", "Build a clickable prototype"),
        ("Visual Design", "Design systems, components, and accessibility.", "Create a design system"),
    ],
    'networking': [
        ("Network Models", "OSI and TCP/IP models overview.", "Map the OSI layers"),
        ("IP Addressing", "IPv4, IPv6, subnetting, CIDR.", "Subnet a /24 network"),
        ("Routing Basics", "Static and dynamic routing (RIP, OSPF).", "Configure a 3-router network"),
        ("Switch Configuration", "VLANs, trunking, STP.", "Set up 3 VLANs on a switch"),
        ("Network Security", "Firewalls, ACLs, NAT, VPNs.", "Configure a firewall ruleset"),
    ],
}

COURSE_DESCRIPTIONS = {
    'software_development': 'Full-stack Python/Django development programme.',
    'ui_ux_design': 'User interface and experience design programme.',
    'networking': 'Computer networking and infrastructure programme.',
}


def create_seed_data():
    cohort, _ = Cohort.objects.get_or_create(
        name='Test Cohort 2026',
        defaults=dict(
            is_default=True,
            registration_open=True,
            max_students=50,
            attachment_fee=Decimal('300.00'),
            required_payment_percentage=50,
        ),
    )

    courses = {}
    for code, weeks in WEEKS_BY_COURSE.items():
        course, _ = Course.objects.get_or_create(
            code=code,
            defaults=dict(
                name=dict(Course.CODE_CHOICES)[code],
                description=COURSE_DESCRIPTIONS.get(code, ''),
                duration_weeks=len(weeks),
            ),
        )
        courses[code] = course
        for i, (title, desc, milestone) in enumerate(weeks, start=1):
            CurriculumWeek.objects.get_or_create(
                course=course,
                week_number=i,
                defaults=dict(title=title, description=desc, milestone=milestone),
            )

    mentor, _ = Mentor.objects.get_or_create(
        email='mentor@test.com',
        defaults=dict(full_name='Mentor One'),
    )
    mentor.courses.set(courses.values())
    mentor.save()

    return cohort, courses, mentor


def create_student(**overrides):
    params = dict(
        full_name='John Doe',
        email='john@example.com',
        phone='0541234567',
        institution='Test University',
        programme='BSc Computer Science',
        level='300',
        duration='June - November 2026',
    )
    params.update(overrides)
    return Student.objects.create(**params)


def create_materials(mentor, courses):
    for code, course in courses.items():
        week = course.weeks.first()
        LearningMaterial.objects.get_or_create(
            course=course,
            week=week,
            title=f'{course.name} - Week 1 Intro',
            defaults=dict(
                description='Introductory material',
                link='https://example.com/' + code,
                uploaded_by=mentor,
            ),
        )


@override_settings(RATELIMIT_ENABLE=False)
class StudentFlowE2ETest(TestCase):
    """End-to-end test of the entire student lifecycle."""

    @classmethod
    def setUpTestData(cls):
        cls.cohort, cls.courses, cls.mentor = create_seed_data()
        create_materials(cls.mentor, cls.courses)

        # Student enrolled in 2 courses
        cls.student = create_student(cohort=cls.cohort)
        cls.student.courses.set([
            cls.courses['software_development'],
            cls.courses['ui_ux_design'],
        ])

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')

    def login(self):
        return self.client.post(self.login_url, {
            'student_id': self.student.student_id,
            'password': self.student._raw_password,
        })

    # ── Application & Login ──────────────────────────────────────────────

    def test_01_apply_form_shows_multi_select(self):
        r = self.client.get(reverse('apply'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '<select id="courses"')
        self.assertContains(r, 'multiple')
        self.assertContains(r, 'Hold Ctrl/Cmd')

    def test_02_submit_application(self):
        new_email = 'jane@example.com'
        r = self.client.post(reverse('apply'), {
            'full_name': 'Jane Doe',
            'email': new_email,
            'phone': '0201234567',
            'institution': 'Test Uni',
            'programme': 'BSc IT',
            'level': '200',
            'courses': ['software_development', 'networking'],
            'duration': 'June - Nov 2026',
        })
        self.assertRedirects(r, reverse('apply'))
        student = Student.objects.get(email=new_email)
        self.assertEqual(student.courses.count(), 2)
        self.assertTrue(student.courses.filter(code='software_development').exists())
        self.assertTrue(student.courses.filter(code='networking').exists())
        self.assertIsNone(student.department)

    def test_03_duplicate_email_rejected(self):
        r = self.client.post(reverse('apply'), {
            'full_name': 'John Dupe',
            'email': 'john@example.com',
            'phone': '0201234567',
            'institution': 'Test Uni',
            'programme': 'BSc IT',
            'level': '200',
            'courses': ['software_development'],
            'duration': 'June - Nov 2026',
        })
        self.assertRedirects(r, reverse('apply'))
        self.assertIn(
            'already exists',
            ''.join(m.message for m in list(r.wsgi_request._messages)),
        )

    def test_04_student_login(self):
        r = self.login()
        self.assertRedirects(r, reverse('dashboard'))

    # ── Course Outline & Progressive Unlocking ───────────────────────────

    def test_05_course_outline_first_week_open(self):
        self.login()
        r = self.client.get(reverse('course_outline'))
        self.assertEqual(r.status_code, 200)
        # First week should show PENDING (not LOCKED)
        self.assertContains(r, 'PENDING')
        # Later weeks show LOCKED — only check that week 1 is not locked
        w1 = self.courses['software_development'].weeks.get(week_number=1)
        self.assertIn(w1.title, r.content.decode())

    def test_06_course_outline_second_week_locked(self):
        self.login()
        # No weeks completed → week 2 should be locked
        course = self.courses['software_development']
        r = self.client.get(reverse('course_outline'), {'course': course.id})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'LOCKED')
        self.assertContains(r, 'fa-lock')

    def test_07_course_outline_course_tabs(self):
        self.login()
        r = self.client.get(reverse('course_outline'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Software Development')
        self.assertContains(r, 'UI/UX Design')
        self.assertContains(r, 'course-tab')

    def test_08_submit_assignment_locked_week_rejected(self):
        self.login()
        w2 = self.courses['software_development'].weeks.get(week_number=2)
        r = self.client.post(reverse('submit_assignment', args=[w2.id]), {
            'submission_url': 'https://github.com/test/project',
        })
        self.assertRedirects(r, reverse('course_outline'))
        self.assertIn(
            'locked',
            ''.join(m.message for m in list(r.wsgi_request._messages)),
        )

    def test_09_submit_assignment_open_week(self):
        self.login()
        w1 = self.courses['software_development'].weeks.get(week_number=1)
        r = self.client.post(reverse('submit_assignment', args=[w1.id]), {
            'submission_url': 'https://github.com/test/project',
        })
        self.assertRedirects(r, reverse('course_outline'))
        assignment = Assignment.objects.get(student=self.student, week=w1)
        self.assertEqual(assignment.submission_url, 'https://github.com/test/project')
        self.assertEqual(assignment.status, 'submitted')

    # ── Progressive unlocking after mentor marks complete ────────────────

    def test_10_progressive_unlock_after_week1_completed(self):
        self.login()
        course = self.courses['software_development']
        w1 = course.weeks.get(week_number=1)
        w2 = course.weeks.get(week_number=2)
        w3 = course.weeks.get(week_number=3)

        # Mentor marks week 1 complete
        self.student.completed_weeks.add(w1)

        r = self.client.get(reverse('course_outline'), {'course': course.id})
        self.assertEqual(r.status_code, 200)
        # Week 1 should be completed
        self.assertContains(r, 'COMPLETED')
        # Week 2 should now be unlocked and present
        self.assertContains(r, 'Week 2')
        self.assertContains(r, 'PENDING')
        # Week 3 should still be locked
        self.assertContains(r, 'Week 3')
        self.assertContains(r, 'fa-lock')
        self.student.completed_weeks.clear()

    # ── Learning Materials (payment gate) ────────────────────────────────

    def test_11_materials_locked_without_payment(self):
        self.login()
        r = self.client.get(reverse('student_materials'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'locked')
        self.assertContains(r, 'Make a Payment')
        self.assertNotContains(r, 'example.com')

    def test_12_materials_unlocked_after_payment(self):
        Payment.objects.create(
            student=self.student,
            reference='PAY-TEST-001',
            amount=Decimal('150.00'),
            status='success',
            paid_at=timezone.now(),
        )
        self.login()
        r = self.client.get(reverse('student_materials'))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'locked')
        self.assertContains(r, 'example.com')

    def test_13_materials_course_tabs(self):
        Payment.objects.create(
            student=self.student,
            reference='PAY-TEST-002',
            amount=Decimal('150.00'),
            status='success',
            paid_at=timezone.now(),
        )
        self.login()
        r = self.client.get(reverse('student_materials'))
        self.assertContains(r, 'course-tab')

    # ── Attendance (pending → approve/reject) ────────────────────────────

    def test_14_check_in_creates_pending(self):
        self.login()
        course = self.student.course
        week = course.weeks.first()
        r = self.client.post(reverse('attendance'), {'week_id': week.id})
        self.assertRedirects(r, reverse('attendance'))
        record = AttendanceRecord.objects.filter(student=self.student).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.status, 'pending')

    def test_15_mentor_approves_attendance(self):
        week = self.student.course.weeks.first()
        record = AttendanceRecord.objects.create(
            student=self.student,
            date=timezone.now().date(),
            status='pending',
            week=week,
        )
        session = self.client.session
        session['mentor_pk'] = self.mentor.pk
        session.save()

        r = self.client.post(reverse('mentor_attendance_approve', args=[record.id]))
        self.assertRedirects(r, reverse('mentor_attendance'))
        record.refresh_from_db()
        self.assertEqual(record.status, 'present')

    # ── Mentor student detail (week completion toggle) ───────────────────

    def test_16_mentor_marks_week_complete(self):
        session = self.client.session
        session['mentor_pk'] = self.mentor.pk
        session.save()

        w1 = self.courses['software_development'].weeks.get(week_number=1)
        r = self.client.post(
            reverse('mentor_student_detail', args=[self.student.id]),
            {'complete_week_id': w1.id},
        )
        self.assertRedirects(r, reverse('mentor_student_detail', args=[self.student.id]))
        self.assertTrue(self.student.completed_weeks.filter(pk=w1.id).exists())

    def test_17_mentor_unmarks_week_complete(self):
        w1 = self.courses['software_development'].weeks.get(week_number=1)
        self.student.completed_weeks.add(w1)

        session = self.client.session
        session['mentor_pk'] = self.mentor.pk
        session.save()

        r = self.client.post(
            reverse('mentor_student_detail', args=[self.student.id]),
            {'complete_week_id': w1.id},
        )
        self.assertRedirects(r, reverse('mentor_student_detail', args=[self.student.id]))
        self.assertFalse(self.student.completed_weeks.filter(pk=w1.id).exists())

    def test_18_mentor_student_detail_shows_courses(self):
        session = self.client.session
        session['mentor_pk'] = self.mentor.pk
        session.save()

        r = self.client.get(reverse('mentor_student_detail', args=[self.student.id]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Software Development')
        self.assertContains(r, 'UI/UX Design')
        self.assertContains(r, 'Week Progress')

    # ── Student portal sidebar shows courses ─────────────────────────────

    def test_19_sidebar_shows_enrolled_courses(self):
        self.login()
        r = self.client.get(reverse('dashboard'))
        self.assertContains(r, 'Software Development')
        self.assertContains(r, 'UI/UX Design')

    # ── Programme complete checks ────────────────────────────────────────

    def test_20_is_programme_complete(self):
        self.assertFalse(self.student.is_programme_complete)
        # Not paid enough
        Payment.objects.create(
            student=self.student,
            reference='PAY-TEST-003',
            amount=Decimal('150.00'),
            status='success',
            paid_at=timezone.now(),
        )
        self.assertTrue(self.student.is_programme_complete)
