from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from children.models import Child
from rewards.models import TreasureChest

from .models import DiagnosticTest


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

    def test_create_endpoint_requires_parent_ownership(self):
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
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DiagnosticTest.objects.count(), 1)

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
