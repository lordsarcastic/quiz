from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.postgres.fields import CICharField
from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.models import SlugifiedModel, TimeStampedModel

from .validators import username_regex


class User(AbstractUser, TimeStampedModel, SlugifiedModel):
    """
    Custom user created with email as the username field
    """

    username = CICharField(
        _("username"),
        unique=True,
        max_length=31,
        validators=[ASCIIUsernameValidator(), username_regex],
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        max_length=100,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    SLUG_FIELD = "username"

    def __str__(self) -> str:
        return f"{self.username} | {self.email}"
