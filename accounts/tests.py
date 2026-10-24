from django.test import TestCase

from .forms import RegistrationForm


class ReporterRoleRegistrationTests(TestCase):
    def test_public_registration_offers_reporter_role_but_not_admin(self):
        choices = dict(RegistrationForm().fields["role"].choices)

        self.assertIn("REPORTER", choices)
        self.assertNotIn("ADMIN", choices)
