from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    """Создаем тестовые сообщение и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='serg')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новое сообщение без группы'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:30])

    def test_models_have_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Сообщение',
            'pub_date': 'Дата публикации',
            'author': 'Автор сообщения',
            'group': 'Группа',
            'image': 'Картинка'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_models_have_help_text(self):
        """help_text в полях совпадает с ожидаемым"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст сообщения',
            'pub_date': 'Дата публикации сообщения',
            'author': 'Автор публиковавший сообщение',
            'group': 'Группа принадлежности сообщения',
            'image': 'Картинка для сообщения'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    """Создаем тестовый пост и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test Group',
            slug='Test',
            description='Description for Test Group'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        group = GroupModelTest.group
        self.assertEqual(str(group), group.title)

    def test_models_have_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым"""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Группа',
            'slug': 'Группа',
            'description': 'Описание'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_models_have_help_text(self):
        """help_text в полях совпадает с ожидаемым"""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Название группы',
            'slug': 'Уникальное название группы',
            'description': 'Описание группы'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)


class CommentModelTest(TestCase):
    """Создаем тестовый пост и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='serg')
        cls.user_another = User.objects.create_user(username='andr')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое сообщение'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_another,
            text='Тестовый комментарий',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        comment = CommentModelTest.comment
        self.assertEqual(str(comment), comment.text[:15])

    def test_models_have_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым"""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Сообщение для комментариев',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата публикации комментария'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_models_have_help_text(self):
        """help_text в полях совпадает с ожидаемым"""
        comment = CommentModelTest.comment
        field_help_texts = {
            'post': 'Сообщение для комментариев',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата публикации комментария'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value)


class FollowModelTest(TestCase):
    """Создаем тестовый пост и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='serg')
        cls.user_another = User.objects.create_user(username='andr')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_another
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        follow = FollowModelTest.follow
        self.assertEqual(str(follow), f'{self.user}, {self.user_another}')

    def test_models_have_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым"""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_models_have_help_text(self):
        """help_text в полях совпадает с ожидаемым"""
        follow = FollowModelTest.follow
        field_help_texts = {
            'user': 'Автор комментария',
            'author': 'Автор комментируемого сообщения'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).help_text, expected_value)
