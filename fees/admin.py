from django.contrib import admin

from .models import FeeStructure, StudentFee, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "semester",
        "academic_year",
        "tuition_fee",
        "exam_fee",
        "library_fee",
        "hostel_fee",
        "other_fee",
        "is_active",
    )

    list_filter = (
        "course",
        "semester",
        "academic_year",
        "is_active",
    )

    search_fields = (
        "course__name",
        "course__code",
        "academic_year",
    )


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "fee_structure",
        "total_amount",
        "paid_amount",
        "balance_display",
        "status",
        "due_date",
    )

    list_filter = (
        "status",
        "due_date",
        "fee_structure__course",
    )

    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
    )

    readonly_fields = (
        "paid_amount",
        "status",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Balance")
    def balance_display(self, obj):
        return obj.balance_amount


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "receipt_number",
        "student_name",
        "amount",
        "payment_mode",
        "status",
        "payment_date",
    )

    list_filter = (
        "payment_mode",
        "status",
        "payment_date",
    )

    search_fields = (
        "receipt_number",
        "student_fee__student__student_id",
        "student_fee__student__first_name",
        "transaction_id",
    )

    readonly_fields = (
        "receipt_number",
        "payment_date",
        "created_at",
    )

    @admin.display(description="Student")
    def student_name(self, obj):
        student = obj.student_fee.student
        return f"{student.first_name} {student.last_name}"