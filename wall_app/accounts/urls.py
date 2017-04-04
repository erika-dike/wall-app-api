from django.conf.urls import url

from accounts import views


urlpatterns = [
    url(r'^register/$',
        views.RegisterView.as_view(), name='user-registration'),
]
