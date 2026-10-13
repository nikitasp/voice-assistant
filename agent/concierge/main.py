from __future__ import annotations

import asyncio
import logging

from livekit.agents import (
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    room_io,
)
from livekit.plugins import silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from concierge.assistant import Concierge
from concierge.backend_client import BackendClient
from concierge.config import get_settings
from concierge.models import build_llm, build_stt, build_tts

logger = logging.getLogger("meridian.concierge")


def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext) -> None:
    ctx.log_context_fields = {"room": ctx.room.name}
    settings = get_settings()

    backend = BackendClient()
    active, property_info = await asyncio.gather(
        backend.get_active_provider_voice_id(),
        backend.get_property_info(),
        return_exceptions=True,
    )
    voice_id = settings.default_tts_voice_id
    if isinstance(active, BaseException):
        logger.error("Could not fetch active voice; using default", exc_info=active)
    elif active:
        voice_id = active
    if isinstance(property_info, BaseException):
        logger.error("Could not fetch property information", exc_info=property_info)
        property_info = None

    session = AgentSession(
        stt=build_stt(),
        llm=build_llm(),
        tts=build_tts(voice_id),
        vad=ctx.proc.userdata["vad"],
        turn_detection=MultilingualModel(),
        preemptive_generation=True,
        allow_interruptions=settings.allow_interruptions,
        min_interruption_duration=settings.min_interruption_duration,
        min_interruption_words=settings.min_interruption_words,
        resume_false_interruption=settings.resume_false_interruption,
        false_interruption_timeout=settings.false_interruption_timeout,
        tts_text_transforms=["filter_emoji", "filter_markdown"],
    )

    await session.start(
        agent=Concierge(property_info=property_info),
        room=ctx.room,
        room_options=room_io.RoomOptions(text_input=True),
    )
    await session.generate_reply(
        instructions=(
            "Greet the guest warmly as the Meridian concierge and invite them to ask "
            "about the property."
        )
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
