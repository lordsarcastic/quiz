from typing import Any, Dict
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from quiz.models import Quiz, UserModel

# Create your tests here.


class TestQuizViews(APITestCase):
    fixtures = ["quiz/tests/fixtures/fixture.json"]

    def setUp(self) -> None:
        self.user = UserModel.objects.get(email="adeoti.15.jude@gmail.com")
        self.access_token = self.client.post(
            reverse("authentify:login"),
            {"email": self.user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_single_quiz_can_be_created(self):
        url = reverse("quiz:list-create-quiz")

        response = self.client.post(url, data={"title": "Geography", "public": True})
        self.assertEqual(response.json()["owner"], str(self.user.uuid))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_created_quiz_will_show_up_in_list(self):
        url = reverse("quiz:list-create-quiz")

        self.client.post(url, data={"title": "Geography", "public": True})

        response = self.client.get(url)
        self.assertGreater(response.json()["count"], 0)
        single_quiz: Dict[str, Any] = response.json()["results"][0]
        self.assertEqual(
            {"owner", "uuid", "title", "public", "created", "modified"},
            set(single_quiz.keys()),
        )

    def test_single_quiz_can_be_retrieved(self):
        quiz = Quiz.objects.all().first()
        url = reverse("quiz:retrieve-update-destroy-quiz", kwargs={"uuid": quiz.uuid})
        response = self.client.get(url)
        self.assertEqual(
            {"uuid", "questions", "created", "modified", "title", "public", "owner"},
            set(response.json().keys()),
        )
        self.assertEqual(response.json()["uuid"], str(quiz.pk))

    def test_non_owner_cannot_access_sensitive_question_details_in_quiz(self):
        user = UserModel.objects.get(email="main@email.com")
        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        quiz = Quiz.objects.filter(
            owner__email="adeoti.15.jude@gmail.com", question__gte=1
        ).first()
        url = reverse("quiz:public-retrieve-quiz", kwargs={"uuid": quiz.uuid})
        response = self.client.get(url)
        self.assertEqual(
            {"uuid", "questions", "created", "modified", "title", "public", "owner"},
            set(response.json().keys()),
        )
        self.assertEqual(response.json()["uuid"], str(quiz.pk))
        self.assertNotIn("is_answer", response.json()["questions"][0]["answers"][0])

    def test_non_owner_cannot_access_sensitive_question_details(self):
        user = UserModel.objects.get(email="main@email.com")
        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        quiz = Quiz.objects.filter(
            owner__email="adeoti.15.jude@gmail.com", question__gte=1
        ).first()
        question = quiz.question_set.all().first()
        url = reverse(
            "quiz:public-retrieve-question",
            kwargs={"quiz__uuid": quiz.uuid, "uuid": question.uuid},
        )
        response = self.client.get(url)
        self.assertEqual(
            {"uuid", "answers", "created", "modified", "text", "quiz"},
            set(response.json().keys()),
        )
        self.assertEqual(response.json()["uuid"], str(question.pk))
        self.assertNotIn("is_answer", response.json()["answers"][0])
