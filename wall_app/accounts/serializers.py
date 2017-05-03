from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from accounts.models import Profile


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=15,
        min_length=5,
        required=True
    )
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    about = serializers.CharField(max_length=250)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two passwords didn't match"))
        return data

    def save(self):
        username = self.validated_data['username']
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    first_name=self.validated_data['first_name'],
                    last_name=self.validated_data['last_name'],
                    email=self.validated_data['email'],
                    password=self.validated_data['password1'],
                    is_active=False
                )
                profile = Profile.objects.create(
                    user=user,
                    about=self.validated_data['about']
                )
        except IntegrityError:
            raise serializers.ValidationError(_(
                "username - '{username}' already exists".format(
                    username=username)
            ))
        return profile


class UserDetailSerializer(serializers.ModelSerializer):
    """Serialized representation of a user"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        extra_kwargs = {
            'username': {'validators': []},
        }


class ProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer representation of a profile"""
    user = UserDetailSerializer()

    class Meta:
        model = Profile
        fields = ('user', 'about', 'profile_pic')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        instance.about = validated_data.get('about', instance.about)
        instance.profile_pic = validated_data.get(
            'profile_pic', instance.profile_pic)
        instance.save()

        user.username = user_data.get('username', user.username)
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.save()

        return instance


class PublicProfileSerializer(serializers.ModelSerializer):
    """Serialized representation of a public profile"""
    class Meta:
        model = Profile
        fields = ('about', 'profile_pic')


class PublicUserSerializer(serializers.ModelSerializer):
    """Serialized representation of a public user"""
    about = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'about', 'profile_pic')
        read_only_fields = ('username', 'first_name', 'last_name', 'about', 'profile_pic')

    def get_about(self, obj):
        return obj.profile.about

    def get_profile_pic(self, obj):
        return obj.profile.profile_pic
