from django.test import TestCase
from automated_survey.models import Survey, Question
from django.core.urlresolvers import reverse


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

        assert self.question.body in voice_response.content.decode('utf8')
        assert 'Record' in voice_response.content.decode('utf8')
        assert question_store_url in voice_response.content.decode('utf8')

    def test_show_numeric_question(self):
        self.question.kind = 'numeric'
        self.question.save()

        numeric_response = self.client.get(reverse('question', kwargs=self.question_ids))

        assert 'Gather' in numeric_response.content.decode('utf8')

    def test_show_yesno_question(self):
        self.question.kind = 'yes-no'
        self.question.save()

        yesno_response = self.client.get(reverse('question', kwargs=self.question_ids))

        assert 'Gather' in yesno_response.content.decode('utf8')
