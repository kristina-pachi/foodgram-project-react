from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class MyUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\Z',),
        ],
    )
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150,)
    last_name = models.CharField(max_length=150,)
    password = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(regex='^[a-zA-Z0-9]*$',),
        ],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)

    def __str__(self) -> str:
        return self.username
