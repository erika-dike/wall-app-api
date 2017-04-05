from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from accounts import views


urlpatterns = [
    url(r'^register/$',
        views.RegistrationView.as_view(), name='user-registration'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.ActivationView.as_view(), name='activate'),
    url(r'^login/', obtain_jwt_token, name='user-login'),
    url(r'^api-token-refresh/', refresh_jwt_token),
]
