from decimal import Decimal
from typing import Optional

from .models import DiagnosticTest


BRONZE_MIN = Decimal("40.00")
BRONZE_MAX = Decimal("50.00")
SILVER_MIN = Decimal("51.00")
SILVER_MAX = Decimal("70.00")
GOLD_MIN = Decimal("71.00")


def determine_rank(score: Optional[Decimal]) -> Optional[str]:
    if score is None:
        return None

    if BRONZE_MIN <= score <= BRONZE_MAX:
        return DiagnosticTest.Rank.BRONZE
    if SILVER_MIN <= score <= SILVER_MAX:
        return DiagnosticTest.Rank.SILVER
    if GOLD_MIN <= score <= Decimal("100.00"):
        return DiagnosticTest.Rank.GOLD
    return None


def assign_rank_for_test(test: DiagnosticTest) -> Optional[str]:
    """
    Idempotently assign a rank for the provided completed diagnostic test.
    """
    if test.rank:
        return test.rank

    rank = determine_rank(test.score_percentage)
    if not rank:
        return None

    updated = DiagnosticTest.objects.filter(pk=test.pk, rank__isnull=True).update(
        rank=rank
    )
    if updated:
        test.rank = rank
    return rank
