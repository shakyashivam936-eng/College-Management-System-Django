from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, ExpressionWrapper, F, Sum
from django.db.models import DecimalField
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    FeeStructureForm,
    PaymentForm,
    StudentFeeForm,
)

from .models import (
    FeeStructure,
    Payment,
    StudentFee,
)

from .services import create_payment


@login_required
def fee_structure_list(request):

    fee_structures = FeeStructure.objects.select_related(
        "course",
        "semester"
    )
    student_fees = StudentFee.objects.select_related(
        "student",
        "fee_structure__course",
        "fee_structure__semester",
    )

    return render(
        request,
        "fees/fee_structure_list.html",
        {
            "fee_structures": fee_structures,
            "student_fees": student_fees,
        }
    )


@login_required
def fee_structure_create(request):

    if request.method == "POST":

        form = FeeStructureForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee structure created successfully."
            )

            return redirect(
                "fees:fee_structure_list"
            )

    else:

        form = FeeStructureForm()

    return render(
        request,
        "fees/fee_structure_form.html",
        {
            "form": form
        }
    )


@login_required
def student_fee_create(request):

    if request.method == "POST":

        form = StudentFeeForm(request.POST)

        if form.is_valid():

            student_fee = form.save()

            messages.success(
                request,
                "Fee assigned to student successfully."
            )

            return redirect(
                "fees:student_fee_detail",
                pk=student_fee.pk,
            )

    else:

        form = StudentFeeForm()

    return render(
        request,
        "fees/student_fee_form.html",
        {
            "form": form
        }
    )
@login_required
def student_fee_detail(request, pk):

    student_fee = get_object_or_404(
        StudentFee.objects.select_related(
            "student",
            "fee_structure",
            "fee_structure__course",
            "fee_structure__semester",
        ),
        pk=pk
    )

    payments = student_fee.payments.all().order_by(
        "-payment_date"
    )

    return render(
        request,
        "fees/student_fee_detail.html",
        {
            "student_fee": student_fee,
            "payments": payments,
        }
    )


@login_required
def make_payment(request, pk):

    student_fee = get_object_or_404(
        StudentFee,
        pk=pk
    )

    if student_fee.balance_amount <= 0:
        messages.info(
            request,
            "This fee has already been fully paid."
        )

        return redirect(
            "fees:student_fee_detail",
            pk=student_fee.pk
        )

    if request.method == "POST":

        form = PaymentForm(request.POST)

        if form.is_valid():

            try:

                payment = create_payment(
                    student_fee_id=student_fee.id,
                    amount=form.cleaned_data["amount"],
                    payment_mode=form.cleaned_data["payment_mode"],
                    transaction_id=form.cleaned_data["transaction_id"],
                    remarks=form.cleaned_data["remarks"],
                )

                messages.success(
                    request,
                    f"Payment successful. Receipt: {payment.receipt_number}"
                )

                return redirect(
                    "fees:payment_receipt",
                    pk=payment.pk
                )

            except Exception as e:

                form.add_error(
                    None,
                    str(e)
                )

    else:

        form = PaymentForm()

    return render(
        request,
        "fees/payment_form.html",
        {
            "form": form,
            "student_fee": student_fee,
        }
    )


@login_required
def payment_receipt(request, pk):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "student_fee",
            "student_fee__student",
            "student_fee__fee_structure",
            "student_fee__fee_structure__course",
            "student_fee__fee_structure__semester",
        ),
        pk=pk
    )

    return render(
        request,
        "fees/payment_receipt.html",
        {
            "payment": payment
        }
    )


@login_required
def fees_dashboard(request):

    # All student fee records
    student_fees = StudentFee.objects.select_related(
        'student',
        'fee_structure__course',
        'fee_structure__semester'
    ).annotate(
        outstanding_balance=ExpressionWrapper(
            F('total_amount') - F('paid_amount'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    # All payment records
    payments = Payment.objects.select_related(
        'student_fee__student',
        'student_fee__fee_structure__course',
        'student_fee__fee_structure__semester'
    )

    # Financial summary
    fee_summary = student_fees.aggregate(
        total_fees=Sum('total_amount'),
        total_paid=Sum('paid_amount'),
        total_due=Sum('outstanding_balance'),
        total_students=Count('student', distinct=True),
    )

    total_fees = fee_summary['total_fees'] or Decimal('0.00')
    total_paid = fee_summary['total_paid'] or Decimal('0.00')
    total_due = fee_summary['total_due'] or Decimal('0.00')
    total_students = fee_summary['total_students'] or 0

    # Payment statistics
    payment_summary = payments.aggregate(
        total_payments=Count('id'),
        total_collected=Sum('amount'),
    )

    total_payments = payment_summary['total_payments'] or 0
    total_collected = payment_summary['total_collected'] or Decimal('0.00')

    # Recent payments
    recent_payments = payments.order_by('-payment_date', '-id')[:8]

    # Students with pending fees
    pending_fees = student_fees.filter(
        outstanding_balance__gt=0
    ).order_by('-outstanding_balance')[:8]

    # Latest student fee accounts
    recent_student_fees = student_fees.order_by('-id')[:8]

    # Fee structures
    fee_structures = FeeStructure.objects.select_related(
        'course',
        'semester'
    ).order_by('-id')[:5]

    # Collection percentage
    if total_fees > 0:
        collection_percentage = min(
            round((total_paid / total_fees) * 100, 2),
            100
        )
    else:
        collection_percentage = 0

    context = {
        'total_fees': total_fees,
        'total_paid': total_paid,
        'total_due': total_due,
        'total_students': total_students,
        'total_payments': total_payments,
        'total_collected': total_collected,
        'collection_percentage': collection_percentage,
        'recent_payments': recent_payments,
        'pending_fees': pending_fees,
        'recent_student_fees': recent_student_fees,
        'fee_structures': fee_structures,
    }

    return render(request, 'fees/dashboard.html', context)
