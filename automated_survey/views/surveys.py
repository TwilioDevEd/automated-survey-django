from automated_survey.models import Survey, Question, QuestionResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.views.decorators.http import require_POST
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

        voice_response.say('Hello and thank you for taking the %s survey' % survey.title)
        voice_response.redirect(first_question_url, method='GET')

        return HttpResponse(voice_response, content_type='application/xml')


class QuestionView(View):
    http_method_names = ['get']

    def get(self, request, survey_id, question_id):
        question = Question.objects.get(id=question_id)

        url_parameters = parameters_for_survey_url(question.survey.id,
                                                   question.id)

        question_store_url = reverse('record-response', kwargs=url_parameters)

        voice_response = twiml.Response()
        voice_response.say(question.body)
        voice_response.say(instructions[question.kind])
        voice_response = attach_command_to_response(
            voice_response, question.kind, question_store_url
        )

        return HttpResponse(voice_response, content_type='application/xml')


class QuestionResponseView(View):
    http_method_names = ['post']

    def post(self, request, survey_id, question_id):
        question_kind = request.GET.get('Kind')
        if question_kind not in ['yes-no', 'numeric', 'voice']:
            raise NoSuchQuestionKindException

        new_response = self._question_response_from_request(request)
        new_response.question_id = question_id
        new_response.save()

        return self._redirect_for_next_question(survey_id, question_id)

    def _question_response_from_request(self, request):
        question_kind = request.GET.get('Kind')
        (call_sid, phone_number) = (request.POST['CallSid'],
                                    request.POST['From'])

        new_response = QuestionResponse(call_sid=call_sid, phone_number=phone_number)
        new_response.response = self._question_response_content(request, question_kind)

        return new_response

    def _redirect_for_next_question(self, survey_id, question_id):
        try:
            next_question = self._next_question(survey_id, question_id)
        except IndexError:
            return self._goodbye_message()

        url_parameters = parameters_for_survey_url(next_question.survey_id, next_question.id)
        next_question_url = reverse('question', kwargs=url_parameters)

        see_other = redirect(next_question_url)
        see_other.status_code = 303
        see_other.reason_phrase = 'See Other'

        return see_other

    def _next_question(self, survey_id, question_id):
        survey = Survey.objects.get(id=survey_id)

        questions = survey.question_set.order_by('id')
        next_questions = filter(lambda q: q.id > int(question_id), questions)

        return list(next_questions)[0]

    def _question_response_content(self, request, question_kind):
        if question_kind in ['yes-no', 'numeric']:
            return request.POST['Digits']
        elif question_kind == 'voice':
            return request.POST['RecordingUrl']
        else:
            raise NoSuchQuestionKindException

    def _goodbye_message(self):
        voice_response = twiml.Response()
        voice_response.say('That was the last question')
        voice_response.say('Thank you for taking this survey')
        voice_response.say('Good-bye')
        voice_response.hangup()

        return HttpResponse(voice_response)


class SurveyResultsView(View):
    http_method_names = ['get']

    def get(self, request, survey_id):
        return render_to_response('base_template.html')

@require_POST
def redirect_to_first_survey(request):
    first_survey = Survey.objects.first()
    first_survey_url = reverse('survey', kwargs={'survey_id': first_survey.id})

    return HttpResponseRedirect(first_survey_url)

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


def parameters_for_survey_url(survey_id, question_id):
    args = {
        'survey_id': survey_id,
        'question_id': question_id
    }

    return args


class NoSuchVerbException(Exception):
    pass


class NoSuchQuestionKindException(Exception):
    pass
