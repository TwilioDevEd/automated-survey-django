from automated_survey.models import Survey, Question, QuestionResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST, require_GET
from twilio import twiml


@require_GET
def show_survey_results(request, survey_id):
    responses = QuestionResponse.objects.filter(question__survey__id=survey_id)
    survey = Survey.objects.get(id=survey_id)
    responses_to_render = list(map(lambda qr: _to_response(qr), responses))

    template_context = {
        'responses': responses_to_render,
        'survey_title': survey.title
    }

    return render_to_response('results.html', context=template_context)


@require_GET
def show_survey(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    first_question = Question.objects.order_by('id').first()

    first_question_ids = {
        'survey_id': survey.id,
        'question_id': first_question.id
    }

    first_question_url = reverse('question', kwargs=first_question_ids)
    text_response = twiml.Response()

    text_response.say(
        'Hello and thank you for taking the %s survey' %
        survey.title)
    text_response.redirect(first_question_url, method='GET')

    return HttpResponse(text_response, content_type='application/xml')


@require_POST
def redirect_to_first_survey(request):
    first_survey = Survey.objects.first()
    first_survey_url = reverse('survey', kwargs={'survey_id': first_survey.id})

    return HttpResponseRedirect(first_survey_url)


@require_GET
def redirect_to_first_results(request):
    first_survey = Survey.objects.first()
    results_for_first_survey = reverse(
        'survey_results', kwargs={
            'survey_id': first_survey.id})
    return HttpResponseRedirect(results_for_first_survey)


def _to_response(question_response):
    return {
        'body': question_response.question.body,
        'kind': question_response.question.kind,
        'response': question_response.response,
        'call_sid': question_response.call_sid,
        'phone_number': question_response.phone_number,
    }
