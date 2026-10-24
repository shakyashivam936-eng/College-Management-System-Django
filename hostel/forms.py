from decimal import Decimal

from django import forms

from .models import (
    Bed,
    Hostel,
    HostelAllocation,
    HostelFee,
    Room,
    HostelFeePayment,
)


class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = (
            "name",
            "hostel_type",
            "address",
            "warden_name",
            "warden_phone",
            "total_floors",
            "is_active",
        )
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = (
            "hostel",
            "room_number",
            "floor_number",
            "room_type",
            "capacity",
            "monthly_fee",
            "is_active",
        )


class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ("room", "bed_number", "is_active")


class HostelAllocationForm(forms.ModelForm):
    class Meta:
        model = HostelAllocation
        fields = (
            "student",
            "bed",
            "allocation_date",
            "leaving_date",
            "remarks",
        )
        widgets = {
            "allocation_date": forms.DateInput(attrs={"type": "date"}),
            "leaving_date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = self.fields["student"].queryset.filter(
            is_active=True
        )
        self.fields["bed"].queryset = self.fields["bed"].queryset.filter(
            is_active=True,
            is_occupied=False,
            room__is_active=True,
            room__hostel__is_active=True,
        ).select_related("room", "room__hostel")


class HostelFeeForm(forms.ModelForm):
    class Meta:
        model = HostelFee
        fields = ("allocation", "month", "amount", "paid_amount", "due_date")
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class HostelFeePaymentForm(forms.ModelForm):

    class Meta:
        model = HostelFeePayment

        fields = [
            "amount",
            "payment_mode",
            "transaction_id",
            "remarks",
        ]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "1",
                }
            ),
            "transaction_id": forms.TextInput(
                attrs={
                    "placeholder": "UPI/Bank Transaction ID"
                }
            ),
            "remarks": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),
        }
