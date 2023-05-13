from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from .managers import UserManager
from .validators import validate_hotmail_or_gmail_email

from core.models import *
from django.core.validators import MinLengthValidator

class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"),validators=[validate_hotmail_or_gmail_email],unique=True)
    first_name = models.CharField(_("first name"), max_length=50,)
    last_name = models.CharField(_("last name"), max_length=50)
    phone_number = models.CharField(_("phone_number"),max_length=10,validators=[MinLengthValidator(10)],unique=True)
    salry = models.PositiveIntegerField(_("salry"))
    pharmacy = models.ForeignKey(Pharmacy,related_name='employees',null=True,blank=True,on_delete=models.CASCADE)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','phone_number','salry']

    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name

    def name(self):
        return self.first_name + ' ' + self.last_name
    