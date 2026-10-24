from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("faculty/", views.faculty_list, name="faculty_list"),
    path("courses/", views.course_list, name="course_list"),
]
