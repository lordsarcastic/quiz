from django.core.exceptions import ValidationError

from rest_framework.exceptions import PermissionDenied


MAX_QUESTIONS_LIMIT_REACHED = ValidationError("Number of questions per quiz cannot be greater than 10")
NOT_OWNER_OF_RESOURCE = PermissionDenied("You are not the owner of this quiz")