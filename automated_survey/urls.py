"""automated_survey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from views.surveys import redirect_to_first_survey
from views.surveys import SurveyView, QuestionView, QuestionResponseView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^survey/(?P<survey_id>\d+)/question/(?P<question_id>\d+)$',
        QuestionView.as_view(),
        name='question'),

    url(r'^survey/(?P<survey_id>\d+)$',
        SurveyView.as_view(),
        name='survey'),

    url(r'^first_survey/',
        redirect_to_first_survey,
        name='first-survey'),

    url(r'^survey/(?P<survey_id>\d+)/question/(?P<question_id>\d+)/question_response$',
        QuestionResponseView.as_view(),
        name='record-response')
]
