import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field

from ava_mosaic_ai.config.settings import LLMProvider, Settings
from ava_mosaic_ai import (
    LLMFactory
) 

class CompletionModel(BaseModel):
    response: str = Field(description="Your response to the user.")
    reasoning: str = Field(description="Explain your reasoning for the response.")
    
    model_config = ConfigDict(populate_by_name=True)


@pytest.fixture
def mock_settings():
    settings = Mock(spec=Settings)
    settings.get_provider_settings.return_value = Mock(
        api_key="test_key",
        default_model="test_model",
        temperature=0.7,
        max_retries=3,
        max_tokens=100,
    )
    return settings

@pytest.fixture
def mock_get_settings(mock_settings):
    with patch(
        "ava_mosaic_ai.llm_factory.get_settings", return_value=mock_settings
    ) as mock:
        yield mock



@pytest.fixture
def mock_instructor():
    with patch(
        "ava_mosaic_ai.llm_factory.instructor"
    ) as mock: 
        yield mock


@pytest.fixture
def llm_factory(mock_get_settings, mock_instructor):
    return LLMFactory(LLMProvider.OPENAI)

def test_initialization(llm_factory, mock_get_settings):
    assert llm_factory.provider == LLMProvider.OPENAI
    assert llm_factory.settings is not None
    assert llm_factory.client is not None
    mock_get_settings.assert_called_once()


def test_initialize_client_openai(mock_instructor, mock_get_settings):
    factory = LLMFactory(LLMProvider.OPENAI)
    mock_instructor.from_openai.assert_called_once()


def test_initialize_client_anthropic(mock_instructor, mock_get_settings):
    factory = LLMFactory(LLMProvider.ANTHROPIC)
    mock_instructor.from_anthropic.assert_called_once()


def test_initialize_client_llama(mock_instructor):
    settings = Mock(spec=Settings)
    settings.get_provider_settings.return_value = Mock(
        api_key="test_key",
        default_model="test_model",
        base_url="http://localhost:11434/v1",
        temperature=0.7,
        max_retries=3,
        max_tokens=100,
    )
    with patch("ava_mosaic_ai.llm_factory.get_settings", return_value=settings) as mock:
        factory = LLMFactory(LLMProvider.LLAMA)
    mock_instructor.from_openai.assert_called_once()


def test_initialize_client_azure_openai(mock_instructor, mock_get_settings):
    factory = LLMFactory(LLMProvider.AZURE_OPENAI)
    mock_instructor.from_openai.assert_called_once()


def test_initialize_client_unsupported():
    with pytest.raises(AttributeError, match="'UNSUPPORTED_PROVIDER' is not supported"):
        LLMFactory("UNSUPPORTED_PROVIDER")

def test_create_completion(llm_factory):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ]

    mock_completion = Mock(spec=CompletionModel)
    mock_completion.response = "I'm doing well, thank you!"
    mock_completion.reasoning = "As an AI assistant, I'm functioning properly."

    llm_factory.client.chat.completions.create.return_value = mock_completion

    result = llm_factory.create_completion(
        response_model=CompletionModel,
        messages=messages,
    )

    assert isinstance(result, CompletionModel)
    assert result.response == "I'm doing well, thank you!"
    assert result.reasoning == "As an AI assistant, I'm functioning properly."

    llm_factory.client.chat.completions.create.assert_called_once_with(
        model=llm_factory.settings.default_model,
        temperature=llm_factory.settings.temperature,
        max_retries=llm_factory.settings.max_retries,
        max_tokens=llm_factory.settings.max_tokens,
        response_model=CompletionModel,
        messages=messages,
    )


def test_create_completion_with_custom_params(llm_factory):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ]

    mock_completion = Mock(spec=CompletionModel)
    llm_factory.client.chat.completions.create.return_value = mock_completion

    custom_model = "gpt-4"
    custom_temperature = 0.9
    custom_max_retries = 5
    custom_max_tokens = 200

    llm_factory.create_completion(
        response_model=CompletionModel,
        messages=messages,
        model=custom_model,
        temperature=custom_temperature,
        max_retries=custom_max_retries,
        max_tokens=custom_max_tokens,
    )

    llm_factory.client.chat.completions.create.assert_called_once_with(
        model=custom_model,
        temperature=custom_temperature,
        max_retries=custom_max_retries,
        max_tokens=custom_max_tokens,
        response_model=CompletionModel,
        messages=messages,
    )

