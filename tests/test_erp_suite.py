import os
import sys
from decimal import Decimal
from datetime import timedelta, date

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from academics.models import Department, Course, Semester, AcademicYear, Subject
from students.models import Student
from faculty.models import Faculty, FacultySubjectAssignment
from fees.models import Fee, FeePayment
from assignments.models import Assignment, AssignmentSubmission
from results.models import Exam, Result
from notifications.models import Notification, create_notification
from audit_logs.models import AuditLog, log_action

User = get_user_model()


class CollegeERPSuiteTestCase(TestCase):
    def setUp(self):
        # Create Users
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'pass123')
        self.stu1_user = User.objects.create_user('stu1_test', 'stu1@test.com', 'pass123')
        self.stu2_user = User.objects.create_user('stu2_test', 'stu2@test.com', 'pass123')
        self.fac1_user = User.objects.create_user('fac1_test', 'fac1@test.com', 'pass123')

        # Create Academic Structure
        self.dept = Department.objects.create(name='Computer Science', code='CS', is_active=True)
        self.course = Course.objects.create(name='B.Tech CSE', code='CSE', department=self.dept, is_active=True)
        self.sem = Semester.objects.create(name='Semester 1', number=1, is_active=True)
        self.ay = AcademicYear.objects.create(name='2026-2027', start_date=date(2026, 6, 1), end_date=date(2027, 5, 31), is_active=True)
        self.subject = Subject.objects.create(name='Data Structures', code='CS101', course=self.course, semester=self.sem, is_active=True)

        # Create Profiles
        self.stu1 = Student.objects.create(
            user=self.stu1_user, student_id='STU1001', first_name='StudentOne', last_name='Test',
            gender='MALE', department=self.dept, course=self.course, semester=self.sem, academic_year=self.ay, date_of_birth=date(2002, 1, 1)
        )
        self.stu2 = Student.objects.create(
            user=self.stu2_user, student_id='STU1002', first_name='StudentTwo', last_name='Test',
            gender='FEMALE', department=self.dept, course=self.course, semester=self.sem, academic_year=self.ay, date_of_birth=date(2002, 2, 2)
        )
        self.fac1 = Faculty.objects.create(
            user=self.fac1_user, faculty_id='FAC1001', first_name='FacultyOne', last_name='Test',
            email='fac1@test.com', department=self.dept, qualification='Ph.D.', joining_date=date(2015, 1, 1)
        )

        FacultySubjectAssignment.objects.create(faculty=self.fac1, subject=self.subject, is_active=True)

        self.client_admin = Client(HTTP_HOST='localhost')
        self.client_admin.force_login(self.admin_user)

        self.client_stu1 = Client(HTTP_HOST='localhost')
        self.client_stu1.force_login(self.stu1_user)

        self.client_stu2 = Client(HTTP_HOST='localhost')
        self.client_stu2.force_login(self.stu2_user)

    def test_01_fee_precision_and_overpayment_validation(self):
        fee = Fee.objects.create(
            student=self.stu1, academic_year=self.ay, course=self.course, semester=self.sem,
            fee_type='TUITION', total_amount=Decimal('50000.00'), due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(fee.pending_amount, Decimal('50000.00'))

        p1 = FeePayment.objects.create(fee=fee, amount=Decimal('30000.00'), payment_method='CASH')
        fee.refresh_from_db()
        self.assertEqual(fee.total_paid, Decimal('30000.00'))
        self.assertEqual(fee.pending_amount, Decimal('20000.00'))
        self.assertEqual(fee.computed_status, 'PARTIAL')

        # Overpayment validation test via view POST
        res = self.client_admin.post(f'/fees/{fee.id}/payment/create/', {
            'amount': '30000.00', # Exceeds pending 20000.00
            'payment_date': timezone.now().date().strftime('%Y-%m-%d'),
            'payment_method': 'CASH'
        })
        self.assertIn('cannot exceed', res.content.decode().lower())

    def test_02_student_data_isolation(self):
        fee2 = Fee.objects.create(
            student=self.stu2, academic_year=self.ay, course=self.course, semester=self.sem,
            fee_type='EXAM', total_amount=Decimal('5000.00'), due_date=timezone.now().date() + timedelta(days=30)
        )
        # Student 1 attempts to access Student 2 fee detail
        res = self.client_stu1.get(f'/fees/{fee2.id}/')
        self.assertEqual(res.status_code, 403)

    def test_03_notification_and_audit_log_system(self):
        # Dispatch notification
        notif = create_notification(self.stu1_user, 'Test Title', 'Test Message', 'SYSTEM', '/dashboard/')
        self.assertIsNotNone(notif)
        self.assertFalse(notif.is_read)

        # Mark read via view
        res = self.client_stu1.get(f'/notifications/{notif.id}/read/', follow=True)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

        # Log audit action
        log_action(self.admin_user, 'Test Action', 'TestModel', 1, 'Audit log test description')
        log_entry = AuditLog.objects.filter(action='Test Action').first()
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.user, self.admin_user)

    def test_04_receipt_number_uniqueness(self):
        fee = Fee.objects.create(
            student=self.stu1, academic_year=self.ay, course=self.course, semester=self.sem,
            fee_type='HOSTEL', total_amount=Decimal('10000.00'), due_date=timezone.now().date() + timedelta(days=30)
        )
        p1 = FeePayment.objects.create(fee=fee, amount=Decimal('5000.00'), payment_method='UPI')
        p2 = FeePayment.objects.create(fee=fee, amount=Decimal('5000.00'), payment_method='UPI')
        self.assertNotEqual(p1.receipt_number, p2.receipt_number)
