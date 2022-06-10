from http import HTTPStatus
from django.urls import reverse
from django.test import TestCase, Client
from posts.models import Post, Group
from django.contrib.auth import get_user_model

User = get_user_model()


class PostsFormBaseTestCase(TestCase):
    """Базовый класс для фикстур"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'auth'
        cls.title = 'Тестовая группа'
        cls.slug = 'test_slug'
        cls.description = 'Тестовое описание'
        cls.text = 'Тестовый текст поста'
        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title=cls.title,
            slug=cls.slug,
            description=cls.description,
        )
        cls.group_for_edit = Group.objects.create(
            title='Группа для редактирования',
            slug='edit_slug',
            description='any_descp',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.text,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


class PostFormTestCase(PostsFormBaseTestCase):
    """Тест формы Post"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create_post_form(self):
        """POST тест валидной формы create_post"""

        post_count = Post.objects.count()
        new_text = 'Создаеём новый пост'
        form_dada = {
            'text': new_text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            form_dada,
            follow=True
        )

        self.assertRedirects(response, f'/profile/{self.post.author}/')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.post.refresh_from_db()
        self.assertEqual(Post.objects.latest('pub_date').text, new_text)

    def test_edit_post_form(self):
        """POST тест формы post_edit"""
        post_count = Post.objects.count()
        new_text = 'Изменяем текс поста'
        form_data = {
            'text': new_text,
            'group': self.group_for_edit.id
        }

        response = self.authorized_client.post(reverse('posts:post_edit', kwargs={'post_id': self.post.pk}), form_data)

        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        self.assertEqual(Post.objects.count(), post_count)
        self.post.refresh_from_db()
        self.assertEqual(
            Post.objects.latest(
                'pub_date'
            ).group,
            self.group_for_edit
        )
        self.assertEqual(
            Post.objects.latest(
                'pub_date'
            ).text,
            new_text
        )

    def test_post_error(self):
        """POST error"""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})

        new_text = ''
        data = {
            'text': new_text
        }
        response = self.authorized_client.post(url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        error = response.context.get('form').errors
        self.assertIn('Обязательное поле', str(error))
