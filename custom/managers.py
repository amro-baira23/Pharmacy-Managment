from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, first_name, last_name, phone_number, salry, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        if not first_name:
            raise ValueError('The given first_name must be set')
        if not last_name:
            raise ValueError('The given last_name must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number, salry=salry,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, phone_number, salry, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, first_name, last_name, phone_number, salry, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, phone_number, salry, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, first_name, last_name, phone_number, salry, **extra_fields)
    