from django.test import TestCase, Client
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class URLTests(TestCase):
    """Тесты URLs"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        """smoke test"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_exists_at_desired_location(self):
        """Доступ к страницам не авторизованному пользователю."""
        field_urls = {
            self.guest_client.get('/'):
            HTTPStatus.OK,
            self.guest_client.get('/group/test_slug/'):
            HTTPStatus.OK,
            self.guest_client.get('/profile/auth/'):
            HTTPStatus.OK,
            self.guest_client.get('/posts/1/'):
            HTTPStatus.OK,
            self.guest_client.get('/unexisting_page/'):
            HTTPStatus.NOT_FOUND,
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertEqual(value.status_code, expected)

    def test_post_urls_auterized(self):
        """Доступ к страницам авторизованному пользователю."""
        field_urls = {
            self.authorized_client.get('/'):
            HTTPStatus.OK,
            self.authorized_client.get('/group/test_slug/'):
            HTTPStatus.OK,
            self.authorized_client.get('/profile/auth/'):
            HTTPStatus.OK,
            self.authorized_client.get('/posts/1/'):
            HTTPStatus.OK,
            self.authorized_client.get('/unexisting_page/'):
            HTTPStatus.NOT_FOUND,
            self.authorized_client.get('/create/'):
            HTTPStatus.OK,
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertEqual(value.status_code, expected)

    def test_about_url_anonimus_correct_template(self):
        """Проверка шаблонов страниц не авторизированному пользователю."""
        field_urls = {
            self.guest_client.get('/'):
            'posts/index.html',
            self.guest_client.get('/group/test_slug/'):
            'posts/group_list.html',
            self.guest_client.get('/profile/auth/'):
            'posts/profile.html',
            self.guest_client.get('/posts/1/'):
            'posts/post_detail.html',
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(value, expected)

    def test_about_url_autorizad_correct_template(self):
        """Проверка шаблонов страниц авторизированному пользователю."""
        field_urls = {
            self.authorized_client.get('/'):
            'posts/index.html',
            self.authorized_client.get('/group/test_slug/'):
            'posts/group_list.html',
            self.authorized_client.get('/profile/auth/'):
            'posts/profile.html',
            self.authorized_client.get('/posts/1/'):
            'posts/post_detail.html',
            self.authorized_client.get('/posts/1/edit/'):
            'posts/create_post.html',
            self.authorized_client.get('/create/'):
            'posts/create_post.html',
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(value, expected)
