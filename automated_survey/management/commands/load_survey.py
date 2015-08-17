from django.core.management import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('load_surveys', metavar='survey-name', nargs=1)

    def handle(self, *args, **options):
        print('Super')
