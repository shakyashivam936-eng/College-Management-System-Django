from django.urls import path

from . import views


app_name = "exams"


urlpatterns = [

    path(
        "",
        views.exam_list,
        name="exam_list"
    ),

    path(
        "result/generate/<int:exam_id>/<int:student_id>/",
        views.generate_result,
        name="generate_result"
    ),

    path(
        "result/<int:pk>/",
        views.result_detail,
        name="result_detail"
    ),
    path(
    "marksheet/<int:result_id>/",
    views.marksheet,
    name="marksheet"
    ),
    path(
    "marks/entry/<int:schedule_id>/",
    views.mark_entry,
    name="mark_entry"
    ),
    path(
    "results/dashboard/<int:exam_id>/",
    views.exam_result_dashboard,
    name="exam_result_dashboard"
),
path(
    "results/generate-all/<int:exam_id>/",
    views.generate_all_results,
    name="generate_all_results"
),

]