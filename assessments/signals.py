from django.dispatch import receiver
from django.utils import timezone

from rewards.models import TreasureChest

from .events import diagnostic_test_completed
from .ranking import assign_rank_for_test


@receiver(diagnostic_test_completed)
def unlock_treasure_chest_on_completion(sender, diagnostic_test, **kwargs):
    try:
        chest = TreasureChest.objects.get(child=diagnostic_test.child)
    except TreasureChest.DoesNotExist:
        return

    if not chest.is_locked:
        return  # Already unlocked elsewhere.

    chest.is_locked = False
    chest.unlocked_at = timezone.now()
    chest.save(update_fields=["is_locked", "unlocked_at"])


@receiver(diagnostic_test_completed)
def assign_rank_on_completion(sender, diagnostic_test, **kwargs):
    assign_rank_for_test(diagnostic_test)
