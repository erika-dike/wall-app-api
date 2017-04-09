from django.conf.urls import url

from core import views


urlpatterns = [
    url(r'^posts/$', views.PostList.as_view(), name='post-list'),
    url(r'^posts/(?P<pk>[0-9]+)/$',
        views.PostDetail.as_view(), name='post-detail'),
    url(r'^posts/(?P<post_id>[0-9]+)/loves/create/$',
        views.LoveCreate.as_view(), name='love-create'),
    url(r'^posts/(?P<post_id>[0-9]+)/loves/delete/$',
        views.LoveDelete.as_view(), name='love-delete'),
]
