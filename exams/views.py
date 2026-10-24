from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from students.models import Student

from .forms import StudentMarkForm
from .models import Exam, StudentMark, ExamResult, ExamSchedule
from .services import generate_exam_result



def generate_result(request, exam_id, student_id):

    exam = get_object_or_404(
        Exam,
        id=exam_id
    )

    try:

        result = generate_exam_result(
            exam_id=exam.id,
            student_id=student_id
        )

        messages.success(
            request,
            "Student result generated successfully."
        )

        return redirect(
            "exams:result_detail",
            pk=result.pk
        )

    except ValueError as e:

        messages.error(
            request,
            str(e)
        )

        return redirect(
            "exams:exam_list"
        )


def exam_list(request):

    exams = Exam.objects.select_related(
        "exam_type",
        "course",
        "semester",
    ).order_by("-start_date")

    return render(
        request,
        "exams/exam_list.html",
        {
            "exams": exams,
        }
    )


def result_detail(request, pk):

    result = get_object_or_404(
        ExamResult.objects.select_related(
            "student",
            "exam",
            "exam__course",
            "exam__semester",
        ),
        pk=pk
    )

    marks = StudentMark.objects.filter(
        exam_schedule__exam=result.exam,
        student=result.student
    ).select_related(
        "exam_schedule",
        "exam_schedule__subject"
    )

    context = {
        "result": result,
        "marks": marks,
    }

    return render(
        request,
        "exams/result_detail.html",
        context
    )

def marksheet(request, result_id):

    result = get_object_or_404(
        ExamResult.objects.select_related(
            "student",
            "exam",
            "exam__course",
            "exam__semester",
        ),
        id=result_id
    )

    marks = StudentMark.objects.filter(
        exam_schedule__exam=result.exam,
        student=result.student
    ).select_related(
        "exam_schedule",
        "exam_schedule__subject",
    ).order_by(
        "exam_schedule__subject__name"
    )

    context = {
        "result": result,
        "marks": marks,
    }

    return render(
        request,
        "exams/marksheet.html",
        context
    )

def mark_entry(request, schedule_id):

    schedule = get_object_or_404(
        ExamSchedule.objects.select_related(
            "exam",
            "subject",
            "exam__course",
            "exam__semester",
        ),
        id=schedule_id
    )

    if request.method == "POST":

        form = StudentMarkForm(
            request.POST,
            exam_schedule=schedule
        )

        if form.is_valid():

            student = form.cleaned_data["student"]

            mark, created = StudentMark.objects.update_or_create(
                exam_schedule=schedule,
                student=student,
                defaults={
                    "subject": schedule.subject,
                    "marks_obtained":
                        form.cleaned_data["marks_obtained"],

                    "attendance":
                        form.cleaned_data["attendance"],

                    "remarks":
                        form.cleaned_data["remarks"],
                }
            )

            if created:

                messages.success(
                    request,
                    "Marks added successfully."
                )

            else:

                messages.success(
                    request,
                    "Marks updated successfully."
                )

            return redirect(
                "exams:mark_entry",
                schedule_id=schedule.id
            )

    else:

        form = StudentMarkForm(
            exam_schedule=schedule
        )

    marks = StudentMark.objects.filter(
        exam_schedule=schedule
    ).select_related("student")

    return render(
        request,
        "exams/mark_entry.html",
        {
            "schedule": schedule,
            "form": form,
            "marks": marks,
        }
    )

def exam_result_dashboard(request, exam_id):

    exam = get_object_or_404(
        Exam.objects.select_related(
            "course",
            "semester",
            "exam_type",
        ),
        id=exam_id
    )

    students = Student.objects.filter(
        course=exam.course,
        semester=exam.semester,
        is_active=True
    ).order_by(
        "student_id"
    )

    results = []

    for student in students:

        result = ExamResult.objects.filter(
            exam=exam,
            student=student
        ).first()

        marks = StudentMark.objects.filter(
            exam_schedule__exam=exam,
            student=student
        ).select_related(
            "exam_schedule__subject"
        )

        results.append({
            "student": student,
            "result": result,
            "marks": marks,
        })

    context = {
        "exam": exam,
        "results": results,
    }

    return render(
        request,
        "exams/exam_result_dashboard.html",
        context
    )

def generate_all_results(request, exam_id):

    exam = get_object_or_404(
        Exam,
        id=exam_id
    )

    students = Student.objects.filter(
        course=exam.course,
        semester=exam.semester,
        is_active=True
    )

    generated_count = 0
    skipped_count = 0

    for student in students:

        try:

            generate_exam_result(
                exam_id=exam.id,
                student_id=student.id
            )

            generated_count += 1

        except ValueError:

            skipped_count += 1

    messages.success(
        request,
        f"{generated_count} results generated successfully."
    )

    if skipped_count:
        messages.warning(
            request,
            f"{skipped_count} students skipped because marks were incomplete."
        )

    return redirect(
        "exams:exam_result_dashboard",
        exam_id=exam.id
    )
