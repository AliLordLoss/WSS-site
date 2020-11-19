# Generated by Django 3.1.3 on 2020-11-18 18:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WSS', '0006_auto_20201116_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wss',
            name='registration_fee',
            field=models.PositiveIntegerField(default=10000, validators=[django.core.validators.MinValueValidator(1000)]),
        ),
    ]