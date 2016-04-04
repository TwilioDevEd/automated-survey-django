from django.views.generic import View
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from twilio import twiml

from automated_survey.models import Survey, QuestionResponse, Question
from automated_survey.views.common import parameters_for_survey_url


class QuestionResponseView(View):
    http_method_names = ['post']

    def post(self, request, survey_id, question_id):
        question_kind = request.GET.get('Kind')
        if question_kind not in [Question.YES_NO, Question.NUMERIC,
                                 Question.TEXT]:
            raise NoSuchQuestionKindException

        new_response = self._question_response_from_request(request)
        new_response.question_id = question_id
        new_response.save()

        return self._redirect_for_next_question(survey_id, question_id)

    def _question_response_from_request(self, request):
        question_kind = request.GET.get('Kind')
        (call_sid, phone_number) = (request.POST['CallSid'],
                                    request.POST['From'])

        new_response = QuestionResponse(
            call_sid=call_sid, phone_number=phone_number)
        new_response.response = self._question_response_content(
            request, question_kind)

        return new_response

    def _question_response_content(self, request, question_kind):
        if question_kind in [Question.YES_NO, Question.NUMERIC]:
            return request.POST['Digits']
        elif question_kind == Question.TEXT:
            return request.POST['RecordingUrl']
        else:
            raise NoSuchQuestionKindException

    def _redirect_for_next_question(self, survey_id, question_id):
        try:
            next_question = self._next_question(survey_id, question_id)
        except IndexError:
            return self._goodbye_message()

        url_parameters = parameters_for_survey_url(
            next_question.survey_id, next_question.id)
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

    def _goodbye_message(self):
        text_response = twiml.Response()
        text_response.say('That was the last question')
        text_response.say('Thank you for taking this survey')
        text_response.say('Good-bye')
        text_response.hangup()

        return HttpResponse(text_response)


class NoSuchQuestionKindException(Exception):
    pass
