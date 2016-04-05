from django.views.generic import View
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from twilio import twiml

from automated_survey.models import QuestionResponse, Question


class QuestionResponseView(View):
    http_method_names = ['post']

    def post(self, request, survey_id, question_id):
        question = Question.objects.get(id=question_id)
        response = QuestionResponse.from_twilio_request(request)
        response.question = question
        response.save()
        return self._redirect_to_next_question(question)

    def _redirect_to_next_question(self, question):
        next_question = question.next()
        if not next_question:
            return self._goodbye_message()

        parameters = {'survey_id':   next_question.survey.id,
                      'question_id': next_question.id}
        next_question_url = reverse('question', kwargs=parameters)

        twiml_response = twiml.Response()
        twiml_response.redirect(next_question_url, method='GET')
        return HttpResponse(twiml_response)

    def _goodbye_message(self):
        text_response = twiml.Response()
        text_response.say('That was the last question')
        text_response.say('Thank you for taking this survey')
        text_response.say('Good-bye')
        text_response.hangup()

        return HttpResponse(text_response)
