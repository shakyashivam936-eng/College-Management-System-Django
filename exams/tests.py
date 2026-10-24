from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from academics.models import Course, Department, Semester, Subject
from exams.models import Exam, ExamSchedule, ExamType, StudentMark
from exams.services import generate_exam_result
from students.models import Student


class StudentMarkSubjectFieldTest(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )
        self.course = Course.objects.create(
            department=self.department,
            name="BCA",
            code="BCA-101",
        )
        self.semester = Semester.objects.create(
            course=self.course,
            semester_number=1,
            name="Semester 1",
        )
        self.user = get_user_model().objects.create_user(
            username="student1",
            password="secret123",
            email="student1@example.com",
            first_name="Test",
            last_name="Student",
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id="STU-001",
            first_name="Test",
            last_name="Student",
            father_name="Father",
            mother_name="Mother",
            date_of_birth=date(2000, 1, 1),
            gender="MALE",
            email="student1@example.com",
            phone="9999999999",
            address="Test Address",
            city="City",
            state="State",
            pincode="123456",
            course=self.course,
            semester=self.semester,
            admission_date=date(2024, 1, 1),
        )
        self.exam_type = ExamType.objects.create(
            name="SEMESTER",
            max_marks=100,
        )
        self.exam = Exam.objects.create(
            name="Mid Semester",
            exam_type=self.exam_type,
            course=self.course,
            semester=self.semester,
            academic_year="2024-25",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
        )
        self.subject1 = Subject.objects.create(
            semester=self.semester,
            name="Mathematics",
            code="MATH-101",
            credits=4,
            max_marks=100,
        )
        self.subject2 = Subject.objects.create(
            semester=self.semester,
            name="Physics",
            code="PHY-101",
            credits=4,
            max_marks=100,
        )
        self.schedule1 = ExamSchedule.objects.create(
            exam=self.exam,
            subject=self.subject1,
            exam_date=date(2024, 1, 2),
            start_time=time(9, 0),
            end_time=time(10, 0),
            room="A101",
            max_marks=100,
            pass_marks=40,
        )
        self.schedule2 = ExamSchedule.objects.create(
            exam=self.exam,
            subject=self.subject2,
            exam_date=date(2024, 1, 3),
            start_time=time(9, 0),
            end_time=time(10, 0),
            room="A102",
            max_marks=80,
            pass_marks=32,
        )

    def test_student_mark_has_subject_field(self):
        field = StudentMark._meta.get_field("subject")
        self.assertEqual(field.related_model.__name__, "Subject")

    def test_generate_exam_result_calculates_correct_summary(self):
        StudentMark.objects.create(
            exam_schedule=self.schedule1,
            subject=self.subject1,
            student=self.student,
            marks_obtained=75,
            attendance="PRESENT",
        )
        StudentMark.objects.create(
            exam_schedule=self.schedule2,
            subject=self.subject2,
            student=self.student,
            marks_obtained=65,
            attendance="PRESENT",
        )

        result = generate_exam_result(self.exam.id, self.student.id)

        self.assertEqual(result.total_marks, 180)
        self.assertEqual(result.obtained_marks, 140)
        self.assertEqual(float(result.percentage), 77.78)
        self.assertEqual(result.grade, "B+")
        self.assertEqual(result.status, "PASS")
