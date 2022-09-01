from typing import Any, Dict
from rest_framework import serializers

from . import exceptions
from quiz.models import Answer, Question, Quiz


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"
        read_only_fields = ('question',)
    
    def create(self, validated_data):
        print("validated data:", validated_data)
        answer = Answer(
            question=self.context.get("question"),
            **validated_data
        )
        answer.save()
        return answer

class AnswerWithSecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(source="answer_set", many=True)
    class Meta:
        model = Question
        exclude = ("quiz",)


    def create(self, validated_data):
        print(validated_data)
        quiz = self.context.get("quiz")
        question = Question.objects.create(
            quiz=quiz,
            text=validated_data.get("text")
        )
        answers = validated_data.pop("answer_set")
        for answer in answers:
            serialized_answer = AnswerSerializer(data={
                **answer
            }, context={"question": question})
            serialized_answer.is_valid(raise_exception=True)
            serialized_answer.save()
        
        return question


class QuestionOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ("quiz",)


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(source="question_set", many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = "__all__"
        read_only_fields = ("uuid", "owner", "questions")


    # def update(self, instance, validated_data):
    #     return super().update(instance, validated_data)
    
    # def create(self, validated_data: Dict[str, Any]):
    #     questions = validated_data.pop("questions")






# class QuizDetailSerializer