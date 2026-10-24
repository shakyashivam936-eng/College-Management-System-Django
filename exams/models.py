from django.db import models
from django.core.exceptions import ValidationError

from academics.models import Course, Semester, Subject
from students.models import Student

class ExamType(models.Model):

    EXAM_TYPE_CHOICES = (
        ("INTERNAL", "Internal Exam"),
        ("MID_TERM", "Mid Term"),
        ("SEMESTER", "Semester Exam"),
        ("PRACTICAL", "Practical Exam"),
        ("VIVA", "Viva"),
    )

    name = models.CharField(
        max_length=50,
        choices=EXAM_TYPE_CHOICES
    )

    max_marks = models.PositiveIntegerField(default=100)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        ordering = ["name"]


class Exam(models.Model):

    name = models.CharField(max_length=100)

    exam_type = models.ForeignKey(
        ExamType,
        on_delete=models.PROTECT,
        related_name="exams"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="exams"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="exams"
    )

    academic_year = models.CharField(
        max_length=20
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):

        if self.semester.course_id != self.course_id:
            raise ValidationError(
                "Selected semester does not belong to selected course."
            )

        if self.end_date < self.start_date:
            raise ValidationError(
                "End date cannot be before start date."
            )

    def __str__(self):
        return f"{self.name} - {self.course.name} - Semester {self.semester.semester_number}"

    class Meta:
        ordering = ["-start_date"]


class ExamSchedule(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="exam_schedules"
    )

    exam_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    room = models.CharField(
        max_length=50,
        blank=True
    )

    max_marks = models.PositiveIntegerField(
        default=100
    )

    pass_marks = models.PositiveIntegerField(
        default=40
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def clean(self):

        # Subject ka semester aur exam semester same hona chahiye
        if self.subject.semester_id != self.exam.semester_id:
            raise ValidationError(
                "Selected subject does not belong to the exam semester."
            )

        # Start time end time se pehle hona chahiye
        if self.end_time <= self.start_time:
            raise ValidationError(
                "End time must be after start time."
            )

        # Pass marks max marks se zyada nahi ho sakte
        if self.pass_marks > self.max_marks:
            raise ValidationError(
                "Pass marks cannot be greater than maximum marks."
            )

    def __str__(self):
        return f"{self.exam.name} - {self.subject.name}"

    class Meta:
        ordering = ["exam_date", "start_time"]

        constraints = [
            models.UniqueConstraint(
                fields=["exam", "subject"],
                name="unique_subject_per_exam"
            )
        ]

class StudentMark(models.Model):

    ATTENDANCE_CHOICES = (
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
    )

    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name="student_marks"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="student_marks"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="exam_marks"
    )

    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    attendance = models.CharField(
        max_length=20,
        choices=ATTENDANCE_CHOICES,
        default="PRESENT"
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def clean(self):

        if self.exam_schedule_id:
            self.subject = self.exam_schedule.subject

        max_marks = self.exam_schedule.max_marks if self.exam_schedule_id else 0

        if self.subject_id and self.exam_schedule_id:
            if self.subject_id != self.exam_schedule.subject_id:
                raise ValidationError(
                    "Selected subject does not match the exam schedule subject."
                )

        if self.marks_obtained < 0:
            raise ValidationError(
                "Marks cannot be negative."
            )

        if self.marks_obtained > max_marks:
            raise ValidationError(
                f"Marks cannot be greater than {max_marks}."
            )

        # Student ka course/semester exam ke course/semester se match hona chahiye
        if self.student.course_id != self.exam_schedule.exam.course_id:
            raise ValidationError(
                "Student does not belong to this course."
            )

        if self.student.semester_id != self.exam_schedule.exam.semester_id:
            raise ValidationError(
                "Student does not belong to this semester."
            )

        # Absent student ke marks normally 0 hone chahiye
        if self.attendance == "ABSENT":
            self.marks_obtained = 0

    def __str__(self):
        subject_name = self.subject.name if self.subject_id else self.exam_schedule.subject.name
        return (
            f"{self.student.student_id} - {subject_name}"
        )

    class Meta:
        ordering = ["student__student_id"]

        constraints = [
            models.UniqueConstraint(
                fields=["exam_schedule", "student"],
                name="unique_student_mark_per_schedule"
            )
        ]

class ExamResult(models.Model):

    RESULT_STATUS_CHOICES = (
        ("PASS", "Pass"),
        ("FAIL", "Fail"),
    )

    GRADE_CHOICES = (
        ("A+", "A+"),
        ("A", "A"),
        ("B+", "B+"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("F", "F"),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="results"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="exam_results"
    )

    total_marks = models.PositiveIntegerField(
        default=0
    )

    obtained_marks = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    grade = models.CharField(
        max_length=5,
        choices=GRADE_CHOICES,
        default="F"
    )

    status = models.CharField(
        max_length=10,
        choices=RESULT_STATUS_CHOICES,
        default="FAIL"
    )

    published = models.BooleanField(
        default=False
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student.student_id} - {self.exam.name}"

    class Meta:
        ordering = ["student__student_id"]

        constraints = [
            models.UniqueConstraint(
                fields=["exam", "student"],
                name="unique_result_per_exam_student"
            )
        ]