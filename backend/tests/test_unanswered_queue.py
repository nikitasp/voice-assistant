"""AP-5–AP-8: unanswered queue list, convert to FAQ, dismiss."""

from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


async def _record(client, question: str) -> dict:
    response = await client.post("/api/unanswered", json={"question": question})
    assert response.status_code in (200, 201), response.text
    return response.json()


async def test_open_queue_sorted_by_frequency_then_recency(client):
    # Keep topics far apart so semantic grouping does not merge them.
    rare = f"What is the wifi password for conference room Zeta-{uuid4().hex[:8]}?"
    frequent = f"Can the spa schedule a hot-stone massage for guest {uuid4().hex[:8]}?"

    rare_row = await _record(client, rare)
    first = await _record(client, frequent)
    await _record(client, frequent)

    response = await client.get("/api/unanswered", params={"status": "open"})
    assert response.status_code == 200, response.text
    items = response.json()
    ids = [item["id"] for item in items]
    assert first["id"] in ids
    assert rare_row["id"] in ids
    assert ids.index(first["id"]) < ids.index(rare_row["id"])
    assert next(item for item in items if item["id"] == first["id"])["frequency"] == 2


async def test_convert_creates_searchable_faq_and_leaves_open_queue(client):
    marker = uuid4().hex[:8]
    question = f"Do you have origami lessons {marker}?"
    answer = f"Origami lessons {marker} are offered Saturdays at 2 PM in the craft studio."
    recorded = await _record(client, question)

    convert = await client.post(
        f"/api/unanswered/{recorded['id']}/convert",
        json={
            "category": "amenities",
            "question": question,
            "answer": answer,
            "slug": f"origami-{marker}",
        },
    )
    assert convert.status_code == 200, convert.text
    assert convert.json()["status"] == "converted"

    open_queue = await client.get("/api/unanswered", params={"status": "open"})
    assert all(item["id"] != recorded["id"] for item in open_queue.json())

    listed = await client.get("/api/faq", params={"q": marker})
    assert listed.status_code == 200, listed.text
    assert any(item["slug"] == f"origami-{marker}" and item["answer"] == answer for item in listed.json())

    search = await client.post(
        "/api/faq/search",
        json={"query": question},
    )
    assert search.status_code == 200, search.text
    body = search.json()
    assert body["found"] is True
    assert any(result["slug"] == f"origami-{marker}" for result in body["results"])


async def test_dismiss_removes_from_open_queue(client):
    question = f"Can I borrow a unicycle {uuid4().hex[:8]}?"
    recorded = await _record(client, question)

    dismiss = await client.post(f"/api/unanswered/{recorded['id']}/dismiss")
    assert dismiss.status_code == 200, dismiss.text
    assert dismiss.json()["status"] == "dismissed"

    open_queue = await client.get("/api/unanswered", params={"status": "open"})
    assert all(item["id"] != recorded["id"] for item in open_queue.json())
