from twilio import twiml

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST

from automated_survey.models import QuestionResponse, Question


@require_POST
def record_response(request, survey_id, question_id):
    question = Question.objects.get(id=question_id)

    save_response(request, question)

    next_question = question.next()
    if not next_question:
        return goodbye(request)
    else:
        return redirect_over_twiml(next_question.id, survey_id)


def redirect_over_twiml(question_id, survey_id):
    parameters = {'survey_id': survey_id, 'question_id': question_id}
    question_url = reverse('question', kwargs=parameters)

    twiml_response = twiml.Response()
    twiml_response.redirect(question_url, method='GET')
    return HttpResponse(twiml_response)


def goodbye(request):
    response = twiml.Response()
    goodbye_messages = ['That was the last question',
                        'Thank you for taking this survey',
                        'Good-bye']
    if request.is_sms:
        [response.message(message) for message in goodbye_messages]
    else:
        [response.say(message) for message in goodbye_messages]
        response.hangup()

    return HttpResponse(response)


def save_response(request, question):
    session_id = request.POST['MessageSid' if request.is_sms else 'CallSid']
    request_body = _extract_request_body(request, question.kind)
    phone_number = request.POST['From']

    QuestionResponse(call_sid=session_id,
                     phone_number=phone_number,
                     response=request_body,
                     question=question).save()


def _extract_request_body(request, question_kind):
    Question.validate_kind(question_kind)

    if request.is_sms:
        key = 'Body'
    elif question_kind in [Question.YES_NO, Question.NUMERIC]:
        key = 'Digits'
    else:
        key = 'RecordingUrl'

    return request.POST.get(key)
