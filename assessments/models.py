import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from children.models import Child
from .events import diagnostic_test_completed


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
        Child,
        on_delete=models.CASCADE,
        related_name="diagnostic_tests",
    )
    subject = models.CharField(max_length=20, choices=Subject.choices)
    total_questions = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="At least one question is required.")]
    )
    correct_answers = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="Correct answers cannot be negative.")],
    )
    score_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        editable=False,
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    rank = models.CharField(
        max_length=10,
        choices=Rank.choices,
        null=True,
        blank=True,
        help_text="Assigned once upon completion",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                check=Q(correct_answers__lte=F("total_questions")),
                name="diagnostic_test_correct_lte_total",
            ),
            models.CheckConstraint(
                check=Q(
                    Q(is_completed=False, completed_at__isnull=True)
                    | Q(is_completed=True, completed_at__isnull=False)
                ),
                name="diagnostic_test_completion_consistency",
            ),
        ]

    def __str__(self):
        return f"{self.child.first_name} - {self.get_subject_display()} test"

    def save(self, *args, **kwargs):
        self.score_percentage = self.calculate_score_percentage()
        super().save(*args, **kwargs)

    def calculate_score_percentage(self) -> Decimal:
        if not self.total_questions:
            return Decimal("0.00")

        raw = (Decimal(self.correct_answers) / Decimal(self.total_questions)) * Decimal(
            "100"
        )
        return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def complete(self, completed_at=None) -> bool:
        """
        Marks the test as completed. Returns True if the completion event
        occurred, False if it was already complete (idempotent behavior).
        """
        if self.is_completed:
            return False

        self.is_completed = True
        self.completed_at = completed_at or timezone.now()
        self.save(update_fields=["is_completed", "completed_at"])

        diagnostic_test_completed.send(
            sender=self.__class__,
            diagnostic_test=self,
        )
        return True


class DiagnosticQuestion(models.Model):
    class Option(models.TextChoices):
        A = "A", "Option A"
        B = "B", "Option B"
        C = "C", "Option C"
        D = "D", "Option D"

    test = models.ForeignKey(
        DiagnosticTest,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    prompt_version = models.CharField(max_length=50)
    seed = models.CharField(max_length=64)
    order = models.PositiveIntegerField()
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=1, choices=Option.choices)
    difficulty = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=("test", "order"), name="diagnostic_question_unique_order"
            )
        ]

    def __str__(self):
        return f"{self.test_id} - Q{self.order}"


class AIRequestLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"

    test = models.ForeignKey(
        DiagnosticTest,
        on_delete=models.CASCADE,
        related_name="ai_request_logs",
        null=True,
        blank=True,
    )
    prompt_version = models.CharField(max_length=50)
    seed = models.CharField(max_length=64)
    provider = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices)
    error_message = models.TextField(blank=True)
    prompt_excerpt = models.TextField()
    response_excerpt = models.TextField(blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.prompt_version} ({self.status})"
