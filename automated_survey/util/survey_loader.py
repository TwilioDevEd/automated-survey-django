import json
from automated_survey.models import Survey, Question


class SurveyLoader(object):

    def __init__(self, survey_content):
        self.survey_content = survey_content

    def load_survey(self):
        try:
            survey = json.loads(self.survey_content)
            new_survey = Survey(title=survey['title'])
            questions = map(lambda q: Question(body=q['body'], kind=q['kind']), survey['questions'])

            new_survey.save()
            new_survey.question_set.add(*questions)

        except KeyError:
            print('Malformed JSON file for survey')
