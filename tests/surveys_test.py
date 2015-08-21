from django.test import TestCase, Client
from automated_survey.models import Survey, Question
from django.core.urlresolvers import reverse


class SurveyRedirectionTest(TestCase):

    def set_up(self):
        self.client = Client()

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

        assert survey.title in response.content

    def test_redirect_to_first_question(self):
        survey = Survey(title='A testing survey')
        survey.save()

        question = Question(body='A Question', kind='voice', survey=survey)
        question.save()

        question_ids = {'survey_id': survey.id, 'question_id': question.id}
        question_url = reverse('question', kwargs=question_ids)

        response = self.client.get(reverse('survey', kwargs={'survey_id': survey.id}))

        assert question_url in response.content


class ShowQuestionTest(TestCase):

    def setUp(self):
        self.survey = Survey(title='A testing survey')
        self.survey.save()

        self.question = Question(body='A Question', kind='voice', survey=self.survey)
        self.question.save()

        self.question_ids = {'survey_id': self.survey.id, 'question_id': self.question.id}

    def test_show_voice_question(self):
        question_store_url = reverse('question', kwargs=self.question_ids)

        self.question.kind = 'voice'
        self.question.save()

        voice_response = self.client.get(reverse('question', kwargs=self.question_ids))

        assert self.question.body in voice_response.content
        assert 'Record' in voice_response.content
        assert question_store_url in voice_response.content

    def test_show_numeric_question(self):
        self.question.kind = 'numeric'
        self.question.save()

        numeric_response = self.client.get(reverse('question', kwargs=self.question_ids))

        assert 'Gather' in numeric_response.content

    def test_show_yesno_question(self):

        self.question.kind = 'yes-no'
        self.question.save()

        yesno_response = self.client.get(reverse('question', kwargs=self.question_ids))

        assert 'Gather' in yesno_response.content


class StoreQuestionResponseTest(TestCase):
    pass
