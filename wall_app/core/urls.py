from django.conf.urls import url

from core import views


urlpatterns = [
    url(r'^posts/$', views.PostList.as_view(), name='post-list'),
    url(r'^posts/(?P<pk>[0-9]+)/$',
        views.PostDetail.as_view(), name='post-detail'),
    url(r'^posts/(?P<post_id>[0-9]+)/loves/$',
        views.LoveView.as_view(), name='love-view'),
]
