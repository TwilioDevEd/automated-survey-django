# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('automated_survey', '0003_auto_20150826_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='kind',
            field=models.CharField(choices=[('voice', 'Voice'), ('yes-no', 'Yes or no'), ('numeric', 'Numeric')], max_length=255),
        ),
    ]
