from rest_framework import serializers

from . import exceptions
from quiz.models import Answer, Question, Quiz


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        exclude = ('is_answer', 'id')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    class Meta:
        model = Question
        fields = '__all__'
        


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ('uuid', 'owner', 'questions')





# class QuizDetailSerializer