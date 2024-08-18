# import pytest
# from unittest.mock import patch, MagicMock
# from pydantic import BaseModel, Field
# from ava_mosaic_ai.llm_factory import LLMFactory, LLMProvider
# from ava_mosaic_ai.config.settings import (
#     OpenAISettings,
#     AnthropicSettings,
#     LlamaSettings,
#     AzureOpenAISettings,
# )


# class TestCompletionModel(BaseModel):
#     response: str = Field(description="Test response")
#     confidence: float = Field(description="Confidence score", ge=0, le=1)


# @pytest.fixture
# def mock_openai_completion():
#     with patch("openai.OpenAI") as mock_openai:
#         mock_client = MagicMock()
#         mock_client.chat.completions.create.return_value = TestCompletionModel(
#             response="Paris is the capital of France.", confidence=0.95
#         )
#         mock_openai.return_value = mock_client
#         yield mock_openai


# @pytest.fixture
# def mock_anthropic_completion():
#     with patch("anthropic.Anthropic") as mock_anthropic:
#         mock_client = MagicMock()
#         mock_client.completions.create.return_value = TestCompletionModel(
#             response="The capital of France is Paris.", confidence=0.98
#         )
#         mock_anthropic.return_value = mock_client
#         yield mock_anthropic


# @pytest.fixture
# def mock_llama_completion():
#     with patch("openai.OpenAI") as mock_llama:
#         mock_client = MagicMock()
#         mock_client.chat.completions.create.return_value = TestCompletionModel(
#             response="Paris, the city of lights, is the capital of France.",
#             confidence=0.92,
#         )
#         mock_llama.return_value = mock_client
#         yield mock_llama


# @pytest.fixture
# def mock_azure_openai_completion():
#     with patch("openai.AzureOpenAI") as mock_azure:
#         mock_client = MagicMock()
#         mock_client.chat.completions.create.return_value = TestCompletionModel(
#             response="France's capital city is Paris.", confidence=0.97
#         )
#         mock_azure.return_value = mock_client
#         yield mock_azure


# @pytest.mark.parametrize(
#     "provider, mock_fixture, settings_class",
#     [
#         (LLMProvider.OPENAI, "mock_openai_completion", OpenAISettings),
#         (LLMProvider.ANTHROPIC, "mock_anthropic_completion", AnthropicSettings),
#         (LLMProvider.LLAMA, "mock_llama_completion", LlamaSettings),
#         (LLMProvider.AZURE_OPENAI, "mock_azure_openai_completion", AzureOpenAISettings),
#     ],
# )
# def test_completion_generation(provider, mock_fixture, settings_class, request):
#     # Use the mock fixture
#     mock_completion = request.getfixturevalue(mock_fixture)

#     # Mock the settings
#     mock_settings = settings_class(api_key="fake_key")
#     if provider == LLMProvider.AZURE_OPENAI:
#         mock_settings.azure_endpoint = "https://fake-endpoint.openai.azure.com"

#     with patch("ava_mosaic_ai.llm_factory.get_settings") as mock_get_settings:
#         mock_get_settings.return_value.get_provider_settings.return_value = (
#             mock_settings
#         )

#         llm = LLMFactory(provider)
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "What's the capital of France?"},
#         ]

#         completion = llm.create_completion(
#             response_model=TestCompletionModel,
#             messages=messages,
#             temperature=0.7,
#             max_tokens=50,
#         )

#         assert isinstance(completion, TestCompletionModel)
#         assert "Paris" in completion.response
#         assert 0 <= completion.confidence <= 1

#         # Verify that the mock was called with the correct parameters
#         if provider in [
#             LLMProvider.OPENAI,
#             LLMProvider.LLAMA,
#             LLMProvider.AZURE_OPENAI,
#         ]:
#             mock_completion.return_value.chat.completions.create.assert_called_once()
#         elif provider == LLMProvider.ANTHROPIC:
#             mock_completion.return_value.completions.create.assert_called_once()

#         # You can add more specific assertions here to check the exact parameters passed to the API call
