from django.core.exceptions import ValidationError
from django.db import models

from students.models import Student


class Hostel(models.Model):

    HOSTEL_TYPE_CHOICES = (
        ("BOYS", "Boys Hostel"),
        ("GIRLS", "Girls Hostel"),
    )

    name = models.CharField(
        max_length=100
    )

    hostel_type = models.CharField(
        max_length=20,
        choices=HOSTEL_TYPE_CHOICES
    )

    address = models.TextField(
        blank=True
    )

    warden_name = models.CharField(
        max_length=100,
        blank=True
    )

    warden_phone = models.CharField(
        max_length=15,
        blank=True
    )

    total_floors = models.PositiveIntegerField(
        default=1
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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Room(models.Model):

    ROOM_TYPE_CHOICES = (
        ("SINGLE", "Single"),
        ("DOUBLE", "Double"),
        ("TRIPLE", "Triple"),
        ("FOUR", "Four Seater"),
    )

    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.PROTECT,
        related_name="rooms"
    )

    room_number = models.CharField(
        max_length=20
    )

    floor_number = models.PositiveIntegerField(
        default=1
    )

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES
    )

    capacity = models.PositiveIntegerField(
        default=1
    )

    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"

    @property
    def total_beds(self):
        return self.beds.count()

    @property
    def occupied_beds(self):
        return self.beds.filter(
            is_occupied=True
        ).count()

    @property
    def vacant_beds(self):
        return self.beds.filter(
            is_occupied=False,
            is_active=True
        ).count()

class Bed(models.Model):

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="beds"
    )

    bed_number = models.CharField(
        max_length=20
    )

    is_occupied = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["room", "bed_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["room", "bed_number"],
                name="unique_bed_per_room"
            )
        ]

    def __str__(self):
        return f"Room {self.room.room_number} - Bed {self.bed_number}"

class HostelAllocation(models.Model):

    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="hostel_allocations"
    )

    bed = models.ForeignKey(
        Bed,
        on_delete=models.PROTECT,
        related_name="allocations"
    )

    allocation_date = models.DateField()

    leaving_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
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

    class Meta:
        ordering = ["-allocation_date"]

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.bed}"
        )

    def clean(self):

        if self.bed_id and self.bed.is_occupied and not self.pk:
            raise ValidationError(
                "This bed is already occupied."
            )

        if not self.student_id:
            return

        active_allocation = HostelAllocation.objects.filter(
            student=self.student,
            status="ACTIVE"
        )

        if self.pk:
            active_allocation = active_allocation.exclude(
                pk=self.pk
            )

        if active_allocation.exists():
            raise ValidationError(
                "This student already has an active hostel allocation."
            )

class HostelFee(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PARTIAL", "Partial"),
        ("PAID", "Paid"),
    )

    allocation = models.ForeignKey(
        HostelAllocation,
        on_delete=models.PROTECT,
        related_name="hostel_fees"
    )

    month = models.DateField(
        help_text="Use first day of the month."
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    due_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-month"]

        constraints = [
            models.UniqueConstraint(
                fields=["allocation", "month"],
                name="unique_hostel_fee_per_month"
            )
        ]

    def __str__(self):
        return (
            f"{self.allocation.student.student_id} - "
            f"{self.month.strftime('%B %Y')}"
        )

    @property
    def balance_amount(self):
        return self.amount - self.paid_amount

    def update_status(self):

        if self.paid_amount <= 0:
            self.status = "PENDING"

        elif self.paid_amount < self.amount:
            self.status = "PARTIAL"

        else:
            self.status = "PAID"

    def clean(self):

        if self.amount is not None and self.amount < 0:
            raise ValidationError(
                "Hostel fee cannot be negative."
            )

        if self.paid_amount is not None and self.paid_amount < 0:
            raise ValidationError(
                "Paid amount cannot be negative."
            )

        if (
            self.paid_amount is not None
            and self.amount is not None
            and self.paid_amount > self.amount
        ):
            raise ValidationError(
                "Paid amount cannot exceed hostel fee."
            )

    def save(self, *args, **kwargs):

        self.update_status()

        super().save(*args, **kwargs)

class HostelFeePayment(models.Model):

    PAYMENT_MODE_CHOICES = (
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("CARD", "Card"),
        ("NET_BANKING", "Net Banking"),
    )

    hostel_fee = models.ForeignKey(
        HostelFee,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.receipt_number} - ₹{self.amount}"

    def save(self, *args, **kwargs):

        if not self.receipt_number:

            last_payment = (
                HostelFeePayment.objects
                .order_by("-id")
                .first()
            )

            next_number = (
                last_payment.id + 1
                if last_payment
                else 1
            )

            from django.utils import timezone

            year = timezone.now().year

            self.receipt_number = (
                f"HR{year}{next_number:06d}"
            )

        super().save(*args, **kwargs)