from uuid import UUID
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from backend.models import TimeStampedModel
from quiz.utils import RedisClient


UserModel = get_user_model()


class Quiz(TimeStampedModel):
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    public = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title


class Question(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.text


class Answer(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=128)
    is_answer = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.text


class QuizTaken(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "user"], name="unique_quizzes_for_users"
            )
        ]

    def __str__(self) -> str:
        return str(self.quiz)
    
    def get_redis_key(self):
        return f"quiz.{self.quiz.uuid}.{self.user.uuid}"
    
    def get_user_answers(self):
        question_set = self.quiz.question_set.all()
        results = []
        for question in question_set:
            try:
                results.append(UserAnswer.objects.get(
                    user=self.user,
                    question=question
                ))
            except UserAnswer.DoesNotExist:
                pass

        return results

    def get_quiz_score(self):
        if res := RedisClient.get(self.get_redis_key()):
            return res

        total_count = 0
        count = 0
        for question in self.get_user_answers():
            count += 1
            user_answer_score = question.get_score()
            total_count += user_answer_score
        result = total_count / count
        RedisClient.set(self.get_redis_key(), result)

        return result



class UserAnswer(TimeStampedModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ManyToManyField(Answer)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "user"], name="unique_answered_question_for_users"
            )
        ]

    def __str__(self) -> str:
        return str(self.question)
    
    def get_redis_key(self):
        return f"answer.{self.question.uuid}.{self.user.uuid}"

    def get_score(self):
        if res := RedisClient.get(self.get_redis_key()):
            return res

        total_answers = self.question.answer_set.all()
        correct_answers = total_answers.filter(is_answer=True)
        correct_answers_count = correct_answers.count()
        weight = 0
        unit_weight_gain = round(1 / correct_answers_count, 2)
        unit_weight_loss = round(1 / total_answers.filter(is_answer=False).count(), 2)

        for answer in self.answer.all():
            if correct_answers.filter(uuid=answer.uuid).exists():
                weight += unit_weight_gain
            else:
                weight -= unit_weight_loss
        
        RedisClient.set(self.get_redis_key(), weight)
        
        return weight
