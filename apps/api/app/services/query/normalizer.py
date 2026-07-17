import string

from app.services.query.models import NormalizedQuery

QUERY_PREFIXES = (
    "tell me about",
    "what do you know about",
    "who is",
    "what is",
)


def normalize_query(query: str) -> NormalizedQuery:
    normalized = query.strip()
    lowered = normalized.lower()

    for prefix in QUERY_PREFIXES:
        if lowered.startswith(prefix):
            normalized = normalized[len(prefix) :].strip()
            break

    normalized = normalized.strip(string.whitespace + string.punctuation)

    return NormalizedQuery(
        original=query,
        normalized=normalized,
    )
