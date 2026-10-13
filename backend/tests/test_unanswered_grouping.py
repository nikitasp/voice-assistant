"""Unit checks for unanswered paraphrase guards (no database)."""

from uuid import uuid4

from app.services.unanswered import is_near_paraphrase


def test_paraphrase_guard_requires_shared_identifiers():
    shared = "abcdef12"
    assert is_near_paraphrase(
        f"Can I bring my dog to the hotel during stay {shared}?",
        f"Is it allowed to bring a dog when staying at the hotel {shared}?",
    )
    assert not is_near_paraphrase(
        f"Is there a laundry service on floor {uuid4().hex[:8]}?",
        f"Is there a laundry service on floor {uuid4().hex[:8]}?",
    )
    assert not is_near_paraphrase(
        f"Is laundry available on property {shared}?",
        f"Does the resort have a helipad {shared}?",
    )
