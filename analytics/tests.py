from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import Profile
from students.models import Student
from faculty.models import Faculty, FacultySubjectAssignment
from academics.models import Department, Course, AcademicYear, Semester, Subject
from results.models import Exam, Result
from fees.models import Fee, FeePayment


class AnalyticsModuleTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser("admin_analyst", "admin@test.com", "pass123")
        Profile.objects.update_or_create(user=self.admin_user, defaults={"role": "ADMIN"})

        self.dept = Department.objects.create(name="Computer Science", code="CS")
        self.course = Course.objects.create(department=self.dept, name="B.Tech CS", code="BTCS")
        self.ay = AcademicYear.objects.create(name="2026-2027", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
        self.sem = Semester.objects.create(number=1, name="Semester 1")
        self.subject = Subject.objects.create(course=self.course, semester=self.sem, name="Data Structures", code="CS101", credits=4)

        self.stu1_user = User.objects.create_user("stu_analyst1", "s1@test.com", "pass123")
        Profile.objects.update_or_create(user=self.stu1_user, defaults={"role": "STUDENT"})
        self.stu1 = Student.objects.create(
            user=self.stu1_user, student_id="STU-A1", first_name="John", last_name="Doe",
            department=self.dept, course=self.course, semester=self.sem, academic_year=self.ay
        )

        self.fac_user = User.objects.create_user("fac_analyst", "f@test.com", "pass123")
        Profile.objects.update_or_create(user=self.fac_user, defaults={"role": "FACULTY"})
        self.fac = Faculty.objects.create(
            user=self.fac_user, faculty_id="FAC-A1", first_name="Jane", last_name="Smith", department=self.dept
        )
        FacultySubjectAssignment.objects.create(faculty=self.fac, subject=self.subject, is_active=True)

        self.client_admin = Client(HTTP_HOST="localhost")
        self.client_admin.force_login(self.admin_user)

        self.client_stu = Client(HTTP_HOST="localhost")
        self.client_stu.force_login(self.stu1_user)

        self.client_fac = Client(HTTP_HOST="localhost")
        self.client_fac.force_login(self.fac_user)

    def test_01_admin_analytics_dashboard(self):
        res = self.client_admin.get("/analytics/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Institutional Analytics", res.content.decode())

    def test_02_student_denied_admin_analytics(self):
        res = self.client_stu.get("/analytics/")
        # Student gets redirected to student analytics
        self.assertEqual(res.status_code, 302)
        self.assertIn("/analytics/student/", res.url)

    def test_03_student_analytics_page(self):
        res = self.client_stu.get("/analytics/student/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("My Academic Analytics", res.content.decode())

    def test_04_faculty_analytics_page(self):
        res = self.client_fac.get("/analytics/faculty/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Faculty Teaching Analytics", res.content.decode())

    def test_05_export_excel_permissions(self):
        # Student gets 403
        res = self.client_stu.get("/analytics/export/excel/")
        self.assertEqual(res.status_code, 403)

        # Admin gets 200 CSV download
        res = self.client_admin.get("/analytics/export/excel/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "text/csv")
