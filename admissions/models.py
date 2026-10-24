from django.db import models
from django.utils import timezone


class Admission(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CONFIRMED', 'Admission Confirmed'),
    )

    application_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    # Personal Information

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

    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15
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

    # Academic Information

    course = models.ForeignKey(
        'academics.Course',
        on_delete=models.PROTECT,
        related_name='admission_applications'
    )

    previous_school = models.CharField(
        max_length=200,
        blank=True
    )

    high_school_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    intermediate_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    passing_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    # Documents

    profile_photo = models.ImageField(
        upload_to='admissions/photos/',
        blank=True,
        null=True
    )

    high_school_marksheet = models.FileField(
        upload_to='admissions/documents/',
        blank=True,
        null=True
    )

    intermediate_marksheet = models.FileField(
        upload_to='admissions/documents/',
        blank=True,
        null=True
    )

    identity_proof = models.FileField(
        upload_to='admissions/documents/',
        blank=True,
        null=True
    )

    transfer_certificate = models.FileField(
        upload_to='admissions/documents/',
        blank=True,
        null=True
    )

    # Admission Status

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    rejection_reason = models.TextField(
        blank=True
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.application_number:

            year = timezone.now().year

            last_admission = Admission.objects.filter(
                application_number__startswith=f'ADM{year}'
            ).order_by('-id').first()

            if last_admission:

                last_number = int(
                    last_admission.application_number[-5:]
                )

                next_number = last_number + 1

            else:

                next_number = 1

            self.application_number = (
                f'ADM{year}{next_number:05d}'
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f'{self.application_number} - '
            f'{self.first_name} {self.last_name}'
        )
