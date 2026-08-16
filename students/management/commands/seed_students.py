from datetime import date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from students.models import Student
from academics.models import (
    Department,
    Course,
    Semester,
    AcademicYear,
)
from accounts.models import Profile


class Command(BaseCommand):

    help = "Create demo student accounts and profiles"

    @transaction.atomic
    def handle(self, *args, **options):

        academic_year = AcademicYear.objects.get(
            name="2026-27"
        )

        semester = Semester.objects.get(
            number=1
        )

        course = Course.objects.get(
            code="BTECH-CE"
        )

        department = Department.objects.get(
            code="CE"
        )

        students_data = [

            {
                "student_id": "STU001",
                "first_name": "Urvish",
                "last_name": "Patel",
                "email": "urvish.student@collegeerp.com",
                "phone": "9876543210",
                "username": "stu001",
                "password": "Student@123",
                "guardian_name": "Mahesh Patel",
                "guardian_phone": "9876500011",
            },

            {
                "student_id": "STU002",
                "first_name": "Jay",
                "last_name": "Shah",
                "email": "jay.student@collegeerp.com",
                "phone": "9876543211",
                "username": "stu002",
                "password": "Student@123",
                "guardian_name": "Rakesh Shah",
                "guardian_phone": "9876500012",
            },

            {
                "student_id": "STU003",
                "first_name": "Kunal",
                "last_name": "Desai",
                "email": "kunal.student@collegeerp.com",
                "phone": "9876543212",
                "username": "stu003",
                "password": "Student@123",
                "guardian_name": "Suresh Desai",
                "guardian_phone": "9876500013",
            },

            {
                "student_id": "STU004",
                "first_name": "Meet",
                "last_name": "Joshi",
                "email": "meet.student@collegeerp.com",
                "phone": "9876543213",
                "username": "stu004",
                "password": "Student@123",
                "guardian_name": "Amit Joshi",
                "guardian_phone": "9876500014",
            },

            {
                "student_id": "STU005",
                "first_name": "Dhruv",
                "last_name": "Mehta",
                "email": "dhruv.student@collegeerp.com",
                "phone": "9876543214",
                "username": "stu005",
                "password": "Student@123",
                "guardian_name": "Nitin Mehta",
                "guardian_phone": "9876500015",
            },
        ]

        created_count = 0

        for data in students_data:

            user, user_created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                }
            )

            if user_created:
                user.set_password(
                    data["password"]
                )
                user.save()

                created_count += 1

            else:
                user.first_name = data["first_name"]
                user.last_name = data["last_name"]
                user.email = data["email"]
                user.save()

            profile, _ = Profile.objects.get_or_create(
                user=user
            )

            profile.role = "STUDENT"
            profile.phone = data["phone"]
            profile.save()

            Student.objects.update_or_create(
                student_id=data["student_id"],
                defaults={
                    "user": user,
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                    "phone": data["phone"],
                    "date_of_birth": date(
                        2005,
                        1,
                        15
                    ),
                    "gender": "MALE",
                    "address": "Ahmedabad, Gujarat",
                    "guardian_name": data["guardian_name"],
                    "guardian_phone": data["guardian_phone"],
                    "department": department,
                    "course": course,
                    "semester": semester,
                    "academic_year": academic_year,
                    "is_active": True,
                }
            )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "===================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                " Student data seeded successfully!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "===================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Students created: {created_count}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "Demo password: Student@123"
            )
        )

        self.stdout.write("")