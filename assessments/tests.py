import json
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ai.exceptions import AIProviderError
from children.models import Child
from rewards.models import TreasureChest

from .diagnostics.services import DiagnosticGenerationError, ensure_maths_questions_for_test
from .models import (
    AIRequestLog,
    DiagnosticQuestion,
    DiagnosticTest,
    DiagnosticResponse,
)


class DiagnosticTestDomainTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.parent = User.objects.create_user(
            username="parent",
            email="parent@example.com",
            password="pass1234",
        )
        self.other_parent = User.objects.create_user(
            username="intruder",
            email="intruder@example.com",
            password="pass1234",
        )
        self.child = Child.objects.create(
            parent=self.parent,
            first_name="Ava",
            age=6,
            school_name="MVP Primary",
            year_group=1,
        )

    def _create_test_with_score(self, correct_answers):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=100,
            correct_answers=correct_answers,
        )
        return test

    def test_diagnostic_test_persists_and_links_to_child(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=10,
            correct_answers=7,
        )
        self.assertEqual(test.child, self.child)
        self.assertEqual(str(test.score_percentage), "70.00")

    def test_complete_sets_timestamp_and_is_idempotent(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.ENGLISH,
            total_questions=5,
            correct_answers=5,
        )
        first_call = test.complete()
        test.refresh_from_db()

        self.assertTrue(first_call)
        self.assertTrue(test.is_completed)
        self.assertIsNotNone(test.completed_at)

        second_call = test.complete()
        test.refresh_from_db()

        self.assertFalse(second_call)
        self.assertTrue(test.is_completed)

    def test_rank_threshold_boundaries(self):
        cases = [
            (40, DiagnosticTest.Rank.BRONZE),
            (50, DiagnosticTest.Rank.BRONZE),
            (51, DiagnosticTest.Rank.SILVER),
            (70, DiagnosticTest.Rank.SILVER),
            (71, DiagnosticTest.Rank.GOLD),
            (100, DiagnosticTest.Rank.GOLD),
        ]
        for correct, expected_rank in cases:
            with self.subTest(correct=correct):
                test = self._create_test_with_score(correct)
                test.complete()
                test.refresh_from_db()
                self.assertEqual(test.rank, expected_rank)

    def test_rank_not_assigned_below_threshold(self):
        test = self._create_test_with_score(30)
        test.complete()
        test.refresh_from_db()
        self.assertIsNone(test.rank)

    def test_rank_does_not_change_after_completion(self):
        test = self._create_test_with_score(40)
        test.complete()
        test.refresh_from_db()
        original_rank = test.rank

        test.correct_answers = 90
        test.save()
        test.refresh_from_db()
        self.assertEqual(test.rank, original_rank)

    def test_completion_signal_unlocks_treasure_chest_once(self):
        chest = TreasureChest.objects.create(
            parent=self.parent,
            child=self.child,
            reward_description="Sticker pack",
            reward_value=Decimal("1.00"),
        )
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.SCIENCE,
            total_questions=4,
            correct_answers=4,
        )

        test.complete()
        chest.refresh_from_db()
        self.assertFalse(chest.is_locked)
        first_unlocked_at = chest.unlocked_at

        test.complete()
        chest.refresh_from_db()
        self.assertEqual(first_unlocked_at, chest.unlocked_at)

    @mock.patch("ai.maths_diagnostic.call_llm")
    def test_create_endpoint_requires_parent_ownership(self, mock_call_llm):
        mock_call_llm.return_value = json.dumps(
            {
                "questions": [
                    {
                        "question_text": "2 + 3 = ?",
                        "options": ["4", "5", "6", "7"],
                        "correct_answer_index": 1,
                        "difficulty": "easy",
                    }
                ]
            }
        )
        self.client.login(username="parent", password="pass1234")
        url = reverse(
            "assessments:create_diagnostic_test",
            kwargs={"child_id": self.child.id},
        )
        response = self.client.post(
            url,
            {
                "subject": DiagnosticTest.Subject.MATHS,
                "total_questions": 8,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DiagnosticTest.objects.count(), 1)
        self.assertEqual(DiagnosticQuestion.objects.count(), 1)
        test = DiagnosticTest.objects.first()
        self.assertEqual(test.correct_answers, 0)
        self.assertIsNone(response.json().get("rank"))

    def test_cross_parent_access_to_completion_is_denied(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=3,
            correct_answers=2,
        )
        self.client.login(username="intruder", password="pass1234")
        url = reverse(
            "assessments:complete_diagnostic_test",
            kwargs={"test_id": test.id},
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        test.refresh_from_db()
        self.assertFalse(test.is_completed)

    @mock.patch("ai.maths_diagnostic.call_llm")
    def test_service_generates_and_persists_questions(self, mock_call_llm):
        payload = {
            "questions": [
                {
                    "question_text": "5 + 3 = ?",
                    "options": ["6", "7", "8", "9"],
                    "correct_answer_index": 2,
                    "difficulty": "easy",
                },
                {
                    "question_text": "10 - 4 = ?",
                    "options": ["5", "6", "7", "8"],
                    "correct_answer_index": 1,
                    "difficulty": "medium",
                },
            ]
        }
        mock_call_llm.return_value = json.dumps(payload)

        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=10,
            correct_answers=0,
        )
        ensure_maths_questions_for_test(test, n_questions=2)

        questions = DiagnosticQuestion.objects.filter(test=test).order_by("order")
        self.assertEqual(questions.count(), 2)
        self.assertEqual(questions.first().correct_option, "C")
        self.assertEqual(
            AIRequestLog.objects.filter(test=test, status=AIRequestLog.Status.SUCCESS).count(),
            1,
        )

    @mock.patch("ai.maths_diagnostic.call_llm")
    def test_service_is_idempotent_per_test(self, mock_call_llm):
        payload = {
            "questions": [
                {
                    "question_text": "1 + 1 = ?",
                    "options": ["0", "1", "2", "3"],
                    "correct_answer_index": 2,
                    "difficulty": "easy",
                }
            ]
        }
        mock_call_llm.return_value = json.dumps(payload)
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=10,
            correct_answers=0,
        )
        ensure_maths_questions_for_test(test, n_questions=1)
        ensure_maths_questions_for_test(test, n_questions=1)
        self.assertEqual(DiagnosticQuestion.objects.filter(test=test).count(), 1)
        self.assertEqual(AIRequestLog.objects.filter(test=test).count(), 1)

    @mock.patch("ai.maths_diagnostic.call_llm")
    def test_completed_test_cannot_generate(self, mock_call_llm):
        mock_call_llm.return_value = json.dumps(
            {
                "questions": [
                    {
                        "question_text": "2 x 2 = ?",
                        "options": ["2", "3", "4", "5"],
                        "correct_answer_index": 2,
                        "difficulty": "easy",
                    }
                ]
            }
        )
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=10,
            correct_answers=10,
            is_completed=True,
            completed_at=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            ensure_maths_questions_for_test(test)

    @mock.patch("ai.maths_diagnostic.call_llm")
    def test_generation_failure_does_not_persist_questions(self, mock_call_llm):
        mock_call_llm.side_effect = AIProviderError("provider down")
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=10,
            correct_answers=0,
        )

        with self.assertRaises(DiagnosticGenerationError):
            ensure_maths_questions_for_test(test)

        self.assertEqual(DiagnosticQuestion.objects.filter(test=test).count(), 0)
        self.assertEqual(
            AIRequestLog.objects.filter(test=test, status=AIRequestLog.Status.FAILURE).count(),
            1,
        )

    @mock.patch("ai.maths_diagnostic.call_llm")
    def test_create_endpoint_bubbles_ai_failure(self, mock_call_llm):
        mock_call_llm.side_effect = AIProviderError("provider down")
        self.client.login(username="parent", password="pass1234")
        url = reverse(
            "assessments:create_diagnostic_test",
            kwargs={"child_id": self.child.id},
        )
        response = self.client.post(
            url,
            {
                "subject": DiagnosticTest.Subject.MATHS,
                "total_questions": 8,
                "correct_answers": 6,
            },
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(DiagnosticTest.objects.count(), 0)

    def test_complete_endpoint_returns_rank(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=1,
            correct_answers=0,
        )
        question = DiagnosticQuestion.objects.create(
            test=test,
            prompt_version="v1",
            seed="seed",
            order=1,
            question_text="1+1?",
            option_a="2",
            option_b="3",
            option_c="4",
            option_d="5",
            correct_option="A",
            difficulty="easy",
        )
        DiagnosticResponse.objects.create(
            test=test,
            question=question,
            selected_option="A",
        )
        self.client.login(username="parent", password="pass1234")
        url = reverse(
            "assessments:complete_diagnostic_test",
            kwargs={"test_id": test.id},
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("rank"), DiagnosticTest.Rank.GOLD)

    @mock.patch("ai.maths_diagnostic.call_llm")
    def test_create_endpoint_rejects_after_completion(self, mock_call_llm):
        mock_call_llm.return_value = json.dumps(
            {
                "questions": [
                    {
                        "question_text": "2 + 3 = ?",
                        "options": ["4", "5", "6", "7"],
                        "correct_answer_index": 1,
                        "difficulty": "easy",
                    }
                ]
            }
        )
        DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=10,
            correct_answers=10,
            is_completed=True,
            completed_at=timezone.now(),
        )
        self.client.login(username="parent", password="pass1234")
        url = reverse(
            "assessments:create_diagnostic_test",
            kwargs={"child_id": self.child.id},
        )
        response = self.client.post(
            url,
            {
                "subject": DiagnosticTest.Subject.MATHS,
                "total_questions": 8,
            },
        )
        self.assertEqual(response.status_code, 409)


class DiagnosticUIViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.parent = User.objects.create_user(
            username="parent-ui",
            email="parent-ui@example.com",
            password="pass1234",
        )
        self.child = Child.objects.create(
            parent=self.parent,
            first_name="Noah",
            age=7,
            school_name="UI Primary",
            year_group=2,
        )
        TreasureChest.objects.create(
            parent=self.parent,
            child=self.child,
            reward_description="Story time",
            reward_value=Decimal("2.00"),
        )

    def _seed_question(self, test, order=1, correct="A"):
        return DiagnosticQuestion.objects.create(
            test=test,
            prompt_version="test",
            seed="seed",
            order=order,
            question_text=f"{order} + {order}",
            option_a="2",
            option_b="3",
            option_c="4",
            option_d="5",
            correct_option=correct,
            difficulty="easy",
        )

    @mock.patch("assessments.diagnostics.services.ensure_maths_questions_for_test")
    def test_start_flow_creates_test_and_redirects(self, mock_generate):
        def fake_generate(test, n_questions=None):
            if not test.questions.exists():
                self._seed_question(test)
        mock_generate.side_effect = fake_generate

        self.client.login(username="parent-ui", password="pass1234")
        url = reverse("assessments:diagnostic_start", kwargs={"child_id": self.child.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        test = DiagnosticTest.objects.get(child=self.child)
        self.assertEqual(test.questions.count(), 1)

    def test_question_flow_saves_and_submits_answers(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=1,
            correct_answers=0,
        )
        question = self._seed_question(test, correct="C")
        self.client.login(username="parent-ui", password="pass1234")
        url = reverse("assessments:diagnostic_questions", kwargs={"test_id": test.id})
        save_response = self.client.post(
            url,
            {
                f"answer_{question.id}": "C",
                "action": "save",
            },
        )
        self.assertEqual(save_response.status_code, 200)
        self.assertTrue(
            DiagnosticResponse.objects.filter(test=test, question=question).exists()
        )

        submit_response = self.client.post(
            url,
            {
                f"answer_{question.id}": "C",
                "action": "submit",
            },
        )
        self.assertEqual(submit_response.status_code, 302)
        test.refresh_from_db()
        self.assertTrue(test.is_completed)
        self.assertEqual(test.correct_answers, 1)
        results = self.client.get(
            reverse("assessments:diagnostic_results", kwargs={"test_id": test.id})
        )
        self.assertContains(results, "You scored")
        self.assertContains(results, "Treasure")

    def test_submission_blocked_when_answers_missing(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=1,
            correct_answers=0,
        )
        question = self._seed_question(test)
        self.client.login(username="parent-ui", password="pass1234")
        url = reverse("assessments:diagnostic_questions", kwargs={"test_id": test.id})
        response = self.client.post(
            url,
            {
                f"answer_{question.id}": "",
                "action": "submit",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please answer all questions")

    def test_results_read_only_for_completed_tests(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=1,
            correct_answers=1,
            is_completed=True,
            completed_at=timezone.now(),
            rank=DiagnosticTest.Rank.GOLD,
        )
        question = self._seed_question(test, correct="A")
        DiagnosticResponse.objects.create(
            test=test,
            question=question,
            selected_option="A",
        )
        self.client.login(username="parent-ui", password="pass1234")
        url = reverse("assessments:diagnostic_questions", kwargs={"test_id": test.id})
        response = self.client.get(url)
        self.assertRedirects(
            response, reverse("assessments:diagnostic_results", kwargs={"test_id": test.id})
        )
        submit_response = self.client.post(
            url,
            {
                f"answer_{question.id}": "B",
                "action": "submit",
            },
        )
        self.assertRedirects(
            submit_response,
            reverse("assessments:diagnostic_results", kwargs={"test_id": test.id}),
        )

    def test_submit_uses_saved_responses_when_resuming(self):
        test = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=1,
            correct_answers=0,
        )
        question = self._seed_question(test, correct="D")
        DiagnosticResponse.objects.create(
            test=test,
            question=question,
            selected_option="D",
        )
        self.client.login(username="parent-ui", password="pass1234")
        url = reverse("assessments:diagnostic_questions", kwargs={"test_id": test.id})
        response = self.client.post(
            url,
            {
                "action": "submit",
            },
        )
        self.assertRedirects(
            response,
            reverse("assessments:diagnostic_results", kwargs={"test_id": test.id}),
        )
        test.refresh_from_db()
        self.assertTrue(test.is_completed)
        self.assertEqual(test.correct_answers, 1)

    def test_start_redirects_to_results_when_completed(self):
        completed = DiagnosticTest.objects.create(
            child=self.child,
            subject=DiagnosticTest.Subject.MATHS,
            total_questions=1,
            correct_answers=1,
            is_completed=True,
            completed_at=timezone.now(),
        )
        self._seed_question(completed)
        DiagnosticResponse.objects.create(
            test=completed,
            question=completed.questions.first(),
            selected_option="A",
        )
        self.client.login(username="parent-ui", password="pass1234")
        url = reverse("assessments:diagnostic_start", kwargs={"child_id": self.child.id})
        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("assessments:diagnostic_results", kwargs={"test_id": completed.id}),
        )
        self.assertEqual(DiagnosticTest.objects.filter(child=self.child).count(), 1)
