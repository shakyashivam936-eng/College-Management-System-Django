from django.db import models

# Create your models here.
class Student(models.Model):

    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    student_id = models.CharField(
        max_length=30,
        unique=True
    )

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    father_name = models.CharField(
        max_length=150
    )

    mother_name = models.CharField(
        max_length=150
    )

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15
    )

    alternate_phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    course = models.ForeignKey(
        'academics.Course',
        on_delete=models.PROTECT,
        related_name='students'
    )

    semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.PROTECT,
        related_name='students'
    )

    admission_date = models.DateField()

    profile_photo = models.ImageField(
        upload_to='students/photos/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"