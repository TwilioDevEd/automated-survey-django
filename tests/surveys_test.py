from django.test import TestCase, Client
from automated_survey.models import Survey
from django.core.urlresolvers import reverse


class TestSurveyRedirection(TestCase):

    def set_up(self):
        self.client = Client()

    def test_redirection(self):
        survey = Survey(title='A testing survey')
        survey.save()

        response = self.client.post('/first_survey/')
        expected_url = reverse('survey', kwargs={'survey_id': survey.id})

        self.assertTrue(expected_url in str(response.url))
