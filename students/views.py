from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from .forms import StudentForm
from .models import Student


def student_list(request):

    students = Student.objects.select_related(
        'course',
        'semester'
    ).all()

    return render(
        request,
        'students/student_list.html',
        {
            'students': students
        }
    )


def student_create(request):

    if request.method == 'POST':

        form = StudentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Student created successfully.'
            )

            return redirect('student_list')

    else:

        form = StudentForm()

    return render(
        request,
        'students/student_form.html',
        {
            'form': form,
            'title': 'Add Student'
        }
    )


def student_detail(request, pk):

    student = get_object_or_404(
        Student,
        pk=pk
    )

    return render(
        request,
        'students/student_detail.html',
        {
            'student': student
        }
    )


def student_update(request, pk):

    student = get_object_or_404(
        Student,
        pk=pk
    )

    if request.method == 'POST':

        form = StudentForm(
            request.POST,
            request.FILES,
            instance=student
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Student updated successfully.'
            )

            return redirect(
                'student_detail',
                pk=student.pk
            )

    else:

        form = StudentForm(
            instance=student
        )

    return render(
        request,
        'students/student_form.html',
        {
            'form': form,
            'title': 'Edit Student'
        }
    )


def student_delete(request, pk):

    student = get_object_or_404(
        Student,
        pk=pk
    )

    if request.method == 'POST':

        student.delete()

        messages.success(
            request,
            'Student deleted successfully.'
        )

        return redirect(
            'student_list'
        )

    return render(
        request,
        'students/student_delete.html',
        {
            'student': student
        }
    )
