from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Сообщение',
        help_text='Текст сообщения'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации сообщения'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор сообщения',
        help_text='Автор публиковавший сообщение'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа принадлежности сообщения'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
        help_text='Картинка для сообщения'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:30]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Группа',
        help_text='Название группы'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Группа',
        help_text='Уникальное название группы'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы'
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Сообщение для комментариев',
        help_text='Сообщение для комментариев'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор комментария',
        help_text='Автор комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст комментария',
        null=False
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
        help_text='Дата публикации комментария'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Автор комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор комментируемого сообщения'
    )

    class Meta:
        verbose_name = 'follower'
        verbose_name_plural = 'followers'

    def __str__(self):
        return f'{self.user.username}, {self.author.username}'
