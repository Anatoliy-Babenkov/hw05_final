import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings as s
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Post, Group, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=s.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    """Создаем тестовые сообщение и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        test_pic = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xF9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x01\x00\x3b\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.upload = SimpleUploadedFile(
            name='test.gif',
            content=test_pic,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='serg')
        cls.user_another = User.objects.create_user(username='andr')
        cls.group = Group.objects.create(
            title='Test Group',
            slug='Test',
            description='Description for Test Group'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новое сообщение без группы',
            group=cls.group,
            image=cls.upload
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя"""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)
        self.authorized_client_another = Client()
        self.authorized_client_another.force_login(PostViewTests.user_another)
        cache.clear()

    def message_attribute_check(self, post):
        """Проверка атрибутов сообщения на страницах"""
        self.assertEqual(
            post.author,
            PostViewTests.post.author
        )
        self.assertEqual(
            post.text,
            PostViewTests.post.text
        )
        self.assertEqual(
            post.group,
            PostViewTests.post.group
        )
        self.assertEqual(
            post.image,
            PostViewTests.post.image
        )

    def test_index_show_correct_context(self):
        """Шаблон index сформирован корректно"""
        response_index = self.authorized_client.get(reverse('posts:index'))
        page_index_context = response_index.context
        post = page_index_context['page_obj'][0]
        self.message_attribute_check(post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован корректно"""
        response_post_detail = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.post.pk}
            )
        )
        page_post_detail_context = response_post_detail.context
        post = page_post_detail_context['post']
        self.message_attribute_check(post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован корректно"""
        response_group = self.authorized_client.get(
            reverse(
                'posts:post_group',
                kwargs={'slug': PostViewTests.group.slug}
            )
        )
        page_group_context = response_group.context
        task_group = response_group.context['group']
        post = page_group_context['page_obj'][0]
        self.message_attribute_check(post)
        self.assertEqual(task_group, PostViewTests.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован корректно"""
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        )
        page_profile_context = response_profile.context
        task_profile = response_profile.context['author']
        post = page_profile_context['page_obj'][0]
        self.message_attribute_check(post)
        self.assertEqual(task_profile, PostViewTests.user)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован корректно"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован корректно"""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewTests.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_users_can_follow(self):
        """Зарегистрированный пользователь может подписаться"""
        followers = Follow.objects.count()
        response = self.authorized_client_another.get(
            reverse('posts:profile_follow', args=(self.user,))
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.user,)),
            HTTPStatus.FOUND
        )
        self.assertEqual(Follow.objects.count(), followers + 1)
        response = self.authorized_client_another.get(
            reverse('posts:follow_index'))
        self.assertContains(response, self.user)

    def test_users_can_unfollow(self):
        """Зарегистрированный пользователь может отписаться"""
        Follow.objects.create(
            user=self.user_another,
            author=self.user
        )
        followers = Follow.objects.count()
        response = self.authorized_client_another.get(
            reverse('posts:profile_unfollow', args=(self.user,))
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.user,)),
            HTTPStatus.FOUND
        )
        self.assertEqual(Follow.objects.count(), followers - 1)
        response = self.authorized_client_another.get(
            reverse('posts:follow_index'))
        self.assertNotContains(response, self.user)

    def test_post_appears_at_follower_profile(self):
        """Сообщение появляется в ленте подписчика"""
        Follow.objects.create(
            user=self.user_another,
            author=self.user
        )
        response = self.authorized_client_another.get(
            reverse('posts:follow_index')
        )
        self.assertContains(response, self.post)
        Follow.objects.filter(
            user=self.user_another,
            author=self.user
        ).delete()
        response = self.authorized_client_another.get(
            reverse('posts:follow_index')
        )
        self.assertNotContains(response, self.post)


class PaginatorViewTests(TestCase):
    """Создаем тестовые сообщение и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='serg')
        cls.group = Group.objects.create(
            title='Test Group',
            slug='Test',
            description='Description for Test Group'
        )

        cls.second_page_numbers = s.NUMBER_MESSAGES - 2
        cls.all_messages = s.NUMBER_MESSAGES + cls.second_page_numbers
        paginator_objects = []

        for i in range(cls.all_messages):
            new_post = Post(
                author=PaginatorViewTests.user,
                text='Тестовое сообщение ' + str(i),
                group=PaginatorViewTests.group
            )
            paginator_objects.append(new_post)

        Post.objects.bulk_create(paginator_objects)

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя"""
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewTests.user)

    def test_paginator_correct_context(self):
        """Шаблон index, group_list и profile
        сформированы с корректным Перелистывателем.
        """
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:post_group',
                kwargs={'slug': PaginatorViewTests.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewTests.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.authorized_client.get(paginator_page)
                response_page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']),
                    s.NUMBER_MESSAGES
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']),
                    self.second_page_numbers
                )

    def test_cache(self):
        """Проверка работы кэша"""
        post = Post.objects.create(
            author=self.user,
            text='Сообщение для проверки кэша',
            group=self.group
        )
        response_1 = self.client.get(reverse('posts:index'))
        self.assertTrue(Post.objects.get(pk=post.pk))
        Post.objects.get(pk=post.pk).delete()
        cache.clear()
        response_2 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response_1.content, response_2.content)
