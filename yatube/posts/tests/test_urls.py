from django.test import TestCase, Client
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.core.cache import cache

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
        cls.user_2 = User.objects.create_user(username='auth_2')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)
        cache.clear()

    def test_homepage(self):
        """smoke test"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_exists_at_desired_location(self):
        """Доступ к страницам не авторизованному пользователю."""
        field_urls = {
            '/':
            HTTPStatus.OK,
            '/group/test_slug/':
            HTTPStatus.OK,
            '/profile/auth/':
            HTTPStatus.OK,
            '/posts/1/':
            HTTPStatus.OK,
            '/unexisting_page/':
            HTTPStatus.NOT_FOUND,
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.guest_client.get(
                        value
                    )
                    .status_code,
                    expected
                )

    def test_post_urls_auterized(self):
        """Доступ к страницам авторизованному пользователю."""
        field_urls = {
            '/':
            HTTPStatus.OK,
            '/group/test_slug/':
            HTTPStatus.OK,
            '/profile/auth/':
            HTTPStatus.OK,
            '/posts/1/':
            HTTPStatus.OK,
            '/create/':
            HTTPStatus.OK,
            '/unexisting_page/':
            HTTPStatus.NOT_FOUND
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.authorized_client.get(
                        value
                    ).status_code,
                    expected
                )

    def test_about_url_anonimus_correct_template(self):
        """Проверка шаблонов страниц не авторизированному пользователю."""
        field_urls = {
            '/':
            'posts/index.html',
            '/group/test_slug/':
            'posts/group_list.html',
            '/profile/auth/':
            'posts/profile.html',
            '/posts/1/':
            'posts/post_detail.html',
            '/abracadabra/':
            'core/404.html'
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(self.guest_client.get(value), expected)

    def test_about_url_autorizad_correct_template(self):
        """Проверка шаблонов страниц авторизированному пользователю."""
        field_urls = {
            '/':
            'posts/index.html',
            '/group/test_slug/':
            'posts/group_list.html',
            '/profile/auth/':
            'posts/profile.html',
            '/posts/1/':
            'posts/post_detail.html',
            '/posts/1/edit/':
            'posts/create_post.html',
            '/create/':
            'posts/create_post.html',
            '/abracadabra/':
            'core/404.html'
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    self.authorized_client.get(
                        value
                    ),
                    expected
                )

    def test_redirect_anonim_in_pivate_page(self):
        """GET тест редиректа с приватных """
        """страницы не авторизованного пользователя"""

        private_urls = [
            ('/create/', HTTPStatus.FOUND),
            ('/posts/1/edit/', HTTPStatus.FOUND)
        ]

        for url, status in private_urls:
            with self.subTest(url=url, status=status):
                self.assertEqual(
                    self.guest_client.get(
                        url
                    ).status_code,
                    status
                )

    def test_edit_post_no_author(self):
        """Не автор не попадает на """
        """страницу редактирования не своего поста """

        response = self.authorized_client_2.get('/posts/1/edit/')

        self.assertRedirects(response, '/posts/1/')
