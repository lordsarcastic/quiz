from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from .mixins import MultipleFieldLookupMixin
from .models import Answer, Question, Quiz, QuizTaken
from .permissions import (
    AdaptedMethodIsOwnerOfQuizFromQuestionOrPublic,
    IsOwner,
    IsOwnerOfAnswerOrPublic,
    IsOwnerOfQuestion,
    IsOwnerOfQuiz,
)
from .serializers import (
    AnswerSerializer,
    PublicQuestionSerializer,
    PublicQuizSerializer,
    QuestionOnlySerializer,
    QuestionSerializer,
    QuizOnlySerializer,
    QuizSerializer,
    SingleQuizSerializer,
    TotalScoreSerializer,
)


class ListCreateQuizAPI(generics.ListCreateAPIView):
    serializer_class = QuizOnlySerializer
    queryset = Quiz.objects.filter(public=True)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RetrieveUpdateDestroyQuizAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = "uuid"

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


class PublicRetrieveQuizAPI(generics.RetrieveAPIView):
    serializer_class = PublicQuizSerializer
    queryset = Quiz
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"


class CreateQuestionAPI(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    queryset = Question
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfQuiz]

    def post(self, request: Request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs.get("uuid"))
        serializer = self.serializer_class(data=request.data, context={"quiz": quiz})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDestroyQuestionAPI(
    MultipleFieldLookupMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = QuestionSerializer
    queryset = Question
    permission_classes = [
        permissions.IsAuthenticated,
        AdaptedMethodIsOwnerOfQuizFromQuestionOrPublic,
    ]
    lookup_fields = ["quiz__uuid", "uuid"]

    def get_serializer_class(self):
        if self.request.method.upper() == "GET":
            return QuestionSerializer
        return QuestionOnlySerializer


class PublicRetrieveQuestionAPI(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    serializer_class = PublicQuestionSerializer
    queryset = Question
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfAnswerOrPublic]
    lookup_fields = ["quiz__uuid", "uuid"]


class CreateAnswerAPI(MultipleFieldLookupMixin, generics.CreateAPIView):
    serializer_class = AnswerSerializer
    queryset = Answer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfQuestion]
    lookup_fields = ["question__quiz__uuid", "question__uuid"]

    def post(self, request, *args, **kwargs):
        get_object_or_404(Quiz, pk=kwargs.get("quiz_uuid"))
        question = get_object_or_404(Question, pk=kwargs.get("question_uuid"))
        serializer = self.serializer_class(
            data=request.data, context={"question": question}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDestroyAnswerAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnswerSerializer
    queryset = Answer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfQuestion]
    lookup_fields = ["question__quiz__uuid", "question__uuid"]


class TakeQuizAPI(generics.GenericAPIView):
    serializer_class = SingleQuizSerializer
    queryset = Quiz
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data={"uuid": kwargs.get("uuid"), "questions": request.data.get("questions")},
            context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class GetScoreForUserAPI(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    serializer_class = TotalScoreSerializer
    queryset = QuizTaken
    permission_classes = [permissions.IsAuthenticated]
    lookup_fields = ["user__uuid", "quiz__uuid"]


class GetScoresForQuizAPI(MultipleFieldLookupMixin, generics.ListAPIView):
    serializer_class = TotalScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_fields = ["quiz__uuid"]

    def get_queryset(self):
        return QuizTaken.objects.filter(quiz__owner=self.request.user)