from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)
from django.utils import timezone

from .forms import AdmissionForm
from .models import Admission


def admission_list(request):

    admissions = Admission.objects.select_related(
        'course'
    ).all()

    return render(
        request,
        'admissions/admission_list.html',
        {
            'admissions': admissions
        }
    )


def admission_create(request):

    if request.method == 'POST':

        form = AdmissionForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            admission = form.save()

            messages.success(
                request,
                'Admission application submitted successfully.'
            )

            return redirect(
                'admission_detail',
                pk=admission.pk
            )

    else:

        form = AdmissionForm()

    return render(
        request,
        'admissions/admission_form.html',
        {
            'form': form,
            'title': 'Admission Form'
        }
    )


def admission_detail(request, pk):

    admission = get_object_or_404(
        Admission,
        pk=pk
    )

    return render(
        request,
        'admissions/admission_detail.html',
        {
            'admission': admission
        }
    )

def admission_review(request, pk):

    admission = get_object_or_404(
        Admission,
        pk=pk
    )

    if request.method == 'POST':

        status = request.POST.get('status')

        rejection_reason = request.POST.get(
            'rejection_reason',
            ''
        )

        valid_statuses = [
            'PENDING',
            'UNDER_REVIEW',
            'APPROVED',
            'REJECTED',
            'CONFIRMED',
        ]

        if status not in valid_statuses:

            messages.error(
                request,
                'Invalid admission status.'
            )

            return redirect(
                'admission_review',
                pk=pk
            )

        admission.status = status

        if status == 'REJECTED':

            admission.rejection_reason = (
                rejection_reason
            )

        else:

            admission.rejection_reason = ''

        admission.reviewed_at = timezone.now()

        admission.save()

        messages.success(
            request,
            'Admission status updated successfully.'
        )

        return redirect(
            'admission_detail',
            pk=pk
        )

    return render(
        request,
        'admissions/admission_review.html',
        {
            'admission': admission
        }
    )
