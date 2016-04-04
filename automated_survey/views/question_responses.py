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
        self._save_response(request, question_id)
        return self._redirect_to_next_question(survey_id, question_id)

    def _save_response(self, request, question_id):
        QuestionResponse(
            call_sid=request.POST['CallSid'],
            phone_number=request.POST['From'],
            response=self._extract_content(request),
            question_id=question_id).save()

    def _extract_content(self, request):
        question_kind = request.GET.get('Kind')
        self._validate_question_kind(question_kind)

        if question_kind in [Question.YES_NO, Question.NUMERIC]:
            return request.POST['Digits']
        return request.POST['RecordingUrl']

    def _validate_question_kind(self, kind):
        if not Question.is_valid_kind(kind):
            raise NoSuchQuestionKindException

    def _redirect_to_next_question(self, survey_id, question_id):
        next_question = self._next_question(survey_id, question_id)
        if not next_question:
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

        next_questions = \
            survey.question_set.order_by('id').filter(id__gt=question_id)

        return next_questions[0] if next_questions else None

    def _goodbye_message(self):
        text_response = twiml.Response()
        text_response.say('That was the last question')
        text_response.say('Thank you for taking this survey')
        text_response.say('Good-bye')
        text_response.hangup()

        return HttpResponse(text_response)


class NoSuchQuestionKindException(Exception):
    pass
