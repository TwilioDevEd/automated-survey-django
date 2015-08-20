from automated_survey.models import Survey, Question
from django.http import HttpResponse
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from twilio import twiml


class SurveyView(View):
    http_method_names = ['get']

    def get(self, request, survey_id):
        survey = Survey.objects.get(id=survey_id)
        first_question = Question.objects.order_by('id').first()

        first_question_ids = {
            'survey_id':   survey.id,
            'question_id': first_question.id
        }

        first_question_url = reverse('question', kwargs=first_question_ids)
        voice_response = twiml.Response()

        voice_response.say('Hello and welcome for taking the %s survey' % survey.title)
        voice_response.redirect(first_question_url)

        return HttpResponse(voice_response, content_type='application/xml')


class QuestionView(View):
    http_method_names = ['get']

    def get(self, request, survey_id, question_id):
        question = Question.objects.get(id=question_id)
        next_question_parameters = {
            'survey_id': question.survey.id,
            'question_id': question.id
        }

        question_store_url = reverse(
            'record-response',
            kwargs=next_question_parameters
        )

        voice_response = twiml.Response()
        voice_response.say(instructions[question.kind])
        voice_response.say(question.body)
        voice_response = attach_command_to_response(
            voice_response, question.kind, question_store_url
        )

        return HttpResponse(voice_response, content_type='application/xml')


class QuestionResponseView(View):
    http_method_names = ['post']

    def post(self):
        pass

    def _next_question(self, question_id, survey_id):
        survey = Survey.objects.get(id=survey_id)

        questions = survey.question_set.order_by('id')
        next_questions = filter(lambda q: q.id > int(question_id), questions)

        return next_questions[0]


instructions = {
    'voice': 'Please record your answer after the beep and then hit the pound sign',
    'yes-no': 'Please press the one key for yes and the zero key for no and then hit the pound sign',
    'numeric': 'Please press a number between 1 and 10 and then hit the pound sign'
}


def attach_command_to_response(response, kind, action):
    if kind == 'voice':
        response.record(action=action + '?Kind=voice', method='POST')
    elif kind == 'numeric':
        response.gather(action=action + '?Kind=numeric', method='POST')
    elif kind == 'yes-no':
        response.gather(action=action + '?Kind=yes-no', method='POST')
    else:
        raise NoSuchVerbException('%s is not a supported question type' % kind)

    return response


def redirect_to_first_survey(request):
    first_survey = Survey.objects.first()
    first_survey_url = reverse('survey', kwargs={'survey_id': first_survey.id})

    return redirect(first_survey_url, permanent=False)


class NoSuchVerbException(Exception):
    pass
