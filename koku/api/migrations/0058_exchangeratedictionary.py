# Generated by Django 3.2.13 on 2022-06-13 19:16
from django.db import migrations
from django.db import models

from koku.type_json_transcode import TypedJSONDecoder
from koku.type_json_transcode import TypedJSONEncoder


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0057_add_org_ids"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExchangeRateDictionary",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "currency_exchange_dictionary",
                    models.JSONField(null=True, encoder=TypedJSONEncoder, decoder=TypedJSONDecoder),
                ),
            ],
        ),
    ]
