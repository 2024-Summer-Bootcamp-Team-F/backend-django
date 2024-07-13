# Generated by Django 5.0.6 on 2024-07-11 17:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('background', '0001_initial'),
        ('recreated_background', '0003_recreatedbackground_concept_option'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageResizing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('image_url', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('background', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='background.background')),
                ('recreated_background', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recreated_background.recreatedbackground')),
            ],
        ),
    ]