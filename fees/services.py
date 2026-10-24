from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Payment, StudentFee


@transaction.atomic
def create_payment(
    student_fee_id,
    amount,
    payment_mode,
    transaction_id="",
    remarks=""
):

    student_fee = (
        StudentFee.objects
        .select_for_update()
        .get(id=student_fee_id)
    )

    if amount <= 0:
        raise ValidationError(
            "Payment amount must be greater than zero."
        )

    if amount > student_fee.balance_amount:
        raise ValidationError(
            "Payment cannot exceed remaining balance."
        )

    payment = Payment(
        student_fee=student_fee,
        amount=amount,
        payment_mode=payment_mode,
        transaction_id=transaction_id,
        remarks=remarks,
        status="SUCCESS"
    )

    payment.full_clean()
    payment.save()

    student_fee.paid_amount += amount
    student_fee.update_status()
    student_fee.save(
        update_fields=[
            "paid_amount",
            "status",
            "updated_at"
        ]
    )

    return payment