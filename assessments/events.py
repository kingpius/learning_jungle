from django.dispatch import Signal

# Fired exactly once when a diagnostic test transitions into a completed state.
diagnostic_test_completed = Signal()
