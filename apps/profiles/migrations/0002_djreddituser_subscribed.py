# Generated by Django 3.2.15 on 2022-08-26 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='djreddituser',
            name='subscribed',
            field=models.ManyToManyField(to='posts.Thread'),
        ),
    ]
