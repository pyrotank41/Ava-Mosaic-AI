import json
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
import uuid
import instructor
from anthropic import Anthropic
from openai import OpenAI, AzureOpenAI
from pydantic import BaseModel, Field
from ava_mosaic_ai.utils.utils import get_llm_provider
from ava_mosaic_ai.config.settings import LLMProvider, get_settings
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from instructor import Instructor
from anthropic import Anthropic

import httpx
from collections import OrderedDict
import time


class CustomHTTPXClient(httpx.Client):
    def __init__(self, *args, max_cache_size=1000, cache_ttl=3600, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_cache = OrderedDict()
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl

    def send(self, request: httpx.Request, *args, **kwargs):
        if "x-trace-id" not in request.headers:
            raise ValueError("x-trace-id header is required")

        trace_id = request.headers["x-trace-id"]

        # Capture request data
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "content": self._parse_json(request.content.decode())
            if request.content
            else None,
        }

        response = super().send(request, *args, **kwargs)

        # make sure to add x-trace-id to the response header if it is not present
        if "x-trace-id" not in response.headers:
            response.headers["x-trace-id"] = trace_id

        # Capture response data
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": self._parse_json(response.text),
        }

        self._add_to_cache(trace_id, request_data, response_data)

        return response

    def _add_to_cache(self, trace_id, request_data, response_data):
        if len(self.response_cache) >= self.max_cache_size:
            self.response_cache.popitem(last=False)

        self.response_cache[trace_id] = {
            "request": request_data,
            "response": response_data,
            "timestamp": time.time(),
        }

    def _parse_json(self, content: str) -> Union[Dict, List, str]:
        """
        Attempt to parse the content as JSON. If parsing fails, return the original string.
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    def get_request_response_data(self, trace_id):
        if trace_id in self.response_cache:
            cache_entry = self.response_cache[trace_id]
            if time.time() - cache_entry["timestamp"] <= self.cache_ttl:
                return cache_entry["request"], cache_entry["response"]
            else:
                del self.response_cache[trace_id]
        return None, None

    def clear_expired_cache(self):
        current_time = time.time()
        self.response_cache = OrderedDict(
            (k, v)
            for k, v in self.response_cache.items()
            if current_time - v["timestamp"] <= self.cache_ttl
        )


class LLMFactory:
    def __init__(
        self,
        provider: Union[LLMProvider, str],
        metadata: Optional[dict] = None,
        http_client: Any = None,
    ) -> None:
        if isinstance(provider, str):
            provider = get_llm_provider(provider)
        self.http_client = http_client
        if self.http_client is None:
            print("No http_client provided, Creating new http client")
            self.http_client = CustomHTTPXClient(max_cache_size=1000, cache_ttl=3600)

        self.metadata = metadata
        self.provider = provider
        self.settings = get_settings().get_provider_settings(provider)
        self._api_key = self.settings.api_key
        self.client = self._initialize_client()

    def _initialize_client(self) -> Instructor:
        client_initializers = {
            LLMProvider.OPENAI: lambda: instructor.from_openai(
                OpenAI(http_client=self.http_client, api_key=self._api_key)
            ),
            LLMProvider.ANTHROPIC: lambda: instructor.from_anthropic(
                Anthropic(http_client=self.http_client, api_key=self._api_key)
            ),
            LLMProvider.LLAMA: lambda: instructor.from_openai(
                OpenAI(
                    http_client=self.http_client,
                    base_url=self.settings.base_url,
                    api_key=self._api_key,
                ),
                mode=instructor.Mode.JSON,
            ),
            LLMProvider.AZURE_OPENAI: lambda: instructor.from_openai(
                AzureOpenAI(
                    http_client=self.http_client,
                    api_key=self._api_key,
                    azure_endpoint=self.settings.azure_endpoint,
                    api_version=self.settings.api_version,
                )
            ),
            LLMProvider.PORTKEY_AZURE_OPENAI: lambda: instructor.from_openai(
                OpenAI(
                    http_client=self.http_client,
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
                    http_client=self.http_client,
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
        self,
        response_model: Type[T],
        messages: List[Dict[str, str]],
        extra_headers: Dict[str, str] = {},
        **kwargs,
    ) -> T:
        trace_id = extra_headers.get("x-trace-id")
        if trace_id is None:
            trace_id = str(uuid.uuid4())
            extra_headers["x-trace-id"] = trace_id

        # TODO: if portkey is not used, then this should not be added to the extra_headers, adding it for all request as it doesnt hurt
        if extra_headers.get("x-portkey-trace-id") is None:
            extra_headers["x-portkey-trace-id"] = trace_id

        completion_params = {
            "model": kwargs.get("model", self.settings.default_model),
            "temperature": kwargs.get("temperature", self.settings.temperature),
            "max_retries": kwargs.get("max_retries", self.settings.max_retries),
            "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
            "response_model": response_model,
            "messages": messages,
            "extra_headers": extra_headers,
        }

        start_time = time.time()
        response = self.client.chat.completions.create(**completion_params)
        end_time = time.time()

        request_time = end_time - start_time

        # Retrieve HTTP request and response data
        request_data, response_data = self.http_client.get_request_response_data(
            trace_id
        )

        # Embed the trace_id, request_time, and HTTP request/response data in the response object
        if hasattr(response, "__dict__"):
            response.__dict__["_audit_data"] = {
                "trace_id": trace_id,
                "request_time": request_time,
                "http_request": request_data,
                "http_response": response_data,
            }

        return response

    @staticmethod
    def get_audit_data(response: BaseModel) -> Optional[Dict]:
        """Retrieve the audit_data from a response object."""
        return getattr(response, "_audit_data", None)

    @staticmethod
    def get_trace_id(response: BaseModel) -> Optional[str]:
        """Retrieve the trace_id from a response object."""
        audit_data = getattr(response, "_audit_data", None)
        if audit_data is None:
            return None

        return audit_data.get("trace_id")
