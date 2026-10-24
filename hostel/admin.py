from django.contrib import admin

from .models import (
    Hostel,
    Room,
    Bed,
    HostelAllocation,
    HostelFee,
    HostelFeePayment,
)


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "hostel_type",
        "warden_name",
        "warden_phone",
        "total_floors",
        "is_active",
    )

    list_filter = (
        "hostel_type",
        "is_active",
    )

    search_fields = (
        "name",
        "warden_name",
        "warden_phone",
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        "hostel",
        "room_number",
        "floor_number",
        "room_type",
        "capacity",
        "occupied_beds",
        "vacant_beds",
        "monthly_fee",
        "is_active",
    )

    list_filter = (
        "hostel",
        "room_type",
        "floor_number",
        "is_active",
    )

    search_fields = (
        "room_number",
        "hostel__name",
    )


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):

    list_display = (
        "room",
        "bed_number",
        "is_occupied",
        "is_active",
    )

    list_filter = (
        "is_occupied",
        "is_active",
        "room__hostel",
    )

    search_fields = (
        "bed_number",
        "room__room_number",
        "room__hostel__name",
    )


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "bed",
        "allocation_date",
        "leaving_date",
        "status",
    )

    list_filter = (
        "status",
        "allocation_date",
        "bed__room__hostel",
    )

    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "bed__room__room_number",
    )


@admin.register(HostelFee)
class HostelFeeAdmin(admin.ModelAdmin):

    list_display = (
        "allocation",
        "month",
        "amount",
        "paid_amount",
        "balance_amount",
        "status",
        "due_date",
    )

    list_filter = (
        "status",
        "month",
        "due_date",
    )

    search_fields = (
        "allocation__student__student_id",
        "allocation__student__first_name",
        "allocation__student__last_name",
    )

    readonly_fields = (
        "status",
    )

@admin.register(HostelFeePayment)
class HostelFeePaymentAdmin(admin.ModelAdmin):

    list_display = (
        "receipt_number",
        "student_name",
        "amount",
        "payment_mode",
        "payment_date",
    )

    list_filter = (
        "payment_mode",
        "payment_date",
    )

    search_fields = (
        "receipt_number",
        "transaction_id",
        "hostel_fee__allocation__student__student_id",
    )

    readonly_fields = (
        "receipt_number",
        "payment_date",
    )

    @admin.display(description="Student")
    def student_name(self, obj):

        student = (
            obj.hostel_fee
            .allocation
            .student
        )

        return (
            f"{student.first_name} "
            f"{student.last_name}"
        )