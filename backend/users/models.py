from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    ROLES = (('user', 'USER'), ('admin', 'ADMIN'))

    email = models.EmailField(max_length=254, unique=True, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    role = models.CharField(max_length=300, choices=ROLES, default=ROLES[0][0])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = UserManager()

    @property
    def is_admin(self):
        return self.is_superuser or self.role == 'admin'

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

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=('user', 'following'),
                                    name='unique_subscription')
        ]

    def __str__(self):
        return f'{self.user} {self.following}'
