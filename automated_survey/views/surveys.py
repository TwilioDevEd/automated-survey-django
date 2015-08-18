from automated_survey.models import Survey, Question
from django.http import HttpResponse
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from twilio import twiml


def redirect_to_first_survey(request):
    first_survey = Survey.objects.first()
    first_survey_url = reverse('survey', args=[first_survey.id])

    return redirect(first_survey_url, permanent=False)


class SurveyView(View):
    http_method_names = ['get']

    def get(self, request, survey_id):
        survey = Survey.objects.get(id=survey_id)
        first_question = Survey.objects.order_by('id').first()
        voice_response = twiml.Response()

        voice_response.say('Hello and welcome for taking the %s survey' % survey.title)
        voice_response.redirect(str(first_question.id))

        return HttpResponse(voice_response, content_type='application/xml')


class QuestionView(View):
    http_method_names = ['get']

    def get(self, request, survey_id, question_id):
        question = Question.objects.find(id=question_id)
        voice_response = twiml.Response()

        voice_response.say('question.title')

    def _next_question(self, question_id, survey_id):
        survey = Survey.objects.get(id=survey_id)
        questions = survey.question_set.order_by('id')
        next_questions = filter(lambda q: q.id > int(question_id), questions)

        return next_questions[0]
