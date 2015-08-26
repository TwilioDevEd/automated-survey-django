from django.conf.urls import include, url

urlpatterns = [
    url(r'^automated_survey/', include('automated_survey.urls'))
]
