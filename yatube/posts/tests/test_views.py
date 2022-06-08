from http import HTTPStatus
from django.urls import reverse
from django.test import TestCase, Client
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.conf import settings
from django import forms

User = get_user_model()


class PostsBaseTestCase(TestCase):
    """Базовый класс дя фикстур"""
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


class IndexTestCase(PostsBaseTestCase):
    """Тест index views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:index')

    def test_get_success(self):
        """позитивный тест index"""

        response = self.guest_client.get(self.url)

        self.assertTemplateUsed(response, 'posts/index.html')
        self.assertIn('Последние об', response.context.get('title'))
        self.assertEqual(
            len(
                response.context.get(
                    'page_obj'
                )
            ),
            settings.POSTS_IN_PAGE
        )


class GroupPostsTestCase(PostsBaseTestCase):
    """Тест group_list views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:group_list', kwargs={'slug': cls.group.slug})

    def test_get_success(self):
        """позитивный тест group_posts"""

        response = self.guest_client.get(self.url)

        self.assertTemplateUsed(response, 'posts/group_list.html')
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(
            len(
                response.context.get(
                    'page_obj'
                )
            ),
            settings.POSTS_IN_PAGE
        )


class ProfileTestCase(PostsBaseTestCase):
    """Тест profile views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse(
            'posts:profile',
            kwargs={'username': cls.post.author}
        )

    def test_get_success(self):
        """позитивный тест profile"""

        response = self.guest_client.get(self.url)

        self.assertTemplateUsed(response, 'posts/profile.html')
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(
            len(
                response.context.get(
                    'page_obj'
                )
            ),
            settings.POSTS_IN_PAGE
        )


class PostDetailTestCase(PostsBaseTestCase):
    """Тест post_detail views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )

    def test_get_success(self):
        """Позитивный тест post_detail"""

        response = self.guest_client.get(self.url)

        self.assertTemplateUsed(response, 'posts/post_detail.html')
        self.assertEqual(response.context.get('post').id, self.post.pk)


class PostCreateTestCase(PostsBaseTestCase):
    """Тест post_create views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:post_create')

    def test_get_success(self):
        """Позитивный тест post_create"""

        response = self.authorized_client.get(self.url)
        fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        self.assertTemplateUsed(response, 'posts/create_post.html')
        for value, expected in fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(
                    response.context.get('form').fields.get(value), expected
                )

    def test_get_auth(self):
        """GET не авторизованного пользователя create_post"""

        response = self.guest_client.get(self.url)

        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_success(self):
        """POST позитивный тест"""
        post_count = Post.objects.count()
        new_text = 'new_text'
        group = self.group.pk
        data = {
            'text': new_text,
            'group': group
        }
        response = self.authorized_client.post(self.url, data=data)

        self.assertRedirects(response, f'/profile/{self.username}/')
        self.assertEqual(Post.objects.count(), post_count + 1)


class PostEditTestCase(PostsBaseTestCase):
    """Тест post_edit views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:post_edit', kwargs={'post_id': cls.post.pk})

    def test_get_success(self):
        """GET Позитивный тест post_edit"""

        response = self.authorized_client.get(self.url)
        form = response.context.get('form')
        is_edit = response.context.get('is_edit')
        post_in_context = response.context.get('post')
        fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        self.assertEqual(post_in_context.pk, self.post.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')
        self.assertEqual(form.instance, self.post)
        self.assertTrue(is_edit)
        for value, expected in fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(form.fields.get(value), expected)

    def test_get_auth(self):
        """GET не авторизированного пользователя"""

        response = self.guest_client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_success(self):
        """POST запрос редактирования поста"""

        new_text = 'Новый текст'
        data = {
            'text': new_text,
        }
        response = self.authorized_client.post(self.url, data=data)

        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, new_text)

    def test_post_auth(self):
        """POST запрос не авторизированного пользователя"""

        response = self.guest_client.post(self.url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_error(self):
        """POST error"""

        new_text = ''
        data = {
            'text': new_text
        }
        response = self.authorized_client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error = response.context.get('form').errors
        self.assertIn('Обязательное поле', str(error))
