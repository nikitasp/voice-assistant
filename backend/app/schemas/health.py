from pydantic import BaseModel


class ProviderCheck(BaseModel):
    ok: bool
    detail: str


class ProvidersHealthResponse(BaseModel):
    llm: ProviderCheck
    stt: ProviderCheck
    tts: ProviderCheck
