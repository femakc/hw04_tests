# Generated by Django 2.2.16 on 2022-06-15 19:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0009_auto_20220615_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(help_text='тот на кго подписываются', on_delete='cascade', related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Блогер')),
                ('user', models.ForeignKey(help_text='тот кто подписывается ', on_delete='cascade', related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
            ],
        ),
    ]
