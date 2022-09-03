from django.contrib import admin

from quiz.models import Answer, Question, Quiz, QuizTaken, UserAnswer

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizTaken)
admin.site.register(UserAnswer)