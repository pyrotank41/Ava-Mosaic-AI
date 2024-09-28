from typing import Any, Dict, List, Optional, Type, TypeVar, Union
import instructor
from anthropic import Anthropic
from openai import OpenAI, AzureOpenAI
from pydantic import BaseModel, Field
from ava_mosaic_ai.utils.utils import get_llm_provider
from ava_mosaic_ai.config.settings import LLMProvider, get_settings
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from instructor import Instructor
from anthropic import Anthropic


def get_portkey_azure_openai_client(portkey_api_key: str, virtual_api_key: str):
    portkey = OpenAI(
        api_key="gpt-4o-2024-08-bc0138",
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            # provider="openai",
            virtual_key="gpt-4o-2024-08-bc0138",
            api_key="KPhEnBPeKn5DQneaHaC6LLcfrGgw",
        ),
    )
    return instructor.from_openai(portkey)


class LLMFactory:
    def __init__(
        self, 
        provider: Union[LLMProvider, str],
        metadata: Optional[dict] = None
    ) -> None:
        if isinstance(provider, str):
            provider = get_llm_provider(provider)

        self.metadata = metadata
        print(f"metadata: {metadata}")
        self.provider = provider
        self.settings = get_settings().get_provider_settings(provider)
        self._api_key = self.settings.api_key
        self.client = self._initialize_client()

    def _initialize_client(self) -> Instructor:
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
            LLMProvider.PORTKEY_AZURE_OPENAI: lambda: instructor.from_openai(
                OpenAI(
                    api_key=self.settings.virtual_api_key,
                    base_url=PORTKEY_GATEWAY_URL,
                    default_headers=createHeaders(
                        provider="openai",
                        virtual_key=self.settings.virtual_api_key,
                        api_key=self._api_key,
                        metadata=self.metadata,
                    ),
                )
            ),
            LLMProvider.PORTKEY_ANTHROPIC: lambda: instructor.from_anthropic(
                Anthropic(
                    api_key=self.settings.virtual_api_key,
                    base_url=PORTKEY_GATEWAY_URL,
                    default_headers=createHeaders(
                        provider="anthropic",
                        virtual_key=self.settings.virtual_api_key,
                        api_key=self._api_key,
                        metadata=self.metadata,
                    ),
                )
                # .with_options(self.metadata)
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

    T = TypeVar("T", bound=BaseModel)

    def create_completion(
        self, response_model: Type[T], messages: List[Dict[str, str]], **kwargs
    ) -> T:
        completion_params = {
            "model": kwargs.get("model", self.settings.default_model),
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "response_model": response_model,
            "messages": messages,
        }
        # metadata = kwargs.get("metadata", None)
        # client_with_metadata = self.client.with_options(metadata={"_user": "user_12345", "custom_field": "custom_value"})
        # if metadata is not None:
        #     return client_with_metadata.chat.completions.create(**completion_params)
        return self.client.chat.completions.create(**completion_params)
