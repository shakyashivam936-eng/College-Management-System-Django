from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from academics.models import Course, Department, Semester
from students.models import Student

from .models import FeeStructure, Payment, StudentFee


class FeesDashboardTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="fees-dashboard-user",
            password="test-password",
        )
        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )
        course = Course.objects.create(
            department=department,
            name="Computer Science",
            code="CSC",
        )
        semester = Semester.objects.create(
            course=course,
            semester_number=1,
            name="First Semester",
        )
        self.student = Student.objects.create(
            student_id="STU-001",
            user=user,
            first_name="Test",
            last_name="Student",
            father_name="Parent",
            mother_name="Parent",
            date_of_birth=date(2005, 1, 1),
            gender="OTHER",
            email="student@example.com",
            phone="1234567890",
            address="Test Street",
            city="Test City",
            state="Test State",
            pincode="123456",
            course=course,
            semester=semester,
            admission_date=date(2025, 1, 1),
        )
        self.fee_structure = FeeStructure.objects.create(
            course=course,
            semester=semester,
            academic_year="2025-2026",
            tuition_fee=Decimal("800.00"),
            exam_fee=Decimal("100.00"),
            library_fee=Decimal("50.00"),
            hostel_fee=Decimal("0.00"),
            other_fee=Decimal("50.00"),
        )

    def test_empty_dashboard_loads(self):
        user = get_user_model().objects.get(username="fees-dashboard-user")
        self.client.force_login(user)

        response = self.client.get(reverse("fees:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_due"], Decimal("0.00"))
        self.assertEqual(response.context["pending_fees"].count(), 0)

    def test_dashboard_calculates_due_balances_and_displays_fee_structure_total(self):
        partial_fee = StudentFee.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            due_date=date(2025, 12, 31),
            total_amount=Decimal("1000.00"),
            paid_amount=Decimal("250.00"),
        )
        StudentFee.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            due_date=date(2025, 12, 31),
            total_amount=Decimal("1000.00"),
            paid_amount=Decimal("1000.00"),
        )
        Payment.objects.create(
            student_fee=partial_fee,
            amount=Decimal("250.00"),
            payment_mode="CASH",
        )
        self.client.force_login(self.student.user)

        response = self.client.get(reverse("fees:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_fees"], Decimal("2000.00"))
        self.assertEqual(response.context["total_paid"], Decimal("1250.00"))
        self.assertEqual(response.context["total_due"], Decimal("750.00"))
        self.assertEqual(response.context["pending_fees"].count(), 1)
        self.assertContains(response, "STU-001")
        self.assertContains(response, "₹1000.00")
