from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from .managers import UserManager
from .validators import validate_hotmail_or_gmail_email

class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"),validators=[validate_hotmail_or_gmail_email],unique=True)
    first_name = models.CharField(_("first name"), max_length=50)
    last_name = models.CharField(_("last name"), max_length=50)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name

