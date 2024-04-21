from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone
from datetime import timedelta


# Create your models here.
class CustomUserManager(BaseUserManager):

    def create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError(_('User must have an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        user = self.create_user(email, password, **extra_fields)
        return user


class Users(AbstractUser):
    username = None
    email = models.EmailField(verbose_name=_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.get_full_name()


def get_default_expired_at():
    return timezone.now() + timedelta(minutes=10)


class Activation(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    activation_code = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(default=get_default_expired_at)

    def __str__(self):
        return self.activation_code


class PasswordReset(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    reset_code = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(default=get_default_expired_at)

    def __str__(self):
        return self.reset_code
