from django.core.urlresolvers import reverse
from twilio import twiml
from django.http import HttpResponse

from automated_survey.models import Question
from django.views.decorators.http import require_GET


@require_GET
def show_question(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)
    if request.is_sms:
        twiml = sms_twiml_for_question(question)
    else:
        twiml = voice_twiml_for_question(question)
    request.session['answering_question_id'] = question.id
    return HttpResponse(twiml, content_type='application/xml')


def sms_twiml_for_question(question):
    twiml_response = twiml.Response()

    twiml_response.message(question.body)
    twiml_response.message(SMS_INSTRUCTIONS[question.kind])

    return twiml_response

SMS_INSTRUCTIONS = {
    Question.TEXT: 'Please type your answer',
    Question.YES_NO: 'Please type 1 for yes and 0 for no',
    Question.NUMERIC: 'Please type a number between 1 and 10'
}


def voice_twiml_for_question(question):
    twiml_response = twiml.Response()

    twiml_response.say(question.body)
    twiml_response.say(CALL_INSTRUCTIONS[question.kind])

    action = record_response_url(question)
    if question.kind == Question.TEXT:
        twiml_response.record(action=action, method='POST')
    else:
        twiml_response.gather(action=action, method='POST')
    return twiml_response

CALL_INSTRUCTIONS = {
    Question.TEXT: 'Please record your answer after the beep and then hit the pound sign',
    Question.YES_NO: 'Please press the one key for yes and the zero key for no and then hit the pound sign',
    Question.NUMERIC: 'Please press a number between 1 and 10 and then hit the pound sign'
}


def record_response_url(question):
    url = reverse('record_response',
                  kwargs={'survey_id': question.survey.id,
                          'question_id': question.id})
    url += '?Kind=%s' % question.kind
    return url
