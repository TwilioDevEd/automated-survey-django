from automated_survey.models import Survey
from django.http import HttpResponse


def redirect_to_first_survey(request):
    first_survey = Survey.objects.first()
    return HttpResponse(str(first_survey.title) + str(first_survey.id))
