from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Child",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                (
                    "age",
                    models.IntegerField(
                        help_text="Child's age (5-11).",
                        validators=[
                            MinValueValidator(5, message="Age must be at least 5."),
                            MaxValueValidator(11, message="Age must be 11 or under."),
                        ],
                    ),
                ),
                (
                    "school_name",
                    models.CharField(
                        help_text="The name of the child's school.", max_length=255
                    ),
                ),
                (
                    "year_group",
                    models.IntegerField(
                        help_text="School Year Group (e.g., 0 for Reception, 1-6 for Primary Years).",
                        validators=[
                            MinValueValidator(0, message="Year group cannot be negative."),
                            MaxValueValidator(
                                6, message="Year group cannot exceed 6 (e.g., UK Year 6)."
                            ),
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        help_text="The parent who owns this profile.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name_plural": "Children"},
        ),
    ]
