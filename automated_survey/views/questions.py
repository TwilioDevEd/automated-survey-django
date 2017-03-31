from django.core.urlresolvers import reverse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from django.http import HttpResponse

from automated_survey.models import Question
from django.views.decorators.http import require_GET


@require_GET
def show_question(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)
    if request.is_sms:
        twiml = sms_question(question)
    else:
        twiml = voice_question(question)

    request.session['answering_question_id'] = question.id
    return HttpResponse(twiml, content_type='application/xml')


def sms_question(question):
    twiml_response = MessagingResponse()

    twiml_response.message(question.body)
    twiml_response.message(SMS_INSTRUCTIONS[question.kind])

    return twiml_response

SMS_INSTRUCTIONS = {
    Question.TEXT: 'Please type your answer',
    Question.YES_NO: 'Please type 1 for yes and 0 for no',
    Question.NUMERIC: 'Please type a number between 1 and 10'
}


def voice_question(question):
    twiml_response = VoiceResponse()

    twiml_response.say(question.body)
    twiml_response.say(VOICE_INSTRUCTIONS[question.kind])

    action = save_response_url(question)
    if question.kind == Question.TEXT:
        kwargs = {'maxLength': 6,
                  'transcribe': True,
                  'transcribeCallback': action}
        twiml_response.record(action=action, method='POST', **kwargs)
    else:
        twiml_response.gather(action=action, method='POST')
    return twiml_response

VOICE_INSTRUCTIONS = {
    Question.TEXT: 'Please record your answer after the beep and then hit the pound sign',
    Question.YES_NO: 'Please press the one key for yes and the zero key for no and then hit the pound sign',
    Question.NUMERIC: 'Please press a number between 1 and 10 and then hit the pound sign'
}


def save_response_url(question):
    return reverse('save_response',
                   kwargs={'survey_id': question.survey.id,
                           'question_id': question.id})
