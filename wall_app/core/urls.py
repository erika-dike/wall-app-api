from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from core import views


urlpatterns = [
    url(r'^auth/login/', obtain_jwt_token, name='user-login'),
    url(r'^auth/api-token-refresh/', refresh_jwt_token),
    url(r'^messages/$', views.MessageList.as_view(), name='message-list'),
]
