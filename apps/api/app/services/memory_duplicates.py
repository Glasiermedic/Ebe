import hashlib


def normalize_memory_input(text: str) -> str:
    return " ".join(text.casefold().split())


def calculate_memory_input_hash(text: str) -> str:
    normalized_text = normalize_memory_input(text)

    return hashlib.sha256(
        normalized_text.encode("utf-8")
    ).hexdigest()
