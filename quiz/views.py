from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from quiz.mixins import MultipleFieldLookupMixin
from quiz.models import Answer, Question, Quiz

from . import exceptions
from quiz.serializers import AnswerSerializer, AnswerWithSecretSerializer, QuestionOnlySerializer, QuestionSerializer, QuizSerializer
from .permissions import (
    IsOwnerOfQuestion,
    IsOwnerOfQuiz,
    IsOwnerOfQuizFromQuestionOrPublic,
    IsOwnerOrReadOnly,
    IsOwnerOrPublic
)


class ListCreateQuizAPI(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.filter(public=True)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RetrieveUpdateDestroyQuizAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrPublic
    ]
    lookup_field = 'uuid'

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise exceptions.NOT_OWNER_OF_RESOURCE

        instance.delete()

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


class CreateQuestionAPI(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    queryset = Question
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfQuiz]

    def post(self, request: Request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs.get('uuid'))
        serializer = self.serializer_class(data=request.data, context={"quiz": quiz})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

class RetrieveQuestionAPI(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    serializer_class = QuestionSerializer
    queryset = Question
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOfQuizFromQuestionOrPublic
    ]
    lookup_fields = ['quiz__uuid', 'uuid']
# class UpdateDestroyQuestionAPI(generics.U):
#     serializer_class = QuestionOnlySerializer
#     queryset = Question
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOfQuestion]


class CreateAnswerAPI(MultipleFieldLookupMixin, generics.CreateAPIView):
    serializer_class = AnswerSerializer
    queryset = Answer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfQuestion]
    lookup_fields = ['question__quiz__uuid', 'question__uuid']

    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs.get('quiz_uuid'))
        question = get_object_or_404(Question, pk=kwargs.get("question_uuid"))
        serializer = self.serializer_class(data=request.data, context={"question": question})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    # def perform_create(self, serializer):
    #     serializer.save(question=self.request.user)
# class RetrieveUpdateDestroyAnswerAPI(generics.RetrieveUpdateDestroyAPIView):
