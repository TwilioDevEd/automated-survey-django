from django.shortcuts import redirect
from django.conf.urls import include, url

urlpatterns = [
    url(r'^automated_survey/', include('automated_survey.urls'), name='surveys'),
    url(r'^$', lambda r: redirect('/automated_survey'), name='root-redirect')
]
