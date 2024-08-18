from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
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
    default_model: str = Field(default="gpt-4o")


class AnthropicSettings(LLMProviderSettings):
    api_key: str
    default_model: str = Field(default="claude-3-sonnet-20240229")
    max_tokens: int = Field(default=1024)


class LlamaSettings(LLMProviderSettings):
    api_key: str = Field(default="key")  # required, but not used
    default_model: str = Field(default="llama3")
    base_url: str = Field(default="http://localhost:11434/v1")


class AzureOpenAISettings(LLMProviderSettings):
    api_key: str
    api_version: str = Field(default="2024-02-15-preview")
    default_model: str = Field(default="gpt-4o")
    azure_endpoint: str


class Settings(BaseModel):
    app_name: str = Field(default="GenAI Project Template")
    _providers: Dict[LLMProvider, Any] = {}

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
                endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
                api_key = os.environ.get("AZURE_OPENAI_API_KEY")
                deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
                if not endpoint:
                    raise ValueError("Env variable AZURE_OPENAI_ENDPOINT is not set")
                if not api_key:
                    raise ValueError("Env variable AZURE_OPENAI_API_KEY is not set")
                if not deployment_name:
                    raise ValueError(
                        "Env variable AZURE_OPENAI_DEPLOYMENT_NAME is not set"
                    )
                print(f"Using Azure OpenAI provider with endpoint: {endpoint}")
                self._providers[provider] = AzureOpenAISettings(
                    api_key=api_key,
                    azure_endpoint=endpoint,
                    default_model=deployment_name,
                )
        return self._providers[provider]


@lru_cache
def get_settings() -> Settings:
    return Settings()
