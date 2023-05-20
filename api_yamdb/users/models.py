from api.utils import username_validation
from django.contrib.auth.models import AbstractUser

from django.db import models


class Role(models.TextChoices):
    """Выбор ролей"""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    """Кастомная модель User"""

    username = models.CharField(
        max_length=32,
        unique=True,
        validators=(username_validation,),
    )
    first_name = models.CharField(
        max_length=32,
        default='user_name_default'
    )
    last_name = models.CharField(
        max_length=64,
        default='user_last_name_default'
    )
    email = models.EmailField(
        verbose_name='email_address',
        blank=False,
        unique=True,
        max_length=254,
    )
    bio = models.TextField('bio', blank=True)
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.USER,
    )

    class Meta:
        unique_together = ('username',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_user(self):
        return self.role == Role.USER

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR

    @property
    def is_admin(self):
        return (self.role == Role.ADMIN
                or self.is_superuser
                or self.is_staff
                )
