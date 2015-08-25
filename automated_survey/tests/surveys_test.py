from django.test import TestCase
from automated_survey.models import Survey, Question
from django.core.urlresolvers import reverse


class SurveyRedirectionTest(TestCase):

    def test_entry_point_redirection(self):
        survey = Survey(title='A testing survey')
        survey.save()

        response = self.client.post('/first_survey/')
        expected_url = reverse('survey', kwargs={'survey_id': survey.id})

        assert expected_url in response.url

    def test_show_survey(self):
        survey = Survey(title='A testing survey')
        survey.save()
        Question(body='A Question', kind='voice', survey=survey).save()

        response = self.client.get(reverse('survey', kwargs={'survey_id': survey.id}))

        assert survey.title in response.content.decode('utf8')

    def test_redirect_to_first_question(self):
        survey = Survey(title='A testing survey')
        survey.save()

        question = Question(body='A Question', kind='voice', survey=survey)
        question.save()

        question_ids = {'survey_id': survey.id, 'question_id': question.id}
        question_url = reverse('question', kwargs=question_ids)

        response = self.client.get(reverse('survey', kwargs={'survey_id': survey.id}))

        assert question_url in response.content.decode('utf8')
