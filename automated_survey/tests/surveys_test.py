from django.test import TestCase
from automated_survey.models import Survey, Question, QuestionResponse
from django.core.urlresolvers import reverse


class SurveyRedirectionTest(TestCase):

    def test_entry_point_redirection(self):
        survey = Survey(title='A testing survey')
        survey.save()

        response = self.client.post(reverse('first_survey'))
        expected_url = reverse('survey', kwargs={'survey_id': survey.id})

        assert expected_url in response.url

    def test_show_survey(self):
        survey = Survey(title='A testing survey')
        survey.save()
        Question(body='A Question', kind=Question.VOICE, survey=survey).save()

        response = self.client.get(reverse('survey', kwargs={'survey_id': survey.id}))

        assert survey.title in response.content.decode('utf8')

    def test_redirect_to_first_question(self):
        survey = Survey(title='A testing survey')
        survey.save()

        question = Question(body='A Question', kind=Question.VOICE, survey=survey)
        question.save()

        question_ids = {'survey_id': survey.id, 'question_id': question.id}
        question_url = reverse('question', kwargs=question_ids)

        response = self.client.get(reverse('survey', kwargs={'survey_id': survey.id}))

        assert question_url in response.content.decode('utf8')


class SurveyResultsTest(TestCase):

    def test_render_context(self):
        survey = Survey(title='A testing survey')
        survey.save()

        question_one = Question(body='Question one', kind=Question.VOICE, survey=survey)
        question_one.save()

        question_response = QuestionResponse(response='gopher://someaudio.mp3',
                                             call_sid='sup3runiq3',
                                             phone_number='+14155552671',
                                             question=question_one)

        question_response.save()

        redirect = self.client.get(reverse('app_root'))
        survey_results_url = reverse('survey_results', kwargs={'survey_id': survey.id})

        assert survey_results_url in redirect.url

        response = self.client.get(survey_results_url)

        expected_responses = [{'body': 'Question one',
                               'phone_number': '+14155552671',
                               'kind': 'voice',
                               'response': 'gopher://someaudio.mp3',
                               'call_sid': 'sup3runiq3'}]

        assert expected_responses == response.context['responses']
        assert survey.title == response.context['survey_title']
