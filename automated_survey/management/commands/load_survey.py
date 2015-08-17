import os
import json
from django.core.management import BaseCommand
from automated_survey.settings.env import root
from automated_survey.models import Survey, Question


class Command(BaseCommand):
    COMMAND = 'load_surveys'

    def add_arguments(self, parser):
        parser.add_argument(self.COMMAND, metavar='survey-name', nargs=1)

    def handle(self, *args, **options):
        file_name = options['load_surveys'][0]
        absolute_file_name = os.path.join(str(root), file_name)

        with open(absolute_file_name, 'r') as survey_to_load:
            survey = json.loads(survey_to_load.read())

            try:
                new_survey = Survey(title=survey['title'])
                questions = map(lambda q: Question(body=q['body'],
                                                   kind=q['kind'])
                                , survey['questions'])

                new_survey.save()
                new_survey.question_set.add(*questions)

            except KeyError:
                print('Malformed JSON file')
