from django.db import models


class Department(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

class Course(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='courses'
    )

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    duration_years = models.PositiveIntegerField(
        default=3
    )

    total_semesters = models.PositiveIntegerField(
        default=6
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

class Semester(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='semesters'
    )

    semester_number = models.PositiveIntegerField()

    name = models.CharField(
        max_length=50
    )

    is_active = models.BooleanField(
        default=True
    )

    @property
    def display_name(self):
        return f"Semester {self.semester_number}"

    def __str__(self):
        return f"{self.course.code} - {self.display_name}"

    class Meta:
        ordering = ['course', 'semester_number']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'semester_number'],
                name='unique_course_semester'
            )
        ]

class Faculty(models.Model):

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='faculty_profile'
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='faculty_members'
    )

    qualification = models.CharField(
        max_length=150,
        blank=True
    )

    designation = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    joining_date = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"

class Subject(models.Model):

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='subjects'
    )

    name = models.CharField(
        max_length=150
    )

    code = models.CharField(
        max_length=30,
        unique=True
    )

    credits = models.PositiveIntegerField(
        default=4
    )

    max_marks = models.PositiveIntegerField(
        default=100
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects'
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


