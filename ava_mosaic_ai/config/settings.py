from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LLAMA = "llama"
    AZURE_OPENAI = "azure_openai"


class LLMProviderSettings(BaseModel):
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    max_retries: int = 3


class OpenAISettings(LLMProviderSettings):
    api_key: str
    default_model: str = "gpt-4"


class AnthropicSettings(LLMProviderSettings):
    api_key: str
    default_model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 1024


class LlamaSettings(LLMProviderSettings):
    api_key: str = "key"  # required, but not used
    default_model: str = "llama3"
    base_url: str = "http://localhost:11434/v1"


class AzureOpenAISettings(LLMProviderSettings):
    api_key: str
    api_base: str
    api_version: str
    default_model: str = "gpt-4"


class Settings(BaseSettings):
    app_name: str = "GenAI Project Template"
    _providers: Dict[LLMProvider, Any] = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_provider_settings(self, provider: LLMProvider) -> Any:
        if provider not in self._providers:
            if provider == LLMProvider.OPENAI:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is not set")
                self._providers[provider] = OpenAISettings(api_key=api_key)
            elif provider == LLMProvider.ANTHROPIC:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError(
                        "ANTHROPIC_API_KEY environment variable is not set"
                    )
                self._providers[provider] = AnthropicSettings(api_key=api_key)
            elif provider == LLMProvider.LLAMA:
                self._providers[provider] = LlamaSettings()
            elif provider == LLMProvider.AZURE_OPENAI:
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
                api_base = os.getenv("AZURE_OPENAI_API_BASE")
                api_version = os.getenv("AZURE_OPENAI_API_VERSION")
                if not all([api_key, api_base, api_version]):
                    raise ValueError(
                        "One or more Azure OpenAI environment variables are not set"
                    )
                self._providers[provider] = AzureOpenAISettings(
                    api_key=api_key, api_base=api_base, api_version=api_version
                )
        return self._providers[provider]

@lru_cache
def get_settings() -> Settings:
    return Settings()
