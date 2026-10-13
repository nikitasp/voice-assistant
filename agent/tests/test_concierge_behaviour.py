"""Concierge behaviour in text mode with the knowledge-base tools mocked.

VC-2, VC-3, VC-4, VC-5, VC-6, NF-4, TC-3, TC-4.
"""

import pytest
import pytest_asyncio
from livekit.agents import AgentSession, mock_tools

from concierge.assistant import Concierge

from .support import (
    UnansweredRecorder,
    assert_speakable,
    backend_down,
    faq,
    search_returning,
    tool_calls,
)

pytestmark = pytest.mark.asyncio

POKER_ROOM = faq(
    "poker-room",
    "Is the poker room open?",
    "Poker Room: 24/7 operation. Texas Hold'em (No Limit and Limit), Omaha, and Seven Card Stud. "
    "Daily tournaments at 11 AM and 7 PM. $200 buy-in for daily tournaments.",
)

# Deliberately differs from the PRD (8 AM - 8 PM) to prove the reply comes from the tool result.
POOL_ALTERED = faq(
    "pool-complex",
    "When is the pool open?",
    "Pool Complex: three pools including an adults-only infinity pool. Open 9 AM - 7 PM.",
)


async def test_property_question_searches_knowledge_base(session, model):
    mock_tools(Concierge, {"search_faq": search_returning(POKER_ROOM)}, session=session)

    result = await session.run(user_input="Is the poker room open right now?")

    result.expect.contains_function_call(name="search_faq")
    await result.expect.contains_message(role="assistant").judge(
        model, intent="Says the poker room is open 24 hours a day, every day."
    )
    assert_speakable(result)


async def test_answer_uses_facts_from_search_result(session, model):
    mock_tools(Concierge, {"search_faq": search_returning(POOL_ALTERED)}, session=session)

    result = await session.run(user_input="What time does the pool open and close?")

    await result.expect.contains_message(role="assistant").judge(
        model, intent="Says the pool is open from 9 AM to 7 PM. Does not mention 8 AM or 8 PM."
    )
    assert_speakable(result)


async def test_answer_includes_relevant_details(session, model):
    mock_tools(Concierge, {"search_faq": search_returning(POKER_ROOM)}, session=session)

    result = await session.run(user_input="Are there any poker tournaments today?")

    await result.expect.contains_message(role="assistant").judge(
        model, intent="Mentions daily tournaments at 11 AM and 7 PM with a $200 buy-in."
    )
    assert_speakable(result)


@pytest.mark.parametrize(
    "question,topic",
    [
        ("Can I bring my dog to the hotel?", "dog"),
        ("Is there a shuttle to the airport?", "shuttle"),
        ("Do you have cookies?", "cookie"),
        ("Can I turn to the dark side?", "dark"),
    ],
)
async def test_unknown_question_is_recorded_and_apologized(session, model, question, topic):
    recorder = UnansweredRecorder()
    mock_tools(
        Concierge,
        {"search_faq": search_returning(), "record_unanswered": recorder},
        session=session,
    )

    result = await session.run(user_input=question)

    calls = tool_calls(result)
    assert "search_faq" in calls and "record_unanswered" in calls, calls
    assert calls.index("search_faq") < calls.index("record_unanswered"), calls
    assert any(topic in q.lower() for q in recorder.questions), recorder.questions
    await result.expect.contains_message(role="assistant").judge(
        model,
        intent=(
            "Politely says it does not have this information or declines the request, "
            "confirms the question has been noted for the team, and does not make up an answer."
        ),
    )
    assert_speakable(result)


PROPERTY_INFO = """\
Bars & Lounges:
- Eclipse Lounge: Rooftop bar with Strip views. Craft cocktails, champagne menu. Open 5 PM - 2 AM. Formal attire after 8 PM.

Celebrations & Special Events:
- Birthday/Anniversary: Celebration packages include room upgrade, champagne, custom cake, and dinner credit. From $500 additional. 72-hour advance notice required.

Partner Discounts (Show Room Key):
- Carbone (Italian fine dining, 5 min away): 15% off food, priority reservations
- Top Golf Las Vegas: Free hour with 2-hour booking
- Helicopter Tours - Vegas Nights Aviation: 20% off Strip tours, complimentary champagne
"""


@pytest_asyncio.fixture
async def property_session(model):
    async with AgentSession(llm=model) as agent_session:
        await agent_session.start(Concierge(property_info=PROPERTY_INFO))
        yield agent_session


@pytest.mark.parametrize(
    "question,intent",
    [
        (
            "What discounts do you have for hotel guests?",
            (
                "Names at least two partner discounts such as Carbone, Topgolf or helicopter tours. "
                "Does not say the information is unavailable."
            ),
        ),
        (
            "I want to propose to my girlfriend this weekend. Can you help?",
            (
                "Responds warmly and suggests the celebration package or Eclipse Lounge. "
                "Does not say the information is unavailable."
            ),
        ),
    ],
)
async def test_answers_from_property_information(property_session, model, question, intent):
    recorder = UnansweredRecorder()
    mock_tools(
        Concierge,
        {"search_faq": search_returning(), "record_unanswered": recorder},
        session=property_session,
    )

    result = await property_session.run(user_input=question)

    assert recorder.questions == [], recorder.questions
    await result.expect.contains_message(role="assistant").judge(model, intent=intent)
    assert_speakable(result)


async def test_backend_failure_gives_polite_fallback(session, model):
    mock_tools(
        Concierge,
        {"search_faq": backend_down, "record_unanswered": backend_down},
        session=session,
    )

    result = await session.run(user_input="What time does Aurelia open?")

    await result.expect.contains_message(role="assistant").judge(
        model,
        intent=(
            "Apologizes that it cannot look this up right now and offers another way to get help, "
            "such as the front desk. Does not state Aurelia's opening hours."
        ),
    )
    assert_speakable(result)


async def test_record_failure_does_not_claim_question_was_noted(session, model):
    """VC-5 / KB-3: search empty but record HTTP failure must not claim the question was saved."""

    def record_failed(context=None, question: str = "") -> str:
        return (
            "Recording failed. Do not tell the guest that the question was noted. "
            "Apologize that you cannot look that up right now and offer the front desk at extension 0."
        )

    mock_tools(
        Concierge,
        {"search_faq": search_returning(), "record_unanswered": record_failed},
        session=session,
    )

    result = await session.run(user_input="Do you have a dentist on site?")

    await result.expect.contains_message(role="assistant").judge(
        model,
        intent=(
            "Apologizes that it cannot help or look this up right now and offers the front desk. "
            "Does not say the question has been noted, recorded, or saved for the team."
        ),
    )
    assert_speakable(result)


@pytest.mark.parametrize(
    "question,item",
    [
        ("Is the poker room open right now?", POKER_ROOM),
        ("hey whats up, is the pool open", POOL_ALTERED),
    ],
)
async def test_tone_is_warm_and_professional(session, model, question, item):
    mock_tools(Concierge, {"search_faq": search_returning(item)}, session=session)

    result = await session.run(user_input=question)

    await result.expect.contains_message(role="assistant").judge(
        model,
        intent=(
            "Warm, polite and professional, as a concierge at a luxury hotel would speak. "
            "No slang. Short enough to be spoken aloud comfortably."
        ),
    )
    assert_speakable(result)
