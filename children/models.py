from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid

YEAR_GROUP_BY_AGE = {
    5: {0, 1},
    6: {1, 2},
    7: {2, 3},
    8: {3, 4},
    9: {4, 5},
    10: {5, 6},
    11: {6},
}

class Child(models.Model):
    """
    Represents a child profile owned by a parent.
    Strictly scoped to MVP requirements: Age 5-11.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='children',
        help_text=_("The parent who owns this profile.")
    )
    first_name = models.CharField(max_length=100)
    age = models.IntegerField(
        validators=[
            MinValueValidator(5, message=_("Age must be at least 5.")),
            MaxValueValidator(11, message=_("Age must be 11 or under."))
        ],
        help_text=_("Child's age (5-11).")
    )
    school_name = models.CharField(max_length=255, blank=False, help_text=_("The name of the child's school."))
    year_group = models.IntegerField(
        validators=[
            MinValueValidator(0, message=_("Year group cannot be negative.")),
            MaxValueValidator(6, message=_("Year group cannot exceed 6 (e.g., UK Year 6)."))
        ],
        help_text=_("School Year Group (e.g., 0 for Reception, 1-6 for Primary Years).")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Children"

    def __str__(self):
        return f"{self.first_name} ({self.age})"

    def clean(self):
        super().clean()

        if not self.school_name:
            raise ValidationError({"school_name": _("School name cannot be empty.")})

        expected_groups = YEAR_GROUP_BY_AGE.get(self.age)
        if expected_groups and self.year_group not in expected_groups:
            raise ValidationError({
                "year_group": _(
                    "Year group must align with age. Expected one of %(groups)s for age %(age)s."
                ) % {"groups": sorted(expected_groups), "age": self.age}
            })
