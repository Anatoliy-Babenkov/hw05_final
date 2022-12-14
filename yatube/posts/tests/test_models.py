from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    """Создаем тестовые сообщение и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новое сообщение без группы'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:15])

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
