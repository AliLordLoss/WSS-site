# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-10-22 19:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('WSS', '0002_auto_20201022_1926'),
    ]

    operations = [
        migrations.CreateModel(
            name='HoldingTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='human_pictures/')),
                ('degree', models.CharField(max_length=100)),
                ('place', models.CharField(max_length=100)),
                ('bio', models.TextField()),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_people.speaker_set+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='human_pictures/')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_people.staff_set+', to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Staff',
            },
        ),
        migrations.CreateModel(
            name='TechnicalExpert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='human_pictures/')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_people.technicalexpert_set+', to='contenttypes.ContentType')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='technical_experts', to='people.Role')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='holdingteam',
            name='staff',
            field=models.ManyToManyField(blank=True, related_name='holding_teams', to='people.Staff'),
        ),
        migrations.AddField(
            model_name='holdingteam',
            name='wss',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holding_teams', to='WSS.WSS', verbose_name='WSS'),
        ),
    ]