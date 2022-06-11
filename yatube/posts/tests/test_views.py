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
    posts_on_second_page = 4

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
        posts_list = []
        for i in range(self.post_count):
            posts_list.append(
                Post(
                    author=self.user,
                    text=f'{i} {self.text}',
                    group=self.group
                )
            )
        Post.objects.bulk_create(posts_list)
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
        context = response.context

        self.assertTemplateUsed(response, 'posts/index.html')
        self.assertIn('Последние об', context.get('title'))
        self.assertEqual(
            len(
                context.get(
                    'page_obj'
                )
            ),
            settings.POSTS_IN_PAGE
        )

    def test_content(self):
        """Подробная проверка полей поста"""

        response = self.guest_client.get(self.url)
        context = response.context
        post_list = context.get('page_obj')

        for post in post_list:
            with self.subTest(post=post):
                self.assertIn(self.text, post.text)
                self.assertEqual(self.group, post.group)
                self.assertEqual(self.user, post.author)

    def test_paginator_secong_page(self):
        """Тест второй страницы на кольчество постов"""
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        context = response.context

        self.assertEqual(
            len(
                context.get(
                    'page_obj'
                )
            ),
            self.posts_on_second_page
        )


class GroupPostsTestCase(PostsBaseTestCase):
    """Тест group_list views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:group_list', kwargs={'slug': cls.group.slug})
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Текст второй группы',
            group=cls.group_for_edit
        )

    def test_get_success(self):
        """позитивный тест group_posts"""

        response = self.guest_client.get(self.url)
        context = response.context
        post_list = context.get('page_obj')

        for value in post_list:
            with self.subTest(value=value):
                self.assertNotEqual(self.post_2.pk, value.pk)
        self.assertTemplateUsed(response, 'posts/group_list.html')
        self.assertEqual(context.get('group'), self.group)
        self.assertEqual(
            len(
                context.get(
                    'page_obj'
                )
            ),
            settings.POSTS_IN_PAGE
        )

    def test_paginator_secong_page(self):
        """Тест второй страницы на кольчество постов"""

        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
            + '?page=2'
        )
        context = response.context
        post_list = context.get('page_obj')

        for value in post_list:
            with self.subTest(value=value):
                self.assertNotEqual(self.post_2.pk, value.pk)
        self.assertEqual(
            len(
                context.get(
                    'page_obj'
                )
            ),
            4
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
        context = response.context

        self.assertTemplateUsed(response, 'posts/profile.html')
        self.assertEqual(context.get('author'), self.user)
        self.assertEqual(
            len(
                context.get(
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
        context = response.context

        self.assertTemplateUsed(response, 'posts/post_detail.html')
        self.assertEqual(context.get('post').id, self.post.pk)


class PostCreateTestCase(PostsBaseTestCase):
    """Тест post_create views"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('posts:post_create')

    def test_get_success(self):
        """Позитивный тест GET post_create"""

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

    def test_get_anonimus(self):
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
# комит тест