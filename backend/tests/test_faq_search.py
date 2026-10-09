"""API-1, API-3, KB-2, NF-1: natural-language FAQ search."""

import statistics
import time

import pytest

from .support import load_data

pytestmark = pytest.mark.asyncio

CASES = load_data("search_cases.yaml")


async def search(client, query: str) -> dict:
    response = await client.post("/api/faq/search", json={"query": query})
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize("case", CASES["match"], ids=lambda c: c["query"])
async def test_question_finds_expected_faq(client, case):
    body = await search(client, case["query"])

    assert body["found"] is True, f"no match for {case['query']!r}"
    top = body["results"][0]
    assert top["slug"] in case["expected"], (
        f"{case['query']!r}: expected one of {case['expected']}, got {top['slug']!r} "
        f"(score {top['score']:.3f})"
    )


@pytest.mark.parametrize("query", CASES["no_match"])
async def test_unknown_question_reports_no_match(client, query):
    body = await search(client, query)

    assert body["found"] is False, f"{query!r} unexpectedly matched {body['results'][:1]}"
    assert body["results"] == []


async def test_match_response_shape(client):
    body = await search(client, "Is the poker room open right now?")

    results = body["results"]
    assert results
    for result in results:
        assert {"id", "slug", "question", "answer", "score"} <= result.keys()
        assert isinstance(result["score"], float)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("payload", [{}, {"query": ""}, {"query": "   "}])
async def test_empty_query_is_rejected(client, payload):
    response = await client.post("/api/faq/search", json=payload)

    assert response.status_code == 422


@pytest.mark.perf
async def test_search_is_fast(client):
    await search(client, "warm up")
    queries = [case["query"] for case in CASES["match"][:10]]

    timings = []
    for query in queries:
        start = time.perf_counter()
        await search(client, query)
        timings.append(time.perf_counter() - start)

    assert statistics.median(timings) < 0.3, f"median search time {statistics.median(timings):.3f}s"
