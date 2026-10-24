from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import IssueReport


class DashboardAccessTests(TestCase):
    def test_all_authenticated_roles_can_open_both_dashboards_directly(self):
        user_model = get_user_model()
        for role in ("ADMIN", "TEACHER", "STUDENT", "REPORTER"):
            with self.subTest(role=role):
                user = user_model.objects.create_user(
                    username=f"{role.lower()}-dashboard-user",
                    password="test-password",
                    role=role,
                )
                self.client.force_login(user)

                self.assertEqual(
                    self.client.get(reverse("dashboard:index")).status_code,
                    200,
                )
                self.assertEqual(
                    self.client.get(reverse("dashboard")).status_code,
                    200,
                )

    def test_both_dashboards_still_require_login(self):
        for url_name in ("dashboard:index", "dashboard"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response["Location"],
                    f"{reverse('login')}?next={reverse(url_name)}",
                )


class IssueReportWorkflowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.reporter = user_model.objects.create_user(
            username="reporter",
            password="test-password",
            role="REPORTER",
        )
        self.other_reporter = user_model.objects.create_user(
            username="other-reporter",
            password="test-password",
            role="REPORTER",
        )
        self.admin = user_model.objects.create_user(
            username="admin",
            password="test-password",
            role="ADMIN",
        )

    def test_reporter_can_submit_and_only_see_own_reports(self):
        self.client.force_login(self.reporter)
        response = self.client.post(
            reverse("dashboard:issue_submit"),
            {
                "category": "FEES",
                "title": "Incorrect fee balance",
                "description": "The fee balance is not updated after payment.",
            },
        )

        self.assertRedirects(response, reverse("dashboard:issue_mine"))
        issue = IssueReport.objects.get()
        self.assertEqual(issue.created_by, self.reporter)
        self.assertEqual(issue.status, "OPEN")

        IssueReport.objects.create(
            created_by=self.other_reporter,
            category="HOSTEL",
            title="Other user's report",
            description="Private report details.",
        )
        response = self.client.get(reverse("dashboard:issue_mine"))
        self.assertContains(response, "Incorrect fee balance")
        self.assertNotContains(response, "Other user's report")
        self.assertEqual(
            self.client.get(reverse("dashboard:issue_manage")).status_code,
            403,
        )

    def test_admin_can_review_and_update_report(self):
        issue = IssueReport.objects.create(
            created_by=self.reporter,
            category="ATTENDANCE",
            title="Attendance not recorded",
            description="The attendance page did not save the entry.",
        )
        self.client.force_login(self.admin)

        self.assertEqual(
            self.client.get(reverse("dashboard:issue_manage")).status_code,
            200,
        )
        response = self.client.post(
            reverse("dashboard:issue_update", args=[issue.pk]),
            {"status": "RESOLVED", "admin_note": "Fixed and verified."},
        )

        self.assertRedirects(response, reverse("dashboard:issue_manage"))
        issue.refresh_from_db()
        self.assertEqual(issue.status, "RESOLVED")
        self.assertEqual(issue.admin_note, "Fixed and verified.")
