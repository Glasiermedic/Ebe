import hashlib
from typing import Protocol

from openai import OpenAI

from app.config import get_settings
from app.models import MemoryStone


class EmbeddingProvider(Protocol):
    @property
    def model_name(self) -> str:
        """Return the embedding model name."""
        ...

    def embed(self, text: str) -> list[float]:
        """Convert text into an embedding vector."""
        ...


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        dimensions: int,
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self._model_name = model_name
        self.dimensions = dimensions

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text,
            dimensions=self.dimensions,
            encoding_format="float",
        )

        embedding = response.data[0].embedding

        if len(embedding) != self.dimensions:
            raise RuntimeError(
                "Embedding provider returned "
                f"{len(embedding)} dimensions; "
                f"expected {self.dimensions}."
            )

        return embedding


def build_memory_stone_embedding_text(
    stone: MemoryStone,
) -> str:
    parts = [
        f"Title: {stone.title}",
        f"Content: {stone.content}",
        f"Stone type: {stone.stone_type}",
        f"Source type: {stone.source_type}",
    ]

    if stone.source_reference:
        parts.append(
            f"Source reference: {stone.source_reference}"
        )

    if stone.remembered_at:
        parts.append(
            f"Remembered date: {stone.remembered_at.isoformat()}"
        )

    return "\n".join(parts)


def calculate_embedding_source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embedding_is_current(
    stone: MemoryStone,
    *,
    provider_model_name: str,
) -> bool:
    if stone.embedding is None:
        return False

    if stone.embedding_model != provider_model_name:
        return False

    embedding_text = build_memory_stone_embedding_text(stone)
    current_hash = calculate_embedding_source_hash(
        embedding_text
    )

    return stone.embedding_source_hash == current_hash


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required for embedding operations."
        )

    return OpenAIEmbeddingProvider(
        api_key=settings.openai_api_key,
        model_name=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )