from django.conf.urls import url

from accounts import views


urlpatterns = [
    url(r'^register/$',
        views.RegistrationView.as_view(), name='user-registration'),
    # url(r'^account_activation_sent/$',
    #     views.AccountActivationSent.as_view(), name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.ActivationView.as_view(), name='activate'),
]
