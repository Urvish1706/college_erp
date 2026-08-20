from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="OldPassword123!",
            first_name="Reset",
            last_name="Tester",
        )

    def test_01_login_page_contains_forgot_password_link(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("password_reset"))

    def test_02_password_reset_form_page_loads(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_form.html")

    def test_03_password_reset_post_sends_email(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "resetuser@example.com"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_done.html")
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertIn("resetuser@example.com", email.to)
        self.assertIn("Password Reset Request", email.subject)

    def test_04_password_reset_confirm_page_valid_and_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        # Valid token test (follows 302 redirect to set-password token session endpoint)
        valid_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        response_valid = self.client.get(valid_url, follow=True)
        self.assertEqual(response_valid.status_code, 200)
        self.assertTrue(response_valid.context["validlink"])

        # Invalid token test
        invalid_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": "invalid-token"})
        response_invalid = self.client.get(invalid_url, follow=True)
        self.assertEqual(response_invalid.status_code, 200)
        self.assertFalse(response_invalid.context["validlink"])

    def test_05_password_reset_confirm_successful_password_change(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        confirm_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})

        # Step 1: GET reset link to establish session token
        get_res = self.client.get(confirm_url, follow=True)
        self.assertEqual(get_res.status_code, 200)
        self.assertTrue(get_res.context["validlink"])

        new_pass = "NewSecurePassword456!"
        response = self.client.post(
            get_res.request["PATH_INFO"],
            {
                "new_password1": new_pass,
                "new_password2": new_pass,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_complete.html")

        # Verify old password fails
        login_old = self.client.login(username="resetuser", password="OldPassword123!")
        self.assertFalse(login_old)

        # Verify new password succeeds
        login_new = self.client.login(username="resetuser", password=new_pass)
        self.assertTrue(login_new)

