from django.urls import reverse_lazy
from rest_framework import status
import mock

from core.models import Message
from core.tests.http_header import APIHeaderAuthorization


class MessageListTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(MessageListTestSuite, cls).setUpClass()
        cls.url = reverse_lazy('message-list')

    def test_get_all_messages(self):
        messages = ('Hello World!!!', 'Hello TSL!!!', 'Welcome to TSL!!!')
        self.create_message_objects(self.profile, messages)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(messages))
        for index, message in enumerate(response.data['results']):
            self.assertEqual(message['content'], messages[index])

    def test_post_new_message(self):
        message = {'content': 'Hello World!'}
        response = self.client.post(self.url, data=message)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Message.objects.filter(content=message['content']).exists()
        )

    @mock.patch('core.pagination.StandardResultsSetPagination.page_size')
    def test_messages_respons_are_paginated(self, mocked_page_size):
        messages = ('Hello World!!!', 'Hello TSL!!!', 'Welcome to TSL!!!')
        mocked_page_size.return_value = 1
        self.create_message_objects(self.profile, messages)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']),
            mocked_page_size.return_value
        )
        self.assertEqual(response.data['count'], len(messages))
        self.assertTrue(response.data['next'])

    @staticmethod
    def create_message_objects(profile, messages):
        for message in messages:
            Message.objects.create(content=message, owner=profile)


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
