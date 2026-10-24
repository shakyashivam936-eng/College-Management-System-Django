from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django.template.loader import get_template


class HostelDashboardLinksTests(TestCase):
    def test_dashboard_links_to_hostel_pages_and_renders_without_records(self):
        user = get_user_model().objects.create_user(
            username="hostel-dashboard-user",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("hostel:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("hostel:hostel_list"))
        self.assertContains(response, reverse("hostel:room_list"))
        self.assertContains(response, reverse("hostel:bed_list"))
        self.assertContains(response, reverse("hostel:hostel_create"))
        self.assertContains(response, reverse("hostel:room_create"))
        self.assertContains(response, reverse("hostel:bed_create"))
        self.assertContains(response, reverse("hostel:allocation_create"))
        self.assertContains(response, 'id="hostel-fees"')
        self.assertContains(response, 'id="hostel-receipts"')

    def test_hostel_detail_payment_and_receipt_templates_compile(self):
        template_names = (
            "hostel/hostel_dashboard.html",
            "hostel/hostel_list.html",
            "hostel/hostel_form.html",
            "hostel/room_list.html",
            "hostel/room_form.html",
            "hostel/bed_list.html",
            "hostel/bed_form.html",
            "hostel/allocation_form.html",
            "hostel/allocation_detail.html",
            "hostel/hostel_fee_payment.html",
            "hostel/hostel_fee_receipt.html",
        )

        for template_name in template_names:
            with self.subTest(template=template_name):
                get_template(template_name)

        self.assertEqual(reverse("hostel:hostel_fee_payment", args=[1]), "/hostel/fees/1/payment/")
        self.assertEqual(reverse("hostel:hostel_fee_receipt", args=[1]), "/hostel/fees/payment/1/receipt/")
