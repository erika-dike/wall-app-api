from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from core import views


urlpatterns = [
    url(r'^auth/login/', obtain_jwt_token, name='user-login'),
    url(r'^auth/api-token-refresh/', refresh_jwt_token),
    url(r'^posts/$', views.PostList.as_view(), name='post-list'),
    url(r'^posts/(?P<pk>[0-9]+)/$',
        views.PostDetail.as_view(), name='post-detail'),
]
