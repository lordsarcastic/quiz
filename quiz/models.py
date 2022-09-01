from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from backend.models import TimeStampedModel


UserModel = get_user_model()


class Quiz(TimeStampedModel):
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    public = models.BooleanField(default=False)


class Question(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)


class Answer(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=128)
    is_answer = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'], name='unique_answers_for_question'),
        ]


class QuizTaken(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['quiz', 'user'], name='unique_quizzes_for_users')
        ]


class UserAnswer(TimeStampedModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)