from django.db import migrations
from django.contrib.auth.hashers import make_password


def hash_passwords(apps, schema_editor):
    Student = apps.get_model('core', 'Student')
    Mentor = apps.get_model('core', 'Mentor')

    for student in Student.objects.iterator():
        if not student.password.startswith(('pbkdf2_', 'bcrypt', 'argon2', 'scrypt')):
            student.password = make_password(student.password)
            student.save(update_fields=['password'])

    for mentor in Mentor.objects.iterator():
        if not mentor.password.startswith(('pbkdf2_', 'bcrypt', 'argon2', 'scrypt')):
            mentor.password = make_password(mentor.password)
            mentor.save(update_fields=['password'])


def reverse_func(apps, schema_editor):
    pass  # One-way migration — cannot un-hash


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_alter_mentor_password_alter_student_password"),
    ]

    operations = [
        migrations.RunPython(hash_passwords, reverse_func),
    ]
