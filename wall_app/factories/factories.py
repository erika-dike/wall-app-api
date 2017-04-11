from django.contrib.auth.models import User
import factory

from accounts.models import Profile
from core.models import Love, Post


USER_DATA = {
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john_doe@wall.com',
    'password': 'notsecret',
}
PROFILE_DATA = {
    'about': 'Unknown Soldier',
    'profile_pic': 'http://unknown-domain.com/does-not-exit.jpg'
}


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = USER_DATA['username']
    first_name = USER_DATA['first_name']
    last_name = USER_DATA['last_name']
    email = USER_DATA['email']
    password = factory.PostGenerationMethodCall(
        'set_password',
        USER_DATA['password']
    )


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    about = PROFILE_DATA['about']
    profile_pic = PROFILE_DATA['profile_pic']


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    content = factory.Faker('sentence', nb_words=6)
    author = factory.SubFactory(ProfileFactory)


class LoveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Love

    fan = factory.SubFactory(ProfileFactory)
    post = factory.SubFactory(PostFactory)
