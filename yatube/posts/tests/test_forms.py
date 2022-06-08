from django.urls import reverse
from django.test import TestCase, Client
from posts.models import Post, Group
from django.contrib.auth import get_user_model

User = get_user_model()


class PostsFormBaseTestCase(TestCase):
    post_count = 13

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
        for i in range(cls.post_count):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'{i} {cls.text}',
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


class CreatePostFormTestCase(PostsFormBaseTestCase):
    """Тест формы Post """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:post_create')

    def test_post_form(self):
        """POST тест валидной формы"""

        post_count = Post.objects.count()
        new_text = 'new_text'
        form_dada = {
            'text': new_text
        }
        response = self.authorized_client.post(
            self.url,
            form_dada,
            follow=True
        )

        self.assertRedirects(response, f'/profile/{self.post.author}/')
        self.assertEqual(Post.objects.count(), post_count + 1)


class EditPostFormTestCase(PostsFormBaseTestCase):
    """Тесты для формы post_edit"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:post_edit', kwargs={'post_id': cls.post.pk})

    def test_edit_post_form(self):
        """POST тест формы post_edit"""
        post_count = Post.objects.count()
        new_text = 'Новый текст поста'
        form_data = {
            'text': new_text
        }

        response = self.authorized_client.post(self.url, form_data)

        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(self.post.pk, post_count)
