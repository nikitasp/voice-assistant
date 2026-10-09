from pydantic import BaseModel, Field


class VoiceOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    description: str
    provider_voice_id: str
    active: bool


class ActiveVoiceRequest(BaseModel):
    voice_id: str = Field(min_length=1)
