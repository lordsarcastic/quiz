from rest_framework import generics, permissions
from quiz.models import Quiz

from . import exceptions
from quiz.serializers import QuizSerializer
from .permissions import (
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
        
        return instance.delete()
    
    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)
