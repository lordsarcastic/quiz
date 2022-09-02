from django.urls import path, include

from quiz import views


app_name = "quiz"

urlpatterns = [
    path("", views.ListCreateQuizAPI.as_view(), name="list-create-quiz"),
    path(
        "public/",
        include(
            [
                path(
                    "<uuid:uuid>/",
                    views.PublicRetrieveQuizAPI.as_view(),
                    name="public-retrieve-quiz",
                ),
                path(
                    "<uuid:quiz__uuid>/questions/<uuid:uuid>/",
                    views.PublicRetrieveQuestionAPI.as_view(),
                    name="public-retrieve-question",
                ),
            ]
        ),
    ),
    path(
        "<uuid:uuid>/",
        views.RetrieveUpdateDestroyQuizAPI.as_view(),
        name="retrieve-update-destroy-quiz",
    ),
    path(
        "<uuid:uuid>/questions/",
        views.CreateQuestionAPI.as_view(),
        name="create-question",
    ),
    path(
        "<uuid:quiz__uuid>/questions/<uuid:uuid>/",
        views.RetrieveUpdateDestroyQuestionAPI.as_view(),
        name="retrieve-update-destroy-question",
    ),
    path(
        "<uuid:quiz__uuid>/questions/<uuid:question_uuid>/answers",
        views.CreateAnswerAPI.as_view(),
        name="add-answer",
    ),
    path(
        "<uuid:quiz__uuid>/questions/<uuid:question_uuid>/answers/<uuid:pk>",
        views.RetrieveUpdateDestroyAnswerAPI.as_view(),
        name="retrieve-update-destroy-answer",
    ),
]
