import pytest

from automated_survey.models import Survey, Question
from automated_survey.util.survey_loader import SurveyLoader
from django.test import TestCase

sample_survey = """
{"title": "About bears", "questions": [{"body": "What type of bear is best?", "kind": "voice"}, {"body": "In a scale of 1 to 10 how cute do you find koalas?", "kind": "numeric"}, {"body": "Do you think bears beat beets?", "kind": "yes-no"}]}
"""


class SurveyLoaderTest(TestCase):
    def test_load_survey(self):
        loader = SurveyLoader(sample_survey)
        loader.load_survey()

        all_surveys = Survey.objects.all()
        all_questions = Question.objects.all()

        assert len(all_surveys) == 1
        assert len(all_questions) == 3
        assert all_surveys.first().title == 'About bears'
