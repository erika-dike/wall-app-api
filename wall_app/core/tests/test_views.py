from django.urls import reverse_lazy
from rest_framework import status

from core.models import Message
from core.tests.http_header import APIHeaderAuthorization


class MessageListTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(MessageListTestSuite, cls).setUpClass()
        cls.url = reverse_lazy('message-list')

    def test_get_all_messages(self):
        messages = ('Hello World!!!', 'Hello TSL!!!', 'Welcome to TSL!!!')
        Message.objects.create(content=messages[0], owner=self.profile)
        Message.objects.create(content=messages[1], owner=self.profile)
        Message.objects.create(content=messages[2], owner=self.profile)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for index, message in enumerate(response.data):
            self.assertEqual(message['content'], messages[index])

    def test_post_new_message(self):
        message = {'content': 'Hello World!'}
        response = self.client.post(self.url, data=message)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Message.objects.filter(content=message['content']).exists()
        )


class MessageDetailTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(MessageDetailTestSuite, cls).setUpClass()
        cls.CONTENT = 'content'
        cls.OWNER = 'owner'

    def setUp(self):
        super(MessageDetailTestSuite, self).setUp()
        self.data = {self.CONTENT: 'Hello World!!!', self.OWNER: self.profile}
        self.message = Message.objects.create(**self.data)
        self.url = reverse_lazy(
            'message-detail',
            kwargs={'pk': self.message.id}
        )

    def test_retrieve_single_message(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.CONTENT], self.message.content)

    def test_update_message(self):
        data = {self.CONTENT: self.data[self.CONTENT]}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.CONTENT], data[self.CONTENT])

    def test_delete_message(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(
            content=self.data[self.CONTENT]).exists())
