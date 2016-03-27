from django.conf.urls import url

from . import views

app_name='validators'
urlpatterns = [
    url(r'^thankyou$', views.thankyou, name='thankyou'),
    url(r'^contact$', views.ContactView.as_view(), name='contact'),
]

