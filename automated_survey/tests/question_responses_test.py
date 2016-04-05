import pytest
from django.test import TestCase
from automated_survey.models import Survey, Question, QuestionResponse
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse


class StoreQuestionResponseTest(TestCase):

    def setUp(self):
        self.survey = Survey(title='A testing survey')
        self.survey.save()

        self.question_one = Question(body='Question one', kind=Question.TEXT,
                                     survey=self.survey)
        self.question_one.save()
        self.question_ids_one = {'survey_id': self.survey.id,
                                 'question_id': self.question_one.id}

    def test_store_response_during_a_call(self):
        question_store_url = reverse('record_response', kwargs=self.question_ids_one)
        question_store_url += '?Kind=text'

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

    def test_store_SMS_response(self):
        question_store_url = reverse('record_response', kwargs=self.question_ids_one)
        question_store_url += '?Kind=text'

        request_parameters = {
            'MessageSid': 'somerandomuniqueid',
            'From': '324238944',
            'Body': 'I agree with you'
        }

        self.client.post(question_store_url, request_parameters)
        new_response = QuestionResponse.objects.get(question_id=self.question_one.id)

        assert new_response.call_sid == 'somerandomuniqueid'
        assert new_response.phone_number == '324238944'
        assert new_response.response == 'I agree with you'

    def test_store_response_and_redirect(self):
        question_two = Question(body='Question two', kind=Question.TEXT, survey=self.survey)
        question_two.save()
        question_ids_two = {'survey_id': self.survey.id,
                            'question_id': question_two.id}

        question_store_url_one = reverse('record_response', kwargs=self.question_ids_one) + '?Kind=numeric'
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
        invalid_question_store_url = reverse('record_response', kwargs=self.question_ids_one) + '?Kind=lol'
        request_parameters = {
            'CallSid': 'somerandomuniqueid',
            'From': '324238944',
            'Digits': '4'
        }
        with pytest.raises(ValidationError):
            self.client.post(invalid_question_store_url, request_parameters)

    def test_last_question(self):
        question_store_url_one = reverse('record_response', kwargs=self.question_ids_one) + '?Kind=numeric'
        request_parameters = {
            'CallSid': 'somerandomuniqueid',
            'From': '324238944',
            'Digits': '4'
        }

        response = self.client.post(question_store_url_one, request_parameters)

        assert response.status_code == 200
        assert 'Redirect' not in response.content.decode('utf8')
