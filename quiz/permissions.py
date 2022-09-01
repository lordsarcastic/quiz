from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsOwnerOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.public:
            return True
        
        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsOwnerOfQuestion(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        # Instance must have an attribute named `owner`.
        return obj.question.quiz.owner == request.user

class IsOwnerOfQuiz(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        # Instance must have an attribute named `owner`.
        return obj.quiz.owner == request.user


class IsOwnerOfQuizFromQuestionOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.quiz.public:
            return True
        
        # Instance must have an attribute named `owner`.
        return obj.quiz.owner == request.user