from typing import Any, Dict
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from quiz.models import UserModel

# Create your tests here.


class TestQuizViews(APITestCase):
    fixtures = ['quiz/tests/fixtures/auth.json']
    def setUp(self) -> None:
        self.user = UserModel.objects.get(email="adeoti.15.jude@gmail.com")
        self.access_token = self.client.post(
            reverse("authentify:login"),
            {"email": self.user.email, "password": "11111111"}
        ).json()["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_single_quiz_can_be_created(self):
        url = reverse("quiz:list-create-quiz")

        response = self.client.post(
            url,
            data={"title": "Geography", "public": True}
        )
        self.assertEqual(response.json()['owner'], str(self.user.uuid))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_created_quiz_will_show_up_in_list(self):
        url = reverse("quiz:list-create-quiz")

        self.client.post(
            url,
            data={"title": "Geography", "public": True}
        )

        response = self.client.get(url)
        self.assertGreater(response.json()['count'], 0)
        single_quiz: Dict[str, Any] = response.json()['results'][0]
        self.assertEqual(
            {'owner', 'username', 'uuid', 'title', 'public', 'created', 'modified'},
            set(single_quiz.keys())
        )
        self.assertEqual(
            {'username', 'uuid'},
            set(single_quiz['owner'].keys())
        )
    
    def test_single_quiz_can_be_retrieved(self):
        url = reverse("quiz:list-create-quiz")

        self.client.post(
            url,
            data={"title": "Geography", "public": True}
        )
    
    
    
