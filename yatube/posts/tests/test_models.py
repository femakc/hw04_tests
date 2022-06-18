from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post, Group

User = get_user_model()


class PostBaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.text = 'Тестовый текст поста'
        cls.username = 'auth'
        cls.title = 'Тестовая группа'
        cls.slug = 'Тестовый слаг'

        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title=cls.title,
            slug=cls.slug,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.text,
        )


class PostModelTestCase(PostBaseTestCase):
    """ Класс для тестирования модели Post"""

    def test_str(self):
        """Тест отображения модели Post и Group"""
        results = {
            str(self.post): self.text[:15],
            str(self.group): self.title
        }
        for value, expected in results.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_verbose_name_post(self):
        """verbose_name модели Post в полях совпадает с ожидаемым."""

        field_verboses = {
            'text': 'Пост',
            'created': 'Дата создания',
            'author': 'Автор поста',
            'group': 'Группа',
        }

        post = self.post

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text модели Post в полях совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'created': 'Дата',
            'author': 'Автор',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTestCase(PostBaseTestCase):
    """ Класс для тестирования модели Group"""

    def test_verbose_name_group(self):
        """verbose_name модели Group в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Адрес для страницы с постами',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_group(self):
        """help_text модели Group в полях совпадает с ожидаемым."""
        group = self.group
        field_help_texts = {
            'title': 'Заголовок сообщест',
            'slug': 'Адрес сообщест',
            'description': 'Описание сообщест',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
