"""AP-1–AP-4: FAQ list / create / update / delete with immediate searchability."""

from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


async def test_list_faq_returns_seeded_items(client):
    response = await client.get("/api/faq")
    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items) >= 1
    assert {"id", "slug", "category", "question", "answer"} <= set(items[0].keys())


async def test_list_faq_filters_by_category_and_text(client):
    created = await client.post(
        "/api/faq",
        json={
            "slug": f"crud-filter-{uuid4().hex[:8]}",
            "category": "testing-crud",
            "question": "Where is the secret testing lounge?",
            "answer": "On the mezzanine next to the elevators.",
        },
    )
    assert created.status_code == 201, created.text

    by_category = await client.get("/api/faq", params={"category": "testing-crud"})
    assert by_category.status_code == 200
    assert any(item["id"] == created.json()["id"] for item in by_category.json())

    by_text = await client.get("/api/faq", params={"q": "secret testing lounge"})
    assert by_text.status_code == 200
    assert any(item["id"] == created.json()["id"] for item in by_text.json())


async def test_create_update_delete_faq_and_search(client):
    slug = f"crud-roundtrip-{uuid4().hex[:8]}"
    create = await client.post(
        "/api/faq",
        json={
            "slug": slug,
            "category": "testing-crud",
            "question": "Does Meridian have a holographic fountain show tonight?",
            "answer": "Yes, the holographic fountain runs nightly at 9 PM on the plaza.",
        },
    )
    assert create.status_code == 201, create.text
    item = create.json()

    search = await client.post(
        "/api/faq/search",
        json={"query": "holographic fountain show tonight"},
    )
    assert search.status_code == 200, search.text
    body = search.json()
    assert body["found"] is True
    assert any(result["slug"] == slug for result in body["results"])

    update = await client.put(
        f"/api/faq/{item['id']}",
        json={
            "slug": slug,
            "category": "testing-crud",
            "question": "Does Meridian have a holographic fountain show tonight?",
            "answer": "The holographic fountain now starts at 8:30 PM on the plaza.",
        },
    )
    assert update.status_code == 200, update.text
    assert "8:30" in update.json()["answer"]

    delete = await client.delete(f"/api/faq/{item['id']}")
    assert delete.status_code == 204, delete.text

    missing = await client.put(
        f"/api/faq/{item['id']}",
        json={
            "slug": slug,
            "category": "testing-crud",
            "question": "gone",
            "answer": "gone",
        },
    )
    assert missing.status_code == 404
