from django.urls import path, include

from quiz import views



app_name = 'quiz'

urlpatterns = [
    path('', views.ListCreateQuizAPI.as_view(), name='list-create-quiz'),
    path('<slug:uuid>/', views.RetrieveUpdateDestroyQuizAPI.as_view(), name='retrieve-update-destroy-quiz')
]