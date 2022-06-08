from django.test import TestCase, Client
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Доступ к статичным страницам не авторизованному пользователю."""
        field_urls = {
            self.guest_client.get('/about/author/'):
            HTTPStatus.OK,
            self.guest_client.get('/about/tech/'):
            HTTPStatus.OK,
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertEqual(value.status_code, expected)

    def test_about_url_anonimus_correct_template(self):
        """Проверка шаблонов статичных страниц."""
        field_urls = {
            self.guest_client.get('/about/author/'):
            'about/author.html',
            self.guest_client.get('/about/tech/'):
            'about/tech.html',
        }
        for value, expected in field_urls.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(value, expected)
