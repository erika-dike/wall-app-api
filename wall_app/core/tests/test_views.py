from django.urls import reverse_lazy
from rest_framework import status
import mock
from rest_framework_jwt.serializers import User

from accounts.models import Profile
from core.models import Love, Post
from core.tests.http_header import APIHeaderAuthorization


class PostListTestSuite(APIHeaderAuthorization):
    @classmethod
    def setUpClass(cls):
        super(PostListTestSuite, cls).setUpClass()
        cls.url = reverse_lazy('post-list')

    def test_get_all_posts(self):
        posts = ('Hello World!!!', 'Hello TSL!!!', 'Welcome to TSL!!!')
        self.create_post_objects(self.profile, posts)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(posts))
        for index, post in enumerate(response.data['results']):
            self.assertEqual(post['content'], posts[index])

    def test_post_new_post(self):
        post = {'content': 'Hello World!'}
        response = self.client.post(self.url, data=post)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Post.objects.filter(content=post['content']).exists()
        )

    @mock.patch('core.pagination.StandardResultsSetPagination.page_size')
    def test_posts_respons_are_paginated(self, mocked_page_size):
        posts = ('Hello World!!!', 'Hello TSL!!!', 'Welcome to TSL!!!')
        mocked_page_size.return_value = 1
        self.create_post_objects(self.profile, posts)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']),
            mocked_page_size.return_value
        )
        self.assertEqual(response.data['count'], len(posts))
        self.assertTrue(response.data['next'])

    @staticmethod
    def create_post_objects(profile, posts):
        for post in posts:
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
        self.url = reverse_lazy('post-detail', kwargs={'pk': self.post.id})

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


class LoveCreateTestSuite(APIHeaderAuthorization):
    def setUp(self):
        super(LoveCreateTestSuite, self).setUp()
        self.post_data = {
            'content': 'Hello World!!!',
            'owner': self.profile
        }
        self.post = Post.objects.create(**self.post_data)
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
        user_details = self.user_details.copy()
        user_details['username'] = 'new_user'
        profile_details = self.profile_details.copy()
        profile_details['about'] = 'Modern Soldier'
        user = User.objects.create_user(**user_details)
        profile = Profile.objects.create(user=user, **profile_details)
        post = Post.objects.create(content='New Post', owner=profile)

        self.url = reverse_lazy(
            'love-create', kwargs={'post_id': post.id})
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        love = Love.objects.filter(fan=self.profile, post=post)
        self.assertTrue(love.exists())


class LoveDeleteTestSuite(APIHeaderAuthorization):
    def setUp(self):
        super(LoveDeleteTestSuite, self).setUp()
        self.post_data = {
            'content': 'Hello World!!!',
            'owner': self.profile
        }
        self.post = Post.objects.create(**self.post_data)
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
        user_details = self.user_details.copy()
        user_details['username'] = 'new_user'
        profile_details = self.profile_details.copy()
        profile_details['about'] = 'Modern Soldier'
        user = User.objects.create_user(**user_details)
        profile = Profile.objects.create(user=user, **profile_details)
        post = Post.objects.create(content='New Post', owner=profile)

        self.url = reverse_lazy(
            'love-delete', kwargs={'post_id': post.id})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        love = Love.objects.filter(fan=self.profile, post=post)
        self.assertFalse(love.exists())
