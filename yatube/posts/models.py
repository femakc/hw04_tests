from tkinter import CASCADE
from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Заголовок сообщест'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес для страницы с постами',
        help_text='Адрес сообщест'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание сообщест'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


class Post(CreatedModel):
    text = models.TextField(
        verbose_name="Пост",
        help_text='Текст нового поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор поста",
        help_text='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name="Группа",
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-created']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name="Пост",
        help_text='Пост к которому относится коментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name="Автор поста",
        help_text='Автор'
    )
    text = models.TextField(
        verbose_name="Комментарий",
        help_text='Текст комментария'
    )

    def __str__(self):
        return "Комментарий"

    class Meta:
        ordering = ['-created']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
        help_text='тот кто подписывается '
    )
    author = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following',
        verbose_name="Блогер",
        help_text='тот на кого подписываются'
    )

    def __str__(self):
        return 'Подписки'

    class Meta:
        verbose_name = 'follow'
        verbose_name_plural = 'follows'
