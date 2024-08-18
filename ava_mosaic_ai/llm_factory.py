from typing import Any, Dict, List, Type, Union
import instructor
from anthropic import Anthropic
from openai import OpenAI, AzureOpenAI
from pydantic import BaseModel, Field
from ava_mosaic_ai.utils.utils import get_llm_provider
from ava_mosaic_ai.config.settings import LLMProvider, get_settings


class LLMFactory:
    def __init__(self, provider: Union[LLMProvider, str]) -> None:
        if isinstance(provider, str):
            provider = get_llm_provider(provider)

        self.provider = provider
        self.settings = get_settings().get_provider_settings(provider)
        self._api_key = self.settings.api_key
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        client_initializers = {
            LLMProvider.OPENAI: lambda: instructor.from_openai(
                OpenAI(api_key=self._api_key)
            ),
            LLMProvider.ANTHROPIC: lambda: instructor.from_anthropic(
                Anthropic(api_key=self._api_key)
            ),
            LLMProvider.LLAMA: lambda: instructor.from_openai(
                OpenAI(base_url=self.settings.base_url, api_key=self._api_key),
                mode=instructor.Mode.JSON,
            ),
            LLMProvider.AZURE_OPENAI: lambda: instructor.from_openai(
                AzureOpenAI(
                    api_key=self._api_key,
                    azure_endpoint=self.settings.azure_endpoint,
                    api_version=self.settings.api_version,
                )
            ),
        }

        initializer = client_initializers.get(self.provider)

        if initializer:
            return initializer()
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        self.client = self._initialize_client()

    def create_completion(
        self, response_model: Type[BaseModel], messages: List[Dict[str, str]], **kwargs
    ) -> Any:
        completion_params = {
            "model": kwargs.get("model", self.settings.default_model),
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "response_model": response_model,
            "messages": messages,
        }
        return self.client.chat.completions.create(**completion_params)
