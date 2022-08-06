from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):
    username = models.CharField(verbose_name='Username',
                                unique=True, max_length=150)
    email = models.EmailField(max_length=254, unique=True, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

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
        related_name='subscriber',
        blank=True, null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        blank=True, null=True
    )
    created = models.DateTimeField(
        auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created']

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name="unique_subscribers")
        ]

    def __str__(self):
        return f'{self.user} subscribed_to {self.author}'
