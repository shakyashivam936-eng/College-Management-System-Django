from django.shortcuts import render
from .models import Course, Faculty


def faculty_list(request):
    faculty = Faculty.objects.select_related("user", "department").order_by("employee_id")
    return render(request, "academics/faculty_list.html", {"faculty_members": faculty})


def course_list(request):
    courses = Course.objects.select_related("department").order_by("code")
    return render(request, "academics/course_list.html", {"courses": courses})
