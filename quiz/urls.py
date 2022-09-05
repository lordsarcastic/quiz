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
        "<uuid:uuid>/take",
        views.TakeQuizAPI.as_view(),
        name="take-quiz",
    ),
    path(
        "<uuid:uuid>/questions/",
        views.CreateQuestionAPI.as_view(),
        name="create-question",
    ),
    path(
        "<uuid:quiz__uuid>/results/",
        views.GetScoresForQuizAPI.as_view(),
        name="get-score-for-quiz"
    ),
    path(
        "<uuid:quiz__uuid>/results/<uuid:user__uuid>/",
        views.GetScoreForUserAPI.as_view(),
        name="get-score-for-user"
    ),
    path(
        "<uuid:quiz__uuid>/questions/<uuid:uuid>/",
        views.RetrieveUpdateDestroyQuestionAPI.as_view(),
        name="retrieve-update-destroy-question",
    ),
    path(
        "<uuid:question__quiz__uuid>/questions/<uuid:question__uuid>/answers",
        views.CreateAnswerAPI.as_view(),
        name="create-answer",
    ),
    path(
        "<uuid:question__quiz__uuid>/questions/<uuid:question__uuid>/answers/<uuid:pk>",
        views.RetrieveUpdateDestroyAnswerAPI.as_view(),
        name="retrieve-update-destroy-answer",
    ),
]
