from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="index"),
    path("issues/submit/", views.submit_issue_report, name="issue_submit"),
    path("issues/mine/", views.my_issue_reports, name="issue_mine"),
    path("issues/manage/", views.manage_issue_reports, name="issue_manage"),
    path("issues/<int:pk>/update/", views.update_issue_report, name="issue_update"),
]