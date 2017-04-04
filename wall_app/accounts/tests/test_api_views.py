from django.core.urlresolvers import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import SiteUser


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

    def test_user_can_register(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SiteUser.objects.count(), 1)
        self.assertEqual(SiteUser.objects.get().user.username,
                         self.data['username'])

    def test_with_mismatched_password(self):
        self.data['password2'] = 'password2'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_register_with_username_less_than_5(self):
        self.data['username'] = 'user'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
