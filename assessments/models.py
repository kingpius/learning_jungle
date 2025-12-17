import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from children.models import Child

from . import events


class DiagnosticTest(models.Model):
    class Subject(models.TextChoices):
        MATHS = "maths", "Maths"
        ENGLISH = "english", "English"
        SCIENCE = "science", "Science"

    class Rank(models.TextChoices):
        BRONZE = "bronze", "Bronze"
        SILVER = "silver", "Silver"
        GOLD = "gold", "Gold"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="diagnostic_tests"
    )
    subject = models.CharField(max_length=10, choices=Subject.choices)
    total_questions = models.PositiveIntegerField(default=10)
    correct_answers = models.PositiveIntegerField(default=0)
    score_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    rank = models.CharField(
        max_length=10, choices=Rank.choices, null=True, blank=True
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Diagnostic for {self.child} - {self.get_subject_display()}"

    def save(self, *args, **kwargs):
        if self.total_questions > 0:
            score = (
                Decimal(self.correct_answers) / Decimal(self.total_questions)
            ) * 100
            self.score_percentage = score.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            self.score_percentage = Decimal("0.00")
        super().save(*args, **kwargs)

    def complete(self):
        if self.is_completed:
            return False

        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

        events.diagnostic_test_completed.send(
            sender=self.__class__, diagnostic_test=self
        )
        return True


class DiagnosticQuestion(models.Model):
    class CorrectOption(models.TextChoices):
        A = "A"
        B = "B"
        C = "C"
        D = "D"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(
        DiagnosticTest, on_delete=models.CASCADE, related_name="questions"
    )
    prompt_version = models.CharField(max_length=50)
    seed = models.CharField(max_length=255)
    order = models.PositiveIntegerField()
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=CorrectOption.choices)
    difficulty = models.CharField(max_length=20)

    class Meta:
        ordering = ["order"]
        unique_together = ("test", "order")


class DiagnosticResponse(models.Model):
    class SelectedOption(models.TextChoices):
        A = "A"
        B = "B"
        C = "C"
        D = "D"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(
        DiagnosticTest, on_delete=models.CASCADE, related_name="responses"
    )
    question = models.ForeignKey(
        DiagnosticQuestion, on_delete=models.CASCADE, related_name="responses"
    )
    selected_option = models.CharField(max_length=1, choices=SelectedOption.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("test", "question")


class AIRequestLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(
        DiagnosticTest, on_delete=models.SET_NULL, null=True, blank=True
    )
    prompt_version = models.CharField(max_length=50)
    seed = models.CharField(max_length=255)
    provider = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=Status.choices)
    error_message = models.TextField(blank=True)
    prompt_excerpt = models.TextField()
    response_excerpt = models.TextField(blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
