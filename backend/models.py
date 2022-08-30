from uuid import uuid4
from django.db import models
from django.template.defaultfilters import slugify


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True)

    class Meta:
        abstract = True


class TimeStampedModel(BaseModel):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created']


class SlugifiedModel(BaseModel):
    """
    An abstract base class that provides slugs from names field
    """

    slug = models.SlugField(blank=True, max_length=128, unique=True)
    SLUG_FIELD = "name"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.slug = slugify(getattr(self, self.SLUG_FIELD))
        super().save(*args, **kwargs)