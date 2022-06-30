from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):
    username = models.CharField(verbose_name='Имя пользователя',
                                unique=True, max_length=150)
    email = models.EmailField(max_length=254, unique=True, blank=False,
                              verbose_name='Адрес электронной почты',)
    first_name = models.CharField(max_length=150, blank=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=False,
                                 verbose_name='Фамилия',)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    objects = UserManager()

    @property
    def is_admin(self):
        return self.is_superuser or self.role == ADMIN

    def __str__(self):
        return self.username


class Subscription(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Выберите автора, на которого подписываются'
    )

    class Meta:
        ordering = ('following',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=('user', 'following'),
                                    name='unique_subscription')
        ]

    def __str__(self):
        return f'{self.user} {self.following}'
