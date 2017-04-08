from django.urls import reverse_lazy
from rest_framework import status
import mock

from core.models import Post
from core.tests.http_header import APIHeaderAuthorization


class PostListTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(PostListTestSuite, cls).setUpClass()
        cls.url = reverse_lazy('message-list')

    def test_get_all_posts(self):
        posts = ('Hello World!!!', 'Hello TSL!!!', 'Welcome to TSL!!!')
        self.create_message_objects(self.profile, posts)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(posts))
        for index, message in enumerate(response.data['results']):
            self.assertEqual(message['content'], posts[index])

    def test_post_new_message(self):
        message = {'content': 'Hello World!'}
        response = self.client.post(self.url, data=message)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Post.objects.filter(content=message['content']).exists()
        )

    @mock.patch('core.pagination.StandardResultsSetPagination.page_size')
    def test_posts_respons_are_paginated(self, mocked_page_size):
        posts = ('Hello World!!!', 'Hello TSL!!!', 'Welcome to TSL!!!')
        mocked_page_size.return_value = 1
        self.create_message_objects(self.profile, posts)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']),
            mocked_page_size.return_value
        )
        self.assertEqual(response.data['count'], len(posts))
        self.assertTrue(response.data['next'])

    @staticmethod
    def create_message_objects(profile, posts):
        for message in posts:
            Post.objects.create(content=post, owner=profile)


class PostDetailTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(PostDetailTestSuite, cls).setUpClass()
        cls.CONTENT = 'content'
        cls.OWNER = 'owner'

    def setUp(self):
        super(PostDetailTestSuite, self).setUp()
        self.data = {self.CONTENT: 'Hello World!!!', self.OWNER: self.profile}
        self.post = Post.objects.create(**self.data)
        self.url = reverse_lazy(
            'post-detail',
            kwargs={'pk': self.post.id}
        )

    def test_retrieve_single_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.CONTENT], self.post.content)

    def test_update_post(self):
        data = {self.CONTENT: self.data[self.CONTENT]}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.CONTENT], data[self.CONTENT])

    def test_delete_post(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(
            content=self.data[self.CONTENT]).exists())
