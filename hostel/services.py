from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import date

from .models import (
    HostelFee,
    HostelFeePayment,
)


@transaction.atomic
def create_hostel_payment(
    hostel_fee_id,
    amount,
    payment_mode,
    transaction_id="",
    remarks=""
):

    hostel_fee = (
        HostelFee.objects
        .select_for_update()
        .get(pk=hostel_fee_id)
    )

    if amount <= 0:
        raise ValidationError(
            "Payment amount must be greater than zero."
        )

    if amount > hostel_fee.balance_amount:
        raise ValidationError(
            "Payment cannot exceed remaining balance."
        )

    payment = HostelFeePayment(
        hostel_fee=hostel_fee,
        amount=amount,
        payment_mode=payment_mode,
        transaction_id=transaction_id,
        remarks=remarks,
    )

    payment.save()

    hostel_fee.paid_amount += amount

    hostel_fee.update_status()

    hostel_fee.save(
        update_fields=[
            "paid_amount",
            "status",
            "updated_at",
        ]
    )

    return payment

from datetime import date


@transaction.atomic
def generate_monthly_hostel_fee(
    allocation_id,
    month,
    due_date
):

    allocation = HostelAllocation.objects.get(
        pk=allocation_id
    )

    existing_fee = HostelFee.objects.filter(
        allocation=allocation,
        month=month
    ).first()

    if existing_fee:
        return existing_fee

    amount = allocation.bed.room.monthly_fee

    hostel_fee = HostelFee.objects.create(
        allocation=allocation,
        month=month,
        amount=amount,
        due_date=due_date,
    )

    return hostel_fee