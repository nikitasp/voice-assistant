"""KB-5: the full property information sheet is available to the concierge."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_property_info_lists_every_section(client):
    response = await client.get("/api/property")

    assert response.status_code == 200
    titles = [section["title"] for section in response.json()["sections"]]
    assert "Partner Discounts (Show Room Key)" in titles
    assert "Celebrations & Special Events" in titles
    assert "Bars & Lounges" in titles


async def test_property_info_includes_all_partner_discounts(client):
    body = (await client.get("/api/property")).json()

    partners = next(s for s in body["sections"] if s["title"].startswith("Partner Discounts"))
    names = " ".join(item["name"] for item in partners["items"])
    for partner in ["Carbone", "Omega Mart", "Helicopter", "Top Golf", "Spa Aquae", "Fremont"]:
        assert partner in names
