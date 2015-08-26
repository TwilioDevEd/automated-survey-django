from django.shortcuts import redirect
from django.conf.urls import include, url

urlpatterns = [
    url(r'^automated-survey/', include('automated_survey.urls'), name='surveys'),
    url(r'^$', lambda r: redirect('/automated-survey'), name='root-redirect')
]
