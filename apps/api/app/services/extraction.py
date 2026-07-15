from typing import Protocol

from openai import OpenAI

from app.config import get_settings
from app.schemas import ExtractedMemory


EXTRACTION_INSTRUCTIONS = """
You extract personal memories into structured data for Ebe.

Rules:
- Preserve the user's meaning without embellishment.
- Do not invent names, dates, coordinates, events, or biographical facts.
- Use null when information is unknown.
- Keep content faithful to the original text.
- Create a concise descriptive title.
- A person is a named or clearly identified human.
- A place is a named or clearly identified physical location.
- An event is a distinct occurrence worth linking as a reusable graph node.
- Do not create an event merely because the memory itself happened.
- Set remembered_at only when the date is explicitly stated or reliably
  derivable from the user's words.
- Mark is_inferred true when important structured details required inference.
- Reduce confidence when dates, identities, or relationships are uncertain.
- Relationship types should be short snake_case labels such as:
  subject, companion, witness, location, destination, occurred_during.
- source_type should normally be user_entry.
- source_reference should normally be Direct recollection entered by user.
"""


class MemoryExtractionProvider(Protocol):
    def extract(self, text: str) -> ExtractedMemory:
        """Extract a structured memory from natural-language text."""
        ...


class OpenAIMemoryExtractionProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def extract(self, text: str) -> ExtractedMemory:
        response = self.client.responses.parse(
            model=self.model_name,
            input=[
                {
                    "role": "system",
                    "content": EXTRACTION_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            text_format=ExtractedMemory,
        )

        extracted = response.output_parsed

        if extracted is None:
            raise RuntimeError(
                "The extraction model did not return structured memory data."
            )

        return extracted


def get_memory_extraction_provider() -> MemoryExtractionProvider:
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required for memory extraction."
        )

    return OpenAIMemoryExtractionProvider(
        api_key=settings.openai_api_key,
        model_name=settings.extraction_model,
    )