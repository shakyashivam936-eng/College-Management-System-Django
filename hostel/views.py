from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    HostelForm,
    RoomForm,
    BedForm,
    HostelAllocationForm,
    HostelFeeForm,
    HostelFeePaymentForm,
)

from .models import (
    Hostel,
    Room,
    Bed,
    HostelAllocation,
    HostelFee,
    HostelFeePayment,
)
from .services import create_hostel_payment


@login_required
def hostel_dashboard(request):

    hostels = Hostel.objects.filter(
        is_active=True
    )

    rooms = Room.objects.filter(
        is_active=True
    )

    beds = Bed.objects.filter(
        is_active=True
    )

    allocations = HostelAllocation.objects.filter(
        status="ACTIVE"
    )

    pending_hostel_fees = HostelFee.objects.filter(
        status__in=["PENDING", "PARTIAL"]
    ).select_related(
        "allocation__student",
        "allocation__bed__room__hostel",
    ).order_by("due_date")[:8]

    recent_hostel_payments = HostelFeePayment.objects.select_related(
        "hostel_fee__allocation__student",
        "hostel_fee__allocation__bed__room__hostel",
    ).order_by("-payment_date")[:8]

    total_beds = beds.count()

    occupied_beds = beds.filter(
        is_occupied=True
    ).count()

    vacant_beds = beds.filter(
        is_occupied=False
    ).count()

    context = {
        "hostels": hostels,
        "rooms": rooms,
        "beds": beds,
        "allocations": allocations,
        "pending_hostel_fees": pending_hostel_fees,
        "recent_hostel_payments": recent_hostel_payments,
        "total_hostels": hostels.count(),
        "total_rooms": rooms.count(),
        "total_beds": total_beds,
        "occupied_beds": occupied_beds,
        "vacant_beds": vacant_beds,
    }

    return render(
        request,
        "hostel/hostel_dashboard.html",
        context
    )


@login_required
def hostel_list(request):

    hostels = Hostel.objects.all()

    return render(
        request,
        "hostel/hostel_list.html",
        {
            "hostels": hostels
        }
    )


@login_required
def hostel_create(request):

    if request.method == "POST":

        form = HostelForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Hostel created successfully."
            )

            return redirect(
                "hostel:hostel_list"
            )

    else:

        form = HostelForm()

    return render(
        request,
        "hostel/hostel_form.html",
        {
            "form": form
        }
    )


@login_required
def room_list(request):

    rooms = Room.objects.select_related(
        "hostel"
    ).all()

    return render(
        request,
        "hostel/room_list.html",
        {
            "rooms": rooms
        }
    )


@login_required
def room_create(request):

    if request.method == "POST":

        form = RoomForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Room created successfully."
            )

            return redirect(
                "hostel:room_list"
            )

    else:

        form = RoomForm()

    return render(
        request,
        "hostel/room_form.html",
        {
            "form": form
        }
    )


@login_required
def bed_list(request):

    beds = Bed.objects.select_related(
        "room",
        "room__hostel"
    ).all()

    return render(
        request,
        "hostel/bed_list.html",
        {
            "beds": beds
        }
    )


@login_required
def bed_create(request):

    if request.method == "POST":

        form = BedForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Bed created successfully."
            )

            return redirect(
                "hostel:bed_list"
            )

    else:

        form = BedForm()

    return render(
        request,
        "hostel/bed_form.html",
        {
            "form": form
        }
    )
@login_required
@transaction.atomic
def allocation_create(request):

    if request.method == "POST":

        form = HostelAllocationForm(request.POST)

        if form.is_valid():

            allocation = form.save(
                commit=False
            )

            bed = Bed.objects.select_for_update().get(
                pk=allocation.bed.pk
            )

            if bed.is_occupied:

                form.add_error(
                    "bed",
                    "This bed has already been allocated."
                )

            else:

                allocation.save()

                bed.is_occupied = True

                bed.save(
                    update_fields=[
                        "is_occupied"
                    ]
                )

                messages.success(
                    request,
                    "Bed allocated successfully."
                )

                return redirect(
                    "hostel:allocation_detail",
                    pk=allocation.pk
                )

    else:

        form = HostelAllocationForm()

    return render(
        request,
        "hostel/allocation_form.html",
        {
            "form": form
        }
    )

@login_required
def allocation_detail(request, pk):

    allocation = get_object_or_404(
        HostelAllocation.objects.select_related(
            "student",
            "bed",
            "bed__room",
            "bed__room__hostel",
        ),
        pk=pk
    )

    fees = allocation.hostel_fees.all()

    return render(
        request,
        "hostel/allocation_detail.html",
        {
            "allocation": allocation,
            "fees": fees,
        }
    )

@login_required
@transaction.atomic
def pay_hostel_fee(request, pk):

    fee = get_object_or_404(
        HostelFee.objects.select_for_update().select_related("allocation"),
        pk=pk,
    )

    if fee.balance_amount <= 0:
        messages.info(request, "This hostel fee has already been paid.")
        return redirect(
            "hostel:allocation_detail",
            pk=fee.allocation_id,
        )

    if request.method == "POST":
        form = HostelFeePaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            if amount > fee.balance_amount:
                form.add_error(
                    "amount",
                    "Payment cannot exceed the remaining balance.",
                )
            else:
                fee.paid_amount += amount
                fee.save(
                    update_fields=["paid_amount", "status", "updated_at"]
                )
                messages.success(request, "Hostel fee payment recorded.")
                return redirect(
                    "hostel:allocation_detail",
                    pk=fee.allocation_id,
                )
    else:
        form = HostelFeePaymentForm(
            initial={"amount": fee.balance_amount}
        )

    return render(
        request,
        "hostel/hostel_fee_payment.html",
        {"fee": fee, "form": form},
    )

@login_required
@require_POST
@transaction.atomic
def release_allocation(request, pk):

    allocation = get_object_or_404(
        HostelAllocation.objects.select_for_update(),
        pk=pk
    )

    if allocation.status == "ACTIVE":

        bed = Bed.objects.select_for_update().get(
            pk=allocation.bed.pk
        )

        allocation.status = "COMPLETED"

        from django.utils import timezone

        allocation.leaving_date = timezone.now().date()

        allocation.save(
            update_fields=[
                "status",
                "leaving_date",
                "updated_at",
            ]
        )

        bed.is_occupied = False

        bed.save(
            update_fields=[
                "is_occupied"
            ]
        )

        messages.success(
            request,
            "Student allocation released successfully."
        )

    return redirect(
        "hostel:allocation_detail",
        pk=allocation.pk
    )


@login_required
def hostel_fee_payment(request, pk):

    hostel_fee = get_object_or_404(
        HostelFee.objects.select_related(
            "allocation",
            "allocation__student",
        ),
        pk=pk
    )

    if hostel_fee.balance_amount <= 0:

        messages.info(
            request,
            "This hostel fee is already fully paid."
        )

        return redirect(
            "hostel:allocation_detail",
            pk=hostel_fee.allocation.pk
        )

    if request.method == "POST":

        form = HostelFeePaymentForm(request.POST)

        if form.is_valid():

            try:

                payment = create_hostel_payment(
                    hostel_fee_id=hostel_fee.id,
                    amount=form.cleaned_data["amount"],
                    payment_mode=form.cleaned_data["payment_mode"],
                    transaction_id=form.cleaned_data[
                        "transaction_id"
                    ],
                    remarks=form.cleaned_data["remarks"],
                )

                messages.success(
                    request,
                    f"Payment successful. "
                    f"Receipt: {payment.receipt_number}"
                )

                return redirect(
                    "hostel:hostel_fee_receipt",
                    pk=payment.pk
                )

            except Exception as e:

                form.add_error(
                    None,
                    str(e)
                )

    else:

        form = HostelFeePaymentForm()

    return render(
        request,
        "hostel/hostel_fee_payment.html",
        {
            "form": form,
            "hostel_fee": hostel_fee,
        }
    )


@login_required
def hostel_fee_receipt(request, pk):

    payment = get_object_or_404(
        HostelFeePayment.objects.select_related(
            "hostel_fee__allocation__student",
            "hostel_fee__allocation__bed__room__hostel",
        ),
        pk=pk,
    )

    return render(
        request,
        "hostel/hostel_fee_receipt.html",
        {"payment": payment},
    )
