from django.db.utils import IntegrityError

from rest_framework import serializers, status, exceptions as errors
from rest_framework.exceptions import ValidationError

from .models import Answer, Question, Quiz, QuizTaken, UserAnswer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"
        read_only_fields = ("question",)

    def create(self, validated_data):
        answer = Answer(question=self.context.get("question"), **validated_data)
        answer.save()
        return answer


class PublicAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        exclude = ("is_answer",)


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(source="answer_set", many=True)

    class Meta:
        model = Question
        exclude = ("quiz",)

    def create(self, validated_data):
        quiz = self.context.get("quiz")
        question = Question.objects.create(quiz=quiz, text=validated_data.get("text"))
        answers = validated_data.pop("answer_set")

        if len(answers) > 5:
            raise ValidationError("Answers must not be more than 5")

        for answer in answers:
            serialized_answer = AnswerSerializer(
                data={**answer}, context={"question": question}
            )
            serialized_answer.is_valid(raise_exception=True)
            serialized_answer.save()

        return question


class PublicQuestionSerializer(serializers.ModelSerializer):
    answers = PublicAnswerSerializer(source="answer_set", many=True, read_only=True)

    class Meta:
        model = Question
        fields = "__all__"


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


class QuizOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "__all__"
        read_only_fields = (
            "uuid",
            "owner",
            "is_public"
        )


class PublicQuizSerializer(serializers.ModelSerializer):
    questions = PublicQuestionSerializer(
        source="question_set", many=True, read_only=True
    )

    class Meta:
        model = Quiz
        fields = "__all__"


class TakenAnswerSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=False)
    
    def create(self, validated_data):
        instance = Answer.objects.filter(uuid=validated_data.get("uuid"))
        if not instance.exists():
            raise ValidationError("Answer does not exist")

        if (result := instance.first()).question != self.context.get("question"):
            raise ValidationError("Answer is not related to question")
        
        return result

class SingleQuestionSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    answers = TakenAnswerSerializer(allow_empty=False, many=True)
    
    def create(self, validated_data):
        instance = Question.objects.filter(uuid=validated_data.get("uuid"))

        if not instance.exists():
            raise ValidationError("Question does not exist")
        
        if (instance := instance.first()).quiz != self.context.get("quiz"):
            raise ValidationError("Question is not related to quiz")

        answers = validated_data.get("answers")

        try:
            user_answer = UserAnswer.objects.create(
                user=self.context.get("user"),
                question=instance,
            )

            for answer in answers:
                answer_serialized = TakenAnswerSerializer(data={
                    **answer
                }, context={"question": instance})
                answer_serialized.is_valid(raise_exception=True)
                result = answer_serialized.save()
                user_answer.answer.add(result)
        except IntegrityError:
            raise ValidationError("User has already answered this quiz")
        
        return user_answer


class SingleQuizSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    questions = SingleQuestionSerializer(allow_empty=False, many=True)
    
    def create(self, validated_data):
        quiz = Quiz.objects.filter(uuid=validated_data.get("uuid"))

        if not quiz.exists():
            raise errors.NotFound("Quiz does not exist", code=status.HTTP_404_NOT_FOUND)
        
        quiz = quiz.first()
        questions = validated_data.get("questions")

        for question in questions:
            question_serialized = SingleQuestionSerializer(data={
                **question
            }, context={"quiz": quiz, "user": self.context.get("user")})
            question_serialized.is_valid(raise_exception=True)
            question_serialized.save()
        
        QuizTaken.objects.create(
            quiz=quiz,
            user=self.context.get("user")
        )

        return validated_data


class TakeQuizSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    answers = TakenAnswerSerializer(allow_empty=False, many=True)

    class Meta:
        model = Quiz
        exclude = ("user",)


class QuestionScoreSerializer(serializers.ModelSerializer):
    score = serializers.FloatField(source="get_score")

    class Meta:
        model = UserAnswer
        fields = ("answer", "question", "score")
        read_only_fields = ("score",)

class TotalScoreSerializer(serializers.ModelSerializer):
    score = serializers.FloatField(source="get_quiz_score")
    question = QuestionScoreSerializer(source="get_user_answers", many=True)
    class Meta:
        model = QuizTaken
        fields = ("quiz", "user", "score", "question")
        read_only_fields = ("score", "question")

