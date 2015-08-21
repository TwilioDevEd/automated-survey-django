import pytest

from django.test import TestCase
from automated_survey.models import Survey, Question, QuestionResponse
from automated_survey.views.surveys import NoSuchQuestionKindException
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

    def setUp(self):
        self.survey = Survey(title='A testing survey')
        self.survey.save()

        self.question_one = Question(body='Question one', kind='voice', survey=self.survey)
        self.question_one.save()
        self.question_ids_one = {'survey_id': self.survey.id,
                                 'question_id': self.question_one.id}

    def test_store_response(self):
        question_store_url = reverse('record-response', kwargs=self.question_ids_one) + '?Kind=voice'

        request_parameters = {
            'CallSid': 'somerandomuniqueid',
            'From': '324238944',
            'RecordingUrl': 'gopher://recording.mp3'
        }

        self.client.post(question_store_url, request_parameters)
        new_response = QuestionResponse.objects.get(question_id=self.question_one.id)

        assert new_response.call_sid == 'somerandomuniqueid'
        assert new_response.phone_number == '324238944'
        assert new_response.response == 'gopher://recording.mp3'

    def test_store_response_and_redirect(self):
        question_two = Question(body='Question two', kind='voice', survey=self.survey)
        question_two.save()
        question_ids_two = {'survey_id': self.survey.id,
                            'question_id': question_two.id}

        question_store_url_one = reverse('record-response', kwargs=self.question_ids_one) + '?Kind=numeric'
        next_question_url = reverse('question', kwargs=question_ids_two)

        request_parameters = {
            'CallSid': 'somerandomuniqueid',
            'From': '324238944',
            'Digits': '4'
        }

        response = self.client.post(question_store_url_one, request_parameters)

        assert response.status_code == 303
        assert next_question_url in response.url

    def test_validate_question_kind(self):
        invalid_question_store_url = reverse('record-response', kwargs=self.question_ids_one) + '?Kind=lol'
        request_parameters = {
            'CallSid': 'somerandomuniqueid',
            'From': '324238944',
            'Digits': '4'
        }
        with pytest.raises(NoSuchQuestionKindException):
            self.client.post(invalid_question_store_url, request_parameters)

    def test_last_question(self):
        question_store_url_one = reverse('record-response', kwargs=self.question_ids_one) + '?Kind=numeric'
        request_parameters = {
            'CallSid': 'somerandomuniqueid',
            'From': '324238944',
            'Digits': '4'
        }

        response = self.client.post(question_store_url_one, request_parameters)

        assert response.status_code == 200
        assert 'Redirect' not in response.content
