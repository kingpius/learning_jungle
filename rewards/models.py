from django.db import models
from django.conf import settings
from children.models import Child
from django.core.validators import MaxValueValidator

class TreasureChest(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="treasure_chests"
    )
    child = models.OneToOneField(
        Child,
        on_delete=models.CASCADE,
        related_name="treasure_chest"
    )

    reward_description = models.CharField(max_length=255)
    reward_value = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MaxValueValidator(5.00)]
    )

    is_locked = models.BooleanField(default=True)
    unlocked_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Treasure Chest for {self.child.first_name}"
