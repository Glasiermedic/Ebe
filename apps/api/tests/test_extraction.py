from unittest.mock import Mock

from app.schemas import ExtractedMemory
from app.services.extraction import OpenAIMemoryExtractionProvider


def test_openai_extraction_provider_returns_parsed_memory() -> None:
    expected = ExtractedMemory(
        title="First Date",
        content="Met Laura for dinner.",
    )

    provider = OpenAIMemoryExtractionProvider(
        api_key="test-key",
        model_name="test-model",
    )

    provider.client = Mock()
    provider.client.responses.parse.return_value = Mock(
        output_parsed=expected
    )

    result = provider.extract("Met Laura for dinner.")

    assert result == expected

    provider.client.responses.parse.assert_called_once()


def test_openai_extraction_provider_rejects_missing_output() -> None:
    provider = OpenAIMemoryExtractionProvider(
        api_key="test-key",
        model_name="test-model",
    )

    provider.client = Mock()
    provider.client.responses.parse.return_value = Mock(
        output_parsed=None
    )

    try:
        provider.extract("A memory")
    except RuntimeError as error:
        assert "did not return structured memory data" in str(error)
    else:
        raise AssertionError("Expected RuntimeError")