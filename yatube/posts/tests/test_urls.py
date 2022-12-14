from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    """Создаем тестовые сообщение и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='serg')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новое сообщение без группы'
        )
        cls.group = Group.objects.create(
            title='Test Group',
            slug='Test',
            description='Description for Test Group'
        )

    def setUp(self):
        """Создаем клиент гостя и зарегистрированного пользователя"""
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_response_guest(self):
        """Проверяем статус страниц для гостя"""
        url_status = {
            '/': HTTPStatus.OK,
            '/group/' + self.group.slug + '/': HTTPStatus.OK,
            '/profile/' + self.user.username + '/': HTTPStatus.OK,
            '/posts/' + str(self.post.pk) + '/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            '/posts/' + str(self.post.pk) + '/edit/': HTTPStatus.FOUND,
            '/unexpecting_page/': HTTPStatus.NOT_FOUND,
            '/posts/' + str(self.post.pk) + '/comment/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.FOUND,
            '/profile/' + self.user.username + '/follow/': HTTPStatus.FOUND,
            '/profile/' + self.user.username + '/unfollow/': HTTPStatus.FOUND
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.unauthorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_response_guest_redirect(self):
        """Проверяем редирект страниц для гостя"""
        url_redirect = {
            '/posts/' + str(self.post.pk) + '/edit/':
                '/auth/login/' + '?next='
                + '/posts/' + str(self.post.pk) + '/edit/',
            '/create/': '/auth/login/' + '?next=' + '/create/'
        }
        for url, redirect_url in url_redirect.items():
            with self.subTest(url=url):
                response = self.unauthorized_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_urls_response_auth(self):
        """Проверяем статус страниц для зарегистрированного пользователя"""
        url_status = {
            '/posts/' + str(self.post.pk) + '/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/posts/' + str(self.post.pk) + '/comment/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.OK,
            '/profile/' + self.user.username + '/follow/': HTTPStatus.FOUND,
            '/profile/' + self.user.username + '/unfollow/': HTTPStatus.FOUND
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """Проверяем запрашиваемые шаблоны страниц через имена"""
        templates_pages_names = {
            '/': 'posts/index.html',
            '/group/' + self.group.slug + '/': 'posts/group_list.html',
            '/profile/' + self.user.username + '/': 'posts/profile.html',
            '/posts/' + str(self.post.pk) + '/': 'posts/post_detail.html',
            '/posts/' + str(self.post.pk) + '/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_404_nonexistent_page(self):
        """Проверка кастомной страницы 404"""
        url = '/unexisting_page/'
        roles = (
            self.unauthorized_client,
            self.authorized_client
        )
        for role in roles:
            with self.subTest(url=url):
                response = role.get(url, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertTemplateUsed(response, 'core/404.html')
