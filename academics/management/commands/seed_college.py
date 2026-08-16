from datetime import date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from academics.models import (
    AcademicYear,
    Semester,
    Department,
    Course,
    Subject,
)

from faculty.models import Faculty


class Command(BaseCommand):

    help = "Seed College ERP with demo academic data"

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.WARNING(
                "\nStarting College ERP demo data...\n"
            )
        )

        # ==================================================
        # ACADEMIC YEAR
        # ==================================================

        academic_year, _ = AcademicYear.objects.get_or_create(
            name="2026-27",
            defaults={
                "start_date": date(2026, 7, 1),
                "end_date": date(2027, 6, 30),
                "is_active": True,
            }
        )

        # ==================================================
        # SEMESTERS
        # ==================================================

        semesters = {}

        for number in range(1, 9):

            semester, _ = Semester.objects.get_or_create(
                number=number,
                defaults={
                    "name": f"Semester {number}",
                    "is_active": True,
                }
            )

            semesters[number] = semester

        # ==================================================
        # DEPARTMENTS
        # ==================================================

        departments_data = [

            {
                "name": "Computer Engineering",
                "code": "CE",
                "description": (
                    "Focuses on computer hardware, software, "
                    "programming, algorithms, databases, networking, "
                    "artificial intelligence and modern computing technologies."
                ),
                "hod_name": "Dr. Rajesh Patel",
            },

            {
                "name": "Information Technology",
                "code": "IT",
                "description": (
                    "Focuses on software development, web technologies, "
                    "cloud computing, cybersecurity, data management "
                    "and information systems."
                ),
                "hod_name": "Dr. Amit Shah",
            },

            {
                "name": "Mechanical Engineering",
                "code": "ME",
                "description": (
                    "Focuses on mechanical design, manufacturing, "
                    "thermodynamics, robotics, industrial engineering "
                    "and production technologies."
                ),
                "hod_name": "Dr. Nilesh Desai",
            },

            {
                "name": "Civil Engineering",
                "code": "CEV",
                "description": (
                    "Focuses on structural engineering, construction, "
                    "transportation, environmental engineering, "
                    "surveying and infrastructure development."
                ),
                "hod_name": "Dr. Kiran Mehta",
            },
        ]

        departments = {}

        for data in departments_data:

            department, _ = Department.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "hod_name": data["hod_name"],
                    "is_active": True,
                }
            )

            departments[data["code"]] = department

        # ==================================================
        # COURSES
        # ==================================================

        courses_data = [

            (
                "BTECH-CE",
                "B.Tech Computer Engineering",
                "CE",
            ),

            (
                "DIP-CE",
                "Diploma Computer Engineering",
                "CE",
            ),

            (
                "BTECH-IT",
                "B.Tech Information Technology",
                "IT",
            ),

            (
                "DIP-IT",
                "Diploma Information Technology",
                "IT",
            ),

            (
                "BTECH-ME",
                "B.Tech Mechanical Engineering",
                "ME",
            ),

            (
                "DIP-ME",
                "Diploma Mechanical Engineering",
                "ME",
            ),

            (
                "BTECH-CEV",
                "B.Tech Civil Engineering",
                "CEV",
            ),

            (
                "DIP-CEV",
                "Diploma Civil Engineering",
                "CEV",
            ),
        ]

        courses = {}

        for code, name, department_code in courses_data:

            course, _ = Course.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department": departments[department_code],
                    "duration_years": 4 if code.startswith("BTECH") else 3,
                    "description": (
                        f"{name} professional academic program."
                    ),
                    "is_active": True,
                }
            )

            courses[code] = course

        # ==================================================
        # COMPUTER ENGINEERING SUBJECTS
        # ==================================================

        computer_subjects = [

            (1, "Programming Fundamentals", "CE101", 4, "THEORY"),
            (1, "Engineering Mathematics I", "CE102", 4, "THEORY"),
            (1, "Engineering Physics", "CE103", 3, "THEORY"),
            (1, "Basic Electrical Engineering", "CE104", 3, "THEORY"),
            (1, "Programming Lab", "CE105", 2, "LAB"),

            (2, "Data Structures", "CE201", 4, "THEORY"),
            (2, "Engineering Mathematics II", "CE202", 4, "THEORY"),
            (2, "Digital Electronics", "CE203", 3, "THEORY"),
            (2, "Computer Organization", "CE204", 3, "THEORY"),
            (2, "Data Structures Lab", "CE205", 2, "LAB"),

            (3, "Object Oriented Programming", "CE301", 4, "THEORY"),
            (3, "Database Management Systems", "CE302", 4, "THEORY"),
            (3, "Operating Systems", "CE303", 4, "THEORY"),
            (3, "Computer Networks", "CE304", 3, "THEORY"),
            (3, "DBMS Lab", "CE305", 2, "LAB"),

            (4, "Web Development", "CE401", 4, "THEORY"),
            (4, "Software Engineering", "CE402", 3, "THEORY"),
            (4, "Design and Analysis of Algorithms", "CE403", 4, "THEORY"),
            (4, "Microprocessors", "CE404", 3, "THEORY"),
            (4, "Web Development Lab", "CE405", 2, "LAB"),

            (5, "Artificial Intelligence", "CE501", 4, "THEORY"),
            (5, "Machine Learning", "CE502", 4, "THEORY"),
            (5, "Cyber Security", "CE503", 3, "THEORY"),
            (5, "Cloud Computing", "CE504", 3, "THEORY"),
            (5, "AI ML Lab", "CE505", 2, "LAB"),

            (6, "Deep Learning", "CE601", 4, "THEORY"),
            (6, "Big Data Analytics", "CE602", 4, "THEORY"),
            (6, "Mobile Application Development", "CE603", 3, "THEORY"),
            (6, "DevOps", "CE604", 3, "THEORY"),
            (6, "Mobile Development Lab", "CE605", 2, "LAB"),
        ]

        for (
            semester_number,
            name,
            code,
            credits,
            subject_type,
        ) in computer_subjects:

            Subject.objects.update_or_create(
                code=code,
                defaults={
                    "course": courses["BTECH-CE"],
                    "semester": semesters[semester_number],
                    "name": name,
                    "credits": credits,
                    "subject_type": subject_type,
                    "is_active": True,
                }
            )

        # ==================================================
        # INFORMATION TECHNOLOGY SUBJECTS
        # ==================================================

        it_subjects = [

            (1, "Programming in Python", "IT101", 4, "THEORY"),
            (1, "Engineering Mathematics I", "IT102", 4, "THEORY"),
            (1, "Computer Fundamentals", "IT103", 3, "THEORY"),
            (1, "Digital Logic", "IT104", 3, "THEORY"),
            (1, "Python Programming Lab", "IT105", 2, "LAB"),

            (2, "Data Structures", "IT201", 4, "THEORY"),
            (2, "Engineering Mathematics II", "IT202", 4, "THEORY"),
            (2, "Object Oriented Programming", "IT203", 4, "THEORY"),
            (2, "Computer Architecture", "IT204", 3, "THEORY"),
            (2, "OOP Lab", "IT205", 2, "LAB"),

            (3, "Database Management Systems", "IT301", 4, "THEORY"),
            (3, "Operating Systems", "IT302", 4, "THEORY"),
            (3, "Computer Networks", "IT303", 4, "THEORY"),
            (3, "Web Technologies", "IT304", 3, "THEORY"),
            (3, "DBMS Lab", "IT305", 2, "LAB"),
        ]

        for (
            semester_number,
            name,
            code,
            credits,
            subject_type,
        ) in it_subjects:

            Subject.objects.update_or_create(
                code=code,
                defaults={
                    "course": courses["BTECH-IT"],
                    "semester": semesters[semester_number],
                    "name": name,
                    "credits": credits,
                    "subject_type": subject_type,
                    "is_active": True,
                }
            )

        # ==================================================
        # FACULTY
        # ==================================================

        faculty_data = [

            (
                "FAC001",
                "Rahul",
                "Patel",
                "rahul.patel@collegeerp.com",
                "9876543201",
                "M.Tech Computer Engineering",
                8,
                "CE",
            ),

            (
                "FAC002",
                "Amit",
                "Shah",
                "amit.shah@collegeerp.com",
                "9876543202",
                "M.Tech Computer Science",
                6,
                "CE",
            ),

            (
                "FAC003",
                "Neha",
                "Desai",
                "neha.desai@collegeerp.com",
                "9876543203",
                "M.Tech IT",
                7,
                "IT",
            ),

            (
                "FAC004",
                "Nilesh",
                "Mehta",
                "nilesh.mehta@collegeerp.com",
                "9876543204",
                "M.Tech Mechanical",
                9,
                "ME",
            ),

            (
                "FAC005",
                "Kiran",
                "Joshi",
                "kiran.joshi@collegeerp.com",
                "9876543205",
                "M.Tech Civil Engineering",
                10,
                "CEV",
            ),
        ]

        for (
            faculty_id,
            first_name,
            last_name,
            email,
            phone,
            qualification,
            experience,
            department_code,
        ) in faculty_data:

            Faculty.objects.update_or_create(
                faculty_id=faculty_id,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone,
                    "qualification": qualification,
                    "experience_years": experience,
                    "department": departments[department_code],
                    "joining_date": date(2020, 7, 1),
                    "is_active": True,
                }
            )

        # ==================================================
        # DONE
        # ==================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                " College ERP data seeded successfully!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Academic Year : 2026-27"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Semesters     : 8"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Departments   : 4"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Courses       : 8"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Faculty       : 5"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Subjects      : 45+"
            )
        )

        self.stdout.write("")