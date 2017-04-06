from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.urls import reverse
import mock
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile
from accounts.views import RegistrationView


class RegisterTestSuite(APITestCase):
    def setUp(self):
        self.data = {
            'username': 'john_doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john_doe@wall.com',
            'password1': 'notsecret',
            'password2': 'notsecret',
            'about': 'Unknown Soldier',
            'profile_pic': 'http://unknown-domain.com/does-not-exit.jpg'
        }
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


class LoginTestSuite(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(LoginTestSuite, cls).setUpClass()
        cls.creds = {'username': 'john_doe', 'password': 'notsecret'}
        User.objects.create_user('john_doe', password='notsecret')

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


class ProfileEndpointTestSuite(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(ProfileEndpointTestSuite, cls).setUpClass()
        cls.user_details = {
            'username': 'john_doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john_doe@wall.com',
            'password': 'notsecret'
        }
        cls.profile_details = {'about': 'soldier'}
        user = User.objects.create_user(**cls.user_details)
        Profile.objects.create(user=user, **cls.profile_details)
        cls.url = reverse('profile')

    def test_authenticated_user_can_retrieve_his_profile_details(self):
        self.client.login(
            username=self.user_details['username'],
            password=self.user_details['password']
        )
        response = self.client.get(self.url)
        user_info_without_password = {
            k: v for k, v in self.user_details.items() if k != 'password'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user'], user_info_without_password)
        self.assertEqual(response.json()['about'],
                         self.profile_details['about'])

    def test_unauthenticated_user_is_forbidden(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
