from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from .forms import IssueReportForm, IssueReportUpdateForm
from .models import IssueReport
from students.models import Student
from academics.models import Faculty, Course
from admissions.models import Admission
from fees.models import Payment
from hostel.models import Bed
from exams.models import ExamResult


@login_required
def dashboard(request):
    # =========================================
    # BASIC STATISTICS
    # =========================================

    total_students = Student.objects.filter(
        is_active=True
    ).count()

    total_faculty = Faculty.objects.filter(
        is_active=True
    ).count()

    total_courses = Course.objects.filter(
        is_active=True
    ).count()

    total_admissions = Admission.objects.count()

    # =========================================
    # RECENT ADMISSIONS
    # =========================================

    recent_admissions = Admission.objects.select_related(
        "course"
    ).order_by("-submitted_at")[:5]

    # =========================================
    # FEE COLLECTION
    # =========================================

    total_fee_collection = Payment.objects.filter(
        status="SUCCESS"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # =========================================
    # MONTHLY FEE COLLECTION
    # =========================================

    monthly_fee_data = (
        Payment.objects
        .filter(status="SUCCESS")
        .annotate(month=TruncMonth("payment_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    fee_months = []
    fee_amounts = []

    for item in monthly_fee_data:
        fee_months.append(
            item["month"].strftime("%b %Y")
        )
        fee_amounts.append(
            float(item["total"])
        )

    # =========================================
    # ADMISSION STATISTICS
    # =========================================

    admission_data = (
        Admission.objects
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    admission_labels = []
    admission_counts = []

    for item in admission_data:
        admission_labels.append(
            item["status"]
        )
        admission_counts.append(
            item["total"]
        )

    # =========================================
    # HOSTEL OCCUPANCY
    # =========================================

    total_beds = Bed.objects.filter(
        is_active=True
    ).count()

    occupied_beds = Bed.objects.filter(
        is_active=True,
        is_occupied=True
    ).count()

    vacant_beds = total_beds - occupied_beds

    hostel_occupancy = 0

    if total_beds > 0:
        hostel_occupancy = round(
            (occupied_beds / total_beds) * 100,
            2
        )

    # =========================================
    # EXAM STATISTICS
    # =========================================

    total_results = ExamResult.objects.count()

    passed_students = ExamResult.objects.filter(
        status="PASS"
    ).count()

    failed_students = ExamResult.objects.filter(
        status="FAIL"
    ).count()

  
    # =========================================
    # CONTEXT
    # =========================================

    context = {

        # Statistics
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_courses": total_courses,
        "total_admissions": total_admissions,

        # Admissions
        "recent_admissions": recent_admissions,

        # Fees
        "total_fee_collection": total_fee_collection,
        "fee_months": fee_months,
        "fee_amounts": fee_amounts,

        # Admission chart
        "admission_labels": admission_labels,
        "admission_counts": admission_counts,

        # Hostel
        "total_beds": total_beds,
        "occupied_beds": occupied_beds,
        "vacant_beds": vacant_beds,
        "hostel_occupancy": hostel_occupancy,

        # Exams
        "total_results": total_results,
        "passed_students": passed_students,
        "failed_students": failed_students,

      
    }

    return render(
        request,
        "dashboard/index.html",
        context
    )


@login_required
def submit_issue_report(request):
    if request.user.role != "REPORTER" and not (
        request.user.role == "ADMIN" or request.user.is_staff or request.user.is_superuser
    ):
        return HttpResponseForbidden("Only reporter and admin accounts can submit issue reports.")

    if request.method == "POST":
        form = IssueReportForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()
            messages.success(request, "Your issue report was sent to the administration.")
            return redirect("dashboard:issue_mine")
    else:
        form = IssueReportForm()

    return render(request, "dashboard/issues/submit.html", {"form": form})


@login_required
def my_issue_reports(request):
    if request.user.role not in {"REPORTER", "ADMIN"} and not (
        request.user.is_staff or request.user.is_superuser
    ):
        return HttpResponseForbidden("Only reporter and admin accounts can view issue reports.")

    if request.user.role == "ADMIN" or request.user.is_staff or request.user.is_superuser:
        issues = IssueReport.objects.select_related("created_by").order_by("-created_at")
    else:
        issues = IssueReport.objects.filter(created_by=request.user).order_by("-created_at")

    return render(request, "dashboard/issues/mine.html", {"issues": issues})


@login_required
def manage_issue_reports(request):
    if request.user.role != "ADMIN" and not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Only admin accounts can manage issue reports.")

    issues = IssueReport.objects.select_related("created_by").order_by(
        "status", "-created_at"
    )
    return render(
        request,
        "dashboard/issues/manage.html",
        {"issues": issues, "status_choices": IssueReport.STATUS_CHOICES},
    )


@login_required
@require_POST
def update_issue_report(request, pk):
    if request.user.role != "ADMIN" and not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Only admin accounts can update issue reports.")

    issue = get_object_or_404(IssueReport, pk=pk)
    form = IssueReportUpdateForm(request.POST, instance=issue)
    if form.is_valid():
        form.save()
        messages.success(request, "Issue report status updated.")
    else:
        messages.error(request, "Could not update issue report. Check the selected status.")
    return redirect("dashboard:issue_manage")
