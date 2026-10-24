from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from academics.models import Course, Semester
from students.models import Student


class FeeStructure(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="fee_structures"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="fee_structures"
    )

    academic_year = models.CharField(
        max_length=20
    )

    tuition_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    exam_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    library_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    hostel_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    other_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["course", "semester"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "semester", "academic_year"],
                name="unique_course_semester_academic_year"
            )
        ]

    def __str__(self):
        return f"{self.course.name} - {self.semester.display_name} - {self.academic_year}"

    @property
    def total_fee(self):
        return (
            self.tuition_fee
            + self.exam_fee
            + self.library_fee
            + self.hostel_fee
            + self.other_fee
        )

    def clean(self):
        if self.semester.course_id != self.course_id:
            raise ValidationError(
                "Selected semester does not belong to selected course."
            )

class StudentFee(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PARTIAL", "Partial"),
        ("PAID", "Paid"),
        ("OVERDUE", "Overdue"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="fees"
    )

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name="student_fees"
    )

    due_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.student_id} - {self.total_amount}"

    @property
    def balance_amount(self):
        return self.total_amount - self.paid_amount

    def update_status(self):

        if self.paid_amount <= 0:
            self.status = "PENDING"

        elif self.paid_amount < self.total_amount:
            self.status = "PARTIAL"

        else:
            self.status = "PAID"

    def clean(self):

        # StudentFeeForm calculates total_amount from the selected structure
        # after ModelForm validation, so it may be None during clean().
        if self.total_amount is not None and self.total_amount < 0:
            raise ValidationError(
                "Total amount cannot be negative."
            )

        if self.paid_amount is not None and self.paid_amount < 0:
            raise ValidationError(
                "Paid amount cannot be negative."
            )

        if (
            self.paid_amount is not None
            and self.total_amount is not None
            and self.paid_amount > self.total_amount
        ):
            raise ValidationError(
                "Paid amount cannot be greater than total amount."
            )

    def save(self, *args, **kwargs):

        self.update_status()

        super().save(*args, **kwargs)


class Payment(models.Model):

    PAYMENT_MODE_CHOICES = (
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("CARD", "Card"),
        ("NET_BANKING", "Net Banking"),
    )

    STATUS_CHOICES = (
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    )

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SUCCESS"
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.receipt_number} - ₹{self.amount}"

    def clean(self):

        if self.amount <= 0:
            raise ValidationError(
                "Payment amount must be greater than zero."
            )

        if self.student_fee_id:

            remaining = self.student_fee.balance_amount

            # Existing payment ko edit karte time
            # uski current amount ko remaining calculation se adjust karna hoga.
            if self.pk:
                old_payment = Payment.objects.get(pk=self.pk)

                if old_payment.student_fee_id == self.student_fee_id:
                    remaining += old_payment.amount

            if self.amount > remaining:
                raise ValidationError(
                    f"Payment cannot exceed remaining balance of ₹{remaining}."
                )

    def save(self, *args, **kwargs):

        if not self.receipt_number:

            last_payment = Payment.objects.order_by("-id").first()

            if last_payment:
                next_number = last_payment.id + 1
            else:
                next_number = 1

            year = timezone.now().year

            self.receipt_number = (
                f"REC{year}{next_number:06d}"
            )

        super().save(*args, **kwargs)
