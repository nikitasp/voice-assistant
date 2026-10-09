"""PRD example conversations and other scenarios against the real backend.

VC-2, VC-3, VC-4, VC-5, VC-6, KB-5, NF-4, TC-3, TC-4.
"""

import pytest

from .support import assert_speakable, load_data, tool_calls

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]

SCENARIOS = load_data("scenarios.yaml")


def assert_called_in_order(called: list[str], expected: list[str]) -> None:
    remaining = iter(called)
    missing = [name for name in expected if name not in remaining]
    assert not missing, f"expected tool calls {expected} in order, got {called}"


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s["id"])
async def test_scenario(backend_url, session, model, scenario):
    result = await session.run(user_input=scenario["question"])

    assert_called_in_order(tool_calls(result), scenario["tools"])
    await result.expect.contains_message(role="assistant").judge(model, intent=scenario["intent"])
    assert_speakable(result)
