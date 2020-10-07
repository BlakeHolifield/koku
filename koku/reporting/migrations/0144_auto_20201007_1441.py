# Generated by Django 3.1.2 on 2020-10-07 14:41
from django.db import migrations
from django.db import models

import reporting.partition.models


class Migration(migrations.Migration):

    dependencies = [("reporting", "0143_awsorganizationalunit_provider")]

    operations = [
        migrations.AlterField(
            model_name="partitionedtable",
            name="partition_parameters",
            field=models.JSONField(validators=[reporting.partition.models.validate_not_empty]),
        )
    ]
