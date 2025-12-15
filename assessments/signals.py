from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import TestAttempt
from rewards.models import TreasureChest
from django.utils import timezone

@receiver(post_save, sender=TestAttempt)
def unlock_treasure_chest_on_first_test(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.completed:
        return

    try:
        chest = TreasureChest.objects.get(child=instance.child)
    except TreasureChest.DoesNotExist:
        return

    if not chest.is_locked:
        return  # idempotency

    chest.is_locked = False
    chest.unlocked_at = timezone.now()
    chest.save()
