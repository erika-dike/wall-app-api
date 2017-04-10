from django.urls import reverse_lazy
from rest_framework import status
import mock

from core.models import Love, Post
from core.tests.http_header import APIHeaderAuthorization
from factories.factories import PostFactory, ProfileFactory, UserFactory


class PostListTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(PostListTestSuite, cls).setUpClass()
        cls.url = reverse_lazy('post-list')

    def test_get_all_posts(self):
        num_posts = 3
        posts = self.create_post_objects(self.profile, num_posts)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), num_posts)
        for index, post in enumerate(response.data['results']):
            self.assertEqual(post['content'], posts[index].content)

    def test_post_new_post(self):
        post = {'content': 'Hello World!'}
        response = self.client.post(self.url, data=post)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Post.objects.filter(content=post['content']).exists()
        )

    @mock.patch('core.pagination.StandardResultsSetPagination.page_size')
    def test_posts_response_are_paginated(self, mocked_page_size):
        mocked_page_size.return_value = 1
        num_posts = 3
        self.create_post_objects(self.profile, num_posts)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']),
            mocked_page_size.return_value
        )
        self.assertEqual(response.data['count'], num_posts)
        self.assertTrue(response.data['next'])

    @staticmethod
    def create_post_objects(profile, num_posts):
        posts = []
        for post in xrange(num_posts):
            posts.append(PostFactory(owner=profile))
        return posts


class PostDetailTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(PostDetailTestSuite, cls).setUpClass()
        cls.CONTENT = 'content'
        cls.OWNER = 'owner'

    def setUp(self):
        super(PostDetailTestSuite, self).setUp()
        self.post = PostFactory(owner=self.profile)
        self.url = reverse_lazy('post-detail', kwargs={'pk': self.post.id})

    def test_retrieve_single_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.CONTENT], self.post.content)

    def test_update_post(self):
        data = {self.CONTENT: 'Updated Post'}
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[self.CONTENT], data[self.CONTENT])

    def test_delete_post(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(
            content=self.post.content).exists())


class LoveCreateTestSuite(APIHeaderAuthorization):
    def setUp(self):
        super(LoveCreateTestSuite, self).setUp()
        self.post = PostFactory(owner=self.profile)
        self.data = {}

    def test_love_create_success(self):
        self.url = reverse_lazy(
            'love-create', kwargs={'post_id': self.post.id})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        love = Love.objects.filter(fan=self.profile, post=self.post)
        self.assertTrue(love.exists())

    def test_love_create_response(self):
        self.url = reverse_lazy(
            'love-create', kwargs={'post_id': self.post.id})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['num_loves'], 1)
        self.assertEqual(response.data['in_love'], True)

    def test_auth_user_can_love_anothers_post(self):
        user = UserFactory(username='new_user')
        profile = ProfileFactory(user=user, about='Modern Soldier')
        post = PostFactory(content='New Post', owner=profile)

        self.url = reverse_lazy(
            'love-create', kwargs={'post_id': post.id})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        love = Love.objects.filter(fan=self.profile, post=post)
        self.assertTrue(love.exists())


class LoveDeleteTestSuite(APIHeaderAuthorization):
    def setUp(self):
        super(LoveDeleteTestSuite, self).setUp()
        self.post = PostFactory(owner=self.profile)
        self.love = Love.objects.create(fan=self.profile, post=self.post)

    def test_delete_love_success(self):
        self.url = reverse_lazy(
            'love-delete', kwargs={'post_id': self.post.id})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        love = Love.objects.filter(fan=self.profile, post=self.post)
        self.assertFalse(love.exists())

    def test_love_create_response(self):
        self.url = reverse_lazy(
            'love-delete', kwargs={'post_id': self.post.id})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num_loves'], 0)
        self.assertEqual(response.data['in_love'], False)

    def test_auth_user_can_unlove_anothers_post(self):
        user = UserFactory(username='new_user')
        profile = ProfileFactory(user=user, about='Modern Soldier')
        post = PostFactory(content='New Post', owner=profile)

        self.url = reverse_lazy(
            'love-delete', kwargs={'post_id': post.id})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        love = Love.objects.filter(fan=self.profile, post=post)
        self.assertFalse(love.exists())
