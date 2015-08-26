# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def load_sample_survey(apps, schema_editor):
    call_command('load_survey', 'automated_survey/tests/fixtures/bear_survey.json')


class Migration(migrations.Migration):

    dependencies = [
        ('automated_survey', '0002_questionresponse'),
    ]

    operations = [
        migrations.RunPython(load_sample_survey)
    ]
