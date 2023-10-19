from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Кастомная модель пользователя."""

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[validate_username])
    first_name = models.CharField(
        'Имя',
        max_length=150)
    last_name = models.CharField(
        'Фамилия',
        max_length=150)
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        blank=False)
    password = models.CharField(
        'Пароль',
        max_length=150,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Класс для подписки на авторов."""

    subscriber = models.ForeignKey(
        User,
        related_name='subscriber',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='author',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_subscriber_author'
            )
        ]

    def __str__(self) -> str:
        return f'Подписка {self.subscriber.username} на {self.author.username}'
