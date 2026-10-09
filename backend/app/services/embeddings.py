from __future__ import annotations

import asyncio
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.models.faq import EMBEDDING_DIM


@lru_cache
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class EmbeddingService:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    def _encode_sync(self, texts: list[str]) -> list[list[float]]:
        model = _load_model(self._model_name)
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        array = np.asarray(vectors, dtype=np.float32)
        if array.ndim == 1:
            array = array.reshape(1, -1)
        if array.shape[1] != EMBEDDING_DIM:
            raise RuntimeError(
                f"Embedding dimension {array.shape[1]} does not match expected {EMBEDDING_DIM}"
            )
        return array.tolist()

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._encode_sync, texts)

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self.embed_texts([text])
        return vectors[0]

    def warm_up(self) -> None:
        _load_model(self._model_name)
