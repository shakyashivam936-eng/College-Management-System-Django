from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from .models import ExamResult, StudentMark


def calculate_grade(percentage):

    percentage = Decimal(percentage)

    if percentage >= 90:
        return "A+"

    elif percentage >= 80:
        return "A"

    elif percentage >= 70:
        return "B+"

    elif percentage >= 60:
        return "B"

    elif percentage >= 50:
        return "C"

    elif percentage >= 40:
        return "D"

    return "F"


@transaction.atomic
def generate_exam_result(exam_id, student_id):

    marks = StudentMark.objects.filter(
        exam_schedule__exam_id=exam_id,
        student_id=student_id
    ).select_related(
        "exam_schedule"
    )

    if not marks.exists():
        raise ValueError(
            "No marks found for this student."
        )

    total_marks = 0
    obtained_marks = Decimal("0")

    has_failed_subject = False

    for mark in marks:

        total_marks += mark.exam_schedule.max_marks

        obtained_marks += mark.marks_obtained

        if mark.attendance == "ABSENT":
            has_failed_subject = True

        elif mark.marks_obtained < mark.exam_schedule.pass_marks:
            has_failed_subject = True

    if total_marks == 0:
        raise ValueError(
            "Total marks cannot be zero."
        )

    percentage = (
        obtained_marks / Decimal(total_marks)
    ) * Decimal("100")
    percentage = percentage.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    grade = calculate_grade(percentage)

    if has_failed_subject or grade == "F":
        status = "FAIL"
    else:
        status = "PASS"

    result, created = ExamResult.objects.update_or_create(
        exam_id=exam_id,
        student_id=student_id,
        defaults={
            "total_marks": total_marks,
            "obtained_marks": obtained_marks,
            "percentage": percentage,
            "grade": grade,
            "status": status,
        }
    )

    return result