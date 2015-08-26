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
from django.views.decorators.csrf import csrf_exempt

from automated_survey.views.surveys import redirect_to_first_survey
from automated_survey.views.surveys import redirect_to_first_results
from automated_survey.views.questions import show_question
from automated_survey.views.surveys import show_survey, show_survey_results
from automated_survey.views.question_responses import QuestionResponseView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', redirect_to_first_results, name='app_root'),

    url(r'^survey/(?P<survey_id>\d+)/question/(?P<question_id>\d+)$',
        show_question,
        name='question'),

    url(r'^survey/(?P<survey_id>\d+)$',
        show_survey,
        name='survey'),

    url(r'^first-survey/',
        csrf_exempt(redirect_to_first_survey),
        name='first_survey'),

    url(r'^survey/(?P<survey_id>\d+)/results$',
        show_survey_results,
        name='survey_results'),

    url(r'^survey/(?P<survey_id>\d+)/question/(?P<question_id>\d+)/question_response$',
        csrf_exempt(QuestionResponseView.as_view()),
        name='record_response')
]
