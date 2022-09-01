from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver

from . import exceptions
from quiz.models import Quiz


@receiver(pre_save, sender=Quiz)
def resident_pre_save(sender, instance: Quiz, **kwargs):
    if instance.question_set.count() > settings.MAX_QUESTION_PER_QUIZ:
        raise exceptions.MAX_QUESTIONS_LIMIT_REACHED
