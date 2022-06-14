import shutil
import tempfile
from http import HTTPStatus
from django.conf import settings
from django.urls import reverse
from django.test import TestCase, Client, override_settings
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


class PostFormTestCase(PostsFormBaseTestCase):
    """Тест формы Post"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post_form(self):
        """POST тест валидной формы create_post"""

        post_count = Post.objects.count()
        new_text = 'Создаеём новый пост'
        form_dada = {
            'text': new_text,
            'group': self.group.id,
            'image': self.uploaded,
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

        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            form_data
        )

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
