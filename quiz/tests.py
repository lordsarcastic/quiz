import json
import uuid
from typing import Any, Dict
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from quiz.models import Answer, Question, Quiz, UserAnswer, UserModel

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

    def test_question_can_be_created_with_answers(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        url = reverse('quiz:create-question', kwargs={"uuid": str(quiz.uuid)})
        response = self.client.post(
            url,
            data=json.dumps({
                "text": "What is the meaning of RPG?",
                "answers": [
                    {
                        "text": "Run Play Guard"
                    },
                    {
                        "text": "Run Play Guard",
                        "is_answer": True
                    },
                    {
                        "text": "Run Play Guard"
                    },
                    {
                        "text": "Run Play Guard"
                    }
                ]
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {"uuid", "answers", "created", "modified", "text"},
            response.json().keys()
        )
        self.assertTrue(Question.objects.get(uuid=uuid.UUID(response.json()["uuid"])))

    def test_question_cannot_have_more_than_5_answers(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        url = reverse('quiz:create-question', kwargs={"uuid": str(quiz.uuid)})
        response = self.client.post(
            url,
            json.dumps({
                "text": "What is the meaning of RPG?",
                "answers": [
                    {
                        "text": "Run Play Guard"
                    },
                    {
                        "text": "Run Play Guard",
                        "is_answer": True
                    },
                    {
                        "text": "Run Play Guard"
                    },
                    {
                        "text": "Run Play Guard"
                    },
                    {
                        "text": "Run Play Guard"
                    },
                    {
                        "text": "Run Play Guard"
                    }
                ]
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()[0], "Answers must not be more than 5")

    def test_question_can_be_updated(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        question = Question.objects.create(
            quiz=quiz,
            text="What is this?"
        )
        url = reverse("quiz:retrieve-update-destroy-question", kwargs={
            "quiz__uuid": str(quiz.uuid),
            "uuid": str(question.uuid)
        })
        response = self.client.patch(
            url,
            data={
                "text": "Why this?"
            }
        )

        self.assertEqual(response.json()['text'], "Why this?")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['uuid'], str(question.uuid))

    def test_question_can_be_deleted(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        question = Question.objects.create(
            quiz=quiz,
            text="What is this?"
        )
        question_uuid = question.uuid
        url = reverse("quiz:retrieve-update-destroy-question", kwargs={
            "quiz__uuid": str(quiz.uuid),
            "uuid": str(question.uuid)
        })
        response = self.client.delete(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Question.objects.filter(uuid=question_uuid).exists()
        )

    def test_answer_can_be_created(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        question = Question.objects.create(
            quiz=quiz,
            text="What is this?"
        )
        url = reverse("quiz:create-answer", kwargs={
            "question__quiz__uuid": str(quiz.uuid),
            "question__uuid": str(question.uuid)
        })
        data = {
            "text": "Answer 1"
        }
        response = self.client.post(
            url,
            data=data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {"uuid", "is_answer", "created", "modified", "text", "question"},
            response.json().keys()
        )
        self.assertEqual(response.json()["question"], str(question.uuid))

    def test_answer_can_be_updated(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        question = Question.objects.create(
            quiz=quiz,
            text="What is this?"
        )
        answer = Answer.objects.create(
            question=question,
            text="Answer 1"
        )
        url = reverse("quiz:retrieve-update-destroy-answer", kwargs={
            "question__quiz__uuid": str(quiz.uuid),
            "question__uuid": str(question.uuid),
            "pk": str(answer.uuid)
        })
        
        response = self.client.patch(
            url,
            data={
                "text": "Why this?"
            }
        )

        self.assertEqual(response.json()['text'], "Why this?")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['uuid'], str(answer.uuid))

    def test_answer_can_be_deleted(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        question = Question.objects.create(
            quiz=quiz,
            text="What is this?"
        )
        answer = Answer.objects.create(
            question=question,
            text="Answer 1"
        )
        url = reverse("quiz:retrieve-update-destroy-answer", kwargs={
            "question__quiz__uuid": str(quiz.uuid),
            "question__uuid": str(question.uuid),
            "pk": str(answer.uuid)
        })

        response = self.client.delete(
            url
        )


        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Answer.objects.filter(uuid=answer.uuid).exists()
        )

    def test_get_user_score_for_question_is_correct(self):
        quiz = Quiz.objects.filter(owner=self.user).first()
        question = Question.objects.create(quiz=quiz, text="Random")
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        answer_4 = Answer.objects.create(
            question=question,
            text="None"
        )
        answer_5 = Answer.objects.create(
            question=question,
            text="None",
            is_answer=True
        )

        user_answer = UserAnswer.objects.create(
            user=self.user,
            question=question,
        )
        for answer in (answer_4, answer_5):
            user_answer.answer.add(answer)
        user_answer.save()
        self.assertEqual(0.75, user_answer.get_score())

    def test_quiz_for_user_can_only_be_taken_once(self):
        user = UserModel.objects.get(email="main@email.com")
        quiz = Quiz.objects.create(
            owner=user,
            title="Indemnity Quiz",
            public=True
        )
        question = Question.objects.create(quiz=quiz, text="Random")
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        answer_4 = Answer.objects.create(
            question=question,
            text="None"
        )
        answer_5 = Answer.objects.create(
            question=question,
            text="None",
            is_answer=True
        )

        user_answer = UserAnswer.objects.create(
            user=self.user,
            question=question,
        )
        for answer in (answer_4, answer_5):
            user_answer.answer.add(answer)
        user_answer.save()

        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("quiz:take-quiz", kwargs={
            "uuid": str(quiz.uuid)
        })

        response = self.client.post(
            url,
            data=json.dumps({
                "questions": [
                    {
                        "uuid": str(question.uuid),
                        "answers": [
                            {"uuid": str(answer_5.uuid)}
                        ]
                    }
                ]
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            url,
            data=json.dumps({
                "questions": [
                    {
                        "uuid": str(question.uuid),
                        "answers": [
                            {"uuid": str(answer_5.uuid)}
                        ]
                    }
                ]
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_view_scores_after_taking_test(self):
        user = UserModel.objects.get(email="main@email.com")
        quiz = Quiz.objects.create(
            owner=user,
            title="Indemnity Quiz",
            public=True
        )
        question = Question.objects.create(quiz=quiz, text="Random")
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        answer_4 = Answer.objects.create(
            question=question,
            text="None"
        )
        answer_5 = Answer.objects.create(
            question=question,
            text="None",
            is_answer=True
        )

        user_answer = UserAnswer.objects.create(
            user=self.user,
            question=question,
        )
        for answer in (answer_4, answer_5):
            user_answer.answer.add(answer)
        user_answer.save()

        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("quiz:take-quiz", kwargs={
            "uuid": str(quiz.uuid)
        })

        response = self.client.post(
            url,
            data=json.dumps({
                "questions": [
                    {
                        "uuid": str(question.uuid),
                        "answers": [
                            {"uuid": str(answer_5.uuid)}
                        ]
                    }
                ]
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse("quiz:get-score-for-user", kwargs={
            "quiz__uuid": str(quiz.uuid),
            "user__uuid": str(user.uuid)
        })

        response = self.client.get(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {"quiz", "user", "score", "question"}
        )

    def test_user_cannot_view_scores_before_taking_test(self):
        user = UserModel.objects.get(email="main@email.com")
        quiz = Quiz.objects.create(
            owner=user,
            title="Indemnity Quiz",
            public=True
        )
        question = Question.objects.create(quiz=quiz, text="Random")
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        answer_4 = Answer.objects.create(
            question=question,
            text="None"
        )
        answer_5 = Answer.objects.create(
            question=question,
            text="None",
            is_answer=True
        )

        user_answer = UserAnswer.objects.create(
            user=self.user,
            question=question,
        )
        for answer in (answer_4, answer_5):
            user_answer.answer.add(answer)
        user_answer.save()

        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("quiz:get-score-for-user", kwargs={
            "quiz__uuid": str(quiz.uuid),
            "user__uuid": str(user.uuid)
        })

        response = self.client.get(
            url
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_of_quiz_can_view_test_results_for_other_users(self):
        user = UserModel.objects.get(email="main@email.com")
        user_owner = UserModel.objects.get(email="adeoti.15.jude@gmail.com")
        quiz = Quiz.objects.create(
            owner=user_owner,
            title="Indemnity Quiz",
            public=True
        )
        question = Question.objects.create(quiz=quiz, text="Random")
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        answer_4 = Answer.objects.create(
            question=question,
            text="None"
        )
        answer_5 = Answer.objects.create(
            question=question,
            text="None",
            is_answer=True
        )

        user_answer = UserAnswer.objects.create(
            user=self.user,
            question=question,
        )
        for answer in (answer_4, answer_5):
            user_answer.answer.add(answer)
        user_answer.save()

        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("quiz:take-quiz", kwargs={
            "uuid": str(quiz.uuid)
        })

        response = self.client.post(
            url,
            data=json.dumps({
                "questions": [
                    {
                        "uuid": str(question.uuid),
                        "answers": [
                            {"uuid": str(answer_5.uuid)}
                        ]
                    }
                ]
            }),
            content_type='application/json'
        )

        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user_owner.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("quiz:get-score-for-quiz", kwargs={
            "quiz__uuid": str(quiz.uuid)
        })

        response = self.client.get(
            url
        )
        self.assertEqual(
            set(response.json().keys()),
            {"count", "next", "previous", "results"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.json()["results"]),
            1
        )
        self.assertEqual(
            set(response.json()["results"][0].keys()),
            {"quiz", "user", "score", "question"}
        )

    def test_marked_as_published_cannot_be_edited(self): ...

    def test_other_user_cannot_view_test_results_for_other_users(self):
        user = UserModel.objects.get(email="main@email.com")
        quiz = Quiz.objects.create(
            owner=user,
            title="Indemnity Quiz",
            public=True
        )
        question = Question.objects.create(quiz=quiz, text="Random")
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        Answer.objects.create(
            question=question,
            text="None"
        )
        answer_4 = Answer.objects.create(
            question=question,
            text="None"
        )
        answer_5 = Answer.objects.create(
            question=question,
            text="None",
            is_answer=True
        )

        user_answer = UserAnswer.objects.create(
            user=self.user,
            question=question,
        )
        for answer in (answer_4, answer_5):
            user_answer.answer.add(answer)
        user_answer.save()

        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("quiz:take-quiz", kwargs={
            "uuid": str(quiz.uuid)
        })

        response = self.client.post(
            url,
            data=json.dumps({
                "questions": [
                    {
                        "uuid": str(question.uuid),
                        "answers": [
                            {"uuid": str(answer_5.uuid)}
                        ]
                    }
                ]
            }),
            content_type='application/json'
        )
        url = reverse("quiz:get-score-for-quiz", kwargs={
            "quiz__uuid": str(quiz.uuid)
        })

        user_owner = UserModel.objects.get(email="adeoti.15.jude@gmail.com")
        access_token = self.client.post(
            reverse("authentify:login"),
            {"email": user_owner.email, "password": "11111111"},
        ).json()["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(
            url
        )

        self.assertFalse(response.json()['count'])