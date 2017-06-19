from django.test import TestCase

from factories.factories import UserFactory, ProfileFactory

from core.models import Post, Love
from core.tests.testing_utils import (
    create_love_relationship, create_post_objects
)


class Base(TestCase):
    def setUp(self):
        self.user_1 = UserFactory()
        self.user_2 = UserFactory(
            username='jane_doe',
            first_name='Jane',
            email='jane_doe@wallie.com'
        )
        ProfileFactory(user=self.user_1)
        ProfileFactory(user=self.user_2)
        profile_1_posts = create_post_objects(self.user_1, 3)
        profile_2_posts = create_post_objects(self.user_2, 2)
        self.posts_with_2_loves = profile_1_posts[:1] + profile_2_posts[:1]
        self.posts_with_1_love = profile_1_posts[1:2]
        self.posts_with_no_love = profile_1_posts[2:] + profile_2_posts[1:]
        create_love_relationship(self.user_1, self.posts_with_2_loves)
        create_love_relationship(self.user_2, self.posts_with_2_loves)
        create_love_relationship(self.user_2, self.posts_with_1_love)


class PostTestSuite(Base):
    def test_get_queryset_returns_accurate_values_for_num_loves(self):
        queryset = Post.get_queryset(self.user_1.id)
        for post in queryset:
            if post.num_loves == 2:
                self.assertIn(post, self.posts_with_2_loves)
            elif post.num_loves == 1:
                self.assertIn(post, self.posts_with_1_love)
            else:
                self.assertIn(post, self.posts_with_no_love)

    def test_get_queryset_returns_accurate_values_for_in_love_profile_1(self):
        queryset = Post.get_queryset(self.user_1.id)
        queryset_with_loved_posts = queryset.filter(loves__fan=self.user_1)
        expected = self.posts_with_2_loves
        for post in queryset_with_loved_posts:
            self.assertIn(post, expected)

    def test_get_queryset_returns_accurate_values_for_in_love_profile_2(self):
        queryset = Post.get_queryset(self.user_2.id)
        queryset_with_loved_posts = queryset.filter(loves__fan=self.user_2)
        expected = self.posts_with_2_loves + self.posts_with_1_love
        for post in queryset_with_loved_posts:
            self.assertIn(post, expected)

    def test_order_queryset_by_num_loves_returns_posts_ordered_by_num_loves(self):
        queryset = Post.get_queryset(self.user_1.id)
        queryset = Post.order_queryset_by_num_loves(queryset, limit=10)
        expected = (self.posts_with_2_loves +
                    self.posts_with_1_love +
                    self.posts_with_no_love)
        for index, post in enumerate(queryset):
            self.assertEqual(post.id, expected[index].id)


class LoveTestSuite(Base):
    def test_create_love_creates_new_love_object(self):
        love = Love.create_love(self.user_1, self.posts_with_no_love[0].id)
        self.assertIsInstance(love, Love)

    def test_create_love_returns_existing_love_when_relationship_already_exists(self):
        post = self.posts_with_2_loves[0]
        love = Love.create_love(self.user_1, post.id)
        self.assertIsInstance(love, Love)
        self.assertEqual(love.fan, self.user_1)
        self.assertEqual(love.post, post)

    def test_delete_love_object(self):
        post = self.posts_with_1_love[0]
        Love.delete_love(self.user_1, post.id)
        self.assertFalse(
            Love.objects.filter(fan=self.user_1, post=post).exists())

    def test_get_num_post_loves(self):
        for post in self.posts_with_2_loves:
            self.assertEqual(Love.get_num_post_loves(post.id), 2)
        for post in self.posts_with_1_love:
            self.assertEqual(Love.get_num_post_loves(post.id), 1)
        for post in self.posts_with_no_love:
            self.assertEqual(Love.get_num_post_loves(post.id), 0)
