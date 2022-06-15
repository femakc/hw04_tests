# Generated by Django 2.2.16 on 2022-06-14 10:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0006_post_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Текст комментария', verbose_name='Комментарий')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Дата', verbose_name='Дата создания')),
                ('author', models.ForeignKey(help_text='Автор', on_delete='cascade', related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор поста')),
                ('post', models.ForeignKey(blank=True, help_text='Пост к которому относится коментарий', null=True, on_delete='cascade', related_name='comments', to='posts.Post', verbose_name='Пост')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['-created'],
            },
        ),
    ]
