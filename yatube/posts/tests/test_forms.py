import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings as s
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=s.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Создаем тестовые сообщение, группу и форму"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='serg')

        cls.group = Group.objects.create(
            title='Test Group',
            slug='Test',
            description='Description for Test Group'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиент гостя и зарегистрированного пользователя"""
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized(self):
        """Убедимся в отсутствии сообщений и создадим сообщение в Post"""
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xF9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x01\x00\x3b\x02\x0C'
            b'\x0A\x00\x3B'
        )
        upload = SimpleUploadedFile(
            name='test.gif',
            content=test_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новое сообщение',
            'group': self.group.pk,
            'image': upload,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group,
                author=self.user,
                image='posts/test.gif',
            ).exists()
        )

    def test_create_post_unauthorized(self):
        """Пытаемся создать запись в Post"""
        form_data = {
            'text': 'Новое сообщение',
            'group': self.group.pk,
        }
        response = self.unauthorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next='
            + reverse('posts:post_create')
        )

    def test_edit_post(self):
        Post.objects.create(
            author=self.user,
            text='Тестовое сообщение',
            group=self.group
        )
        form_data = {
            'text': 'Измененное сообщение',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk='1')
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        self.assertEqual(
            post.text,
            form_data['text']
        )
        self.assertEqual(
            post.group.pk,
            form_data['group']
        )
        self.assertEqual(
            post.author,
            self.user
        )


class CommentFormTests(PostFormTests):
    def test_comment_for_registered_users(self):
        """Комментарии могут оставлять зарегистрированные пользователи"""
        post_tst = Post.objects.create(
            author=self.user,
            text='Тестовое сообщение',
            group=self.group
        )
        form_data = {'text': 'Тестовый комментарий'}
        response = self.authorized_client.post(
            reverse(
                'posts:ad_comment',
                kwargs={'post_id': '1'}
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ),
            HTTPStatus.FOUND
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertTrue(Comment.objects.filter(text=form_data.get('text')))
        self.assertTrue(Comment.objects.filter(author=self.user))
        self.assertTrue(Comment.objects.filter(post=post_tst))

    def test_comment_cant_comment(self):
        """Комментарии не могут оставлять гости"""
        Post.objects.create(
            author=self.user,
            text='Тестовое сообщение',
            group=self.group
        )
        form_data = {
            'text': 'тестовый комментарий',
        }
        reverse_name = reverse(
            'posts:ad_comment',
            kwargs={'post_id': '1'}
        )
        response = self.unauthorized_client.post(
            reverse_name,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next='
            + reverse('posts:ad_comment', kwargs={'post_id': '1'}),
            HTTPStatus.FOUND
        )
        self.assertEqual(Comment.objects.count(), 0)
