from django.test import override_settings
from django.urls import reverse_lazy
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import mock
from rest_framework import status
from rest_framework.test import APITestCase

from factories.factories import (
    PROFILE_DATA, USER_DATA, ProfileFactory, UserFactory
)

from accounts.models import Profile
from accounts.tokens import account_activation_token
from accounts.views import RegistrationView


class BaseTestCase(APITestCase):
    user_details = {
        'username': 'john_doe',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john_doe@wall.com',
        'password': 'notsecret',
    }
    profile_details = {
        'about': 'Unknown Soldier',
        'profile_pic': 'http://unknown-domain.com/does-not-exit.jpg'
    }


class RegisterTestSuite(APITestCase):
    def setUp(self):
        super(RegisterTestSuite, self).setUp()
        self.data = USER_DATA.copy()
        self.data.update(PROFILE_DATA)
        passwords = {
            'password1': USER_DATA['password'],
            'password2': USER_DATA['password'],
        }
        self.data.update(passwords)
        self.data.pop('password')
        self.url = reverse_lazy('user-registration')

    @mock.patch.object(
        RegistrationView,
        'send_mail',
        autospec=True,
        return_value=None
    )
    def test_user_can_register(self, mock_send_mail):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get().user.username,
                         self.data['username'])
        self.assertTrue(mock_send_mail.called)

    def test_with_mismatched_password(self):
        self.data['password2'] = 'password2'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_register_with_username_less_than_5(self):
        self.data['username'] = 'user'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('sendgrid.SendGridAPIClient')
    def test_send_mail_calls_send_mail(self, mock_sendgrid_client):
        self.client.post(self.url, self.data, format='json')

        profile = Profile.objects.get(user__username='john_doe')
        uidb64 = urlsafe_base64_encode(force_bytes(profile.user.pk))
        token = account_activation_token.make_token(profile.user)
        url = reverse_lazy('activate',
                           kwargs={'uidb64': uidb64, 'token': token})
        expected_link_url = '<a href="http://testserver{url}"'.format(url=url)

        email_content = mock_sendgrid_client.mock_calls[1][2][
            'request_body']['content'][0]['value']
        self.assertIn(self.data['first_name'], email_content)
        self.assertIn(expected_link_url, email_content)


class ActivationViewTestSuite(APITestCase):
    def setUp(self):
        user = UserFactory(is_active=False)
        self.profile = ProfileFactory(user=user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.profile.user.pk))
        token = account_activation_token.make_token(self.profile.user)
        self.url = reverse_lazy('activate',
                                kwargs={'uidb64': uidb64, 'token': token})

    def test_redirect_to_success_url_if_user_found(self):
        self.assertFalse(self.profile.user.is_active)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            'http://localhost:3000/login?status=success',
            fetch_redirect_response=False
        )
        profile = Profile.objects.get(id=self.profile.id)
        self.assertTrue(profile.user.is_active)
        self.assertTrue(profile.email_confirmed)

    @override_settings(FRONTEND_URL='http://wallie.herokuapp.com')
    def test_success_url_contains_FRONTEND_URL_in_settings(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            'http://wallie.herokuapp.com/login?status=success',
            fetch_redirect_response=False
        )
        profile = Profile.objects.get(id=self.profile.id)
        self.assertTrue(profile.user.is_active)
        self.assertTrue(profile.email_confirmed)

    def test_returns_failure_url_if_user_does_not_exist(self):
        self.profile.user.delete()
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            'http://localhost:3000/login?status=failed',
            fetch_redirect_response=False
        )

    def test_returns_failure_url_when_token_and_user_mismatch(self):
        user = UserFactory(username='jane_doe', is_active=False)
        profile = ProfileFactory(user=user)

        uidb64 = urlsafe_base64_encode(force_bytes(self.profile.user.pk))
        token = account_activation_token.make_token(profile.user)
        url = reverse_lazy('activate',
                           kwargs={'uidb64': uidb64, 'token': token})

        response = self.client.get(url)
        self.assertRedirects(
            response,
            'http://localhost:3000/login?status=failed',
            fetch_redirect_response=False
        )
        self.assertFalse(user.is_active)
        self.assertFalse(profile.email_confirmed)
        self.assertFalse(self.profile.user.is_active)
        self.assertFalse(self.profile.email_confirmed)

    def test_returns_failure_url_for_random_token_and_uidb64_values(self):
        uidb64 = urlsafe_base64_encode(force_bytes('lj9\_0ONOVD9239-LSANDA91'))
        token = six.text_type('1212abdSDBD-023KSDFnkdff')
        url = reverse_lazy('activate',
                           kwargs={'uidb64': uidb64, 'token': token})

        response = self.client.get(url)
        self.assertRedirects(
            response,
            'http://localhost:3000/login?status=failed',
            fetch_redirect_response=False
        )
        self.assertFalse(self.profile.user.is_active)
        self.assertFalse(self.profile.email_confirmed)


class LoginTestSuite(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(LoginTestSuite, cls).setUpClass()
        ProfileFactory()
        cls.creds = {
            'username': USER_DATA['username'],
            'password': USER_DATA['password'],
        }

    def test_user_can_login(self):
        response = self.client.login(
            username=self.creds['username'],
            password=self.creds['password']
        )
        self.assertEqual(response, True)

    def test_login_endpoint_returns_token(self):
        url = reverse_lazy('user-login')
        response = self.client.post(url, self.creds, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.json())


class ProfileEndpointTestSuite(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(ProfileEndpointTestSuite, cls).setUpClass()
        ProfileFactory()
        cls.url = reverse_lazy('profile')

    def test_authenticated_user_can_retrieve_his_profile_details(self):
        self.client.login(
            username=USER_DATA['username'],
            password=USER_DATA['password']
        )
        response = self.client.get(self.url)
        user_info_without_password = {
            k: v for k, v in USER_DATA.items() if k != 'password'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user']['num_posts'], 0)
        del response.json()['user']['num_posts']
        self.assertEqual(response.json()['user'], user_info_without_password)
        self.assertEqual(response.json()['about'],
                         self.profile_details['about'])

    def test_unauthenticated_user_is_forbidden(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
