import os
from typing import List
from dotenv import load_dotenv
import pytest
import vcr
from pydantic import BaseModel, Field
from ava_mosaic_ai.llm_factory import LLMFactory, LLMProvider
from ava_mosaic_ai.config.settings import get_settings
from instructor.exceptions import InstructorRetryException

# Load environment variables
load_dotenv()

# def skip_if_no_api_key(provider):
#     key_map = {
#         LLMProvider.OPENAI: "OPENAI_API_KEY",
#         LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
#         LLMProvider.AZURE_OPENAI: "AZURE_OPENAI_API_KEY",
#     }
#     key = os.getenv(key_map[provider])
#     return pytest.mark.skipif(not key, reason=f"No API key for {provider}")


class TestCompletionModel(BaseModel):
    response: str = Field(description="Test response")
    reasoning: str = Field(description="Explanation of the response")


# Configure VCR to save cassettes
vcr = vcr.VCR(
    cassette_library_dir="tests/fixtures/vcr_cassettes",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    filter_headers=["authorization"],  # Don't record the API key
)


@pytest.fixture(scope="module")
def settings():
    return get_settings()


@pytest.mark.parametrize(
    "provider",
    [
        LLMProvider.OPENAI,
        LLMProvider.ANTHROPIC,
        LLMProvider.AZURE_OPENAI,
        # Note: We're excluding LLAMA as it typically runs locally and doesn't need VCR
    ],
)
def test_e2e_completion_generation(provider, settings):
    llm = LLMFactory(provider)

    # Use the provider name in the cassette name for unique cassettes per provider
    with vcr.use_cassette(f"{provider.value}_e2e_test.yaml"):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "What are three key benefits of end-to-end testing in software development?",
            },
        ]

        completion = llm.create_completion(
            response_model=TestCompletionModel,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            max_retries=1,
        )

        assert isinstance(completion, TestCompletionModel)
        assert len(completion.response) > 0
        assert len(completion.reasoning) > 0

        print(f"Response: {completion.response}\n")
        print(f"Reasoning: {completion.reasoning}")

@pytest.mark.parametrize("provider", [LLMProvider.OPENAI, LLMProvider.ANTHROPIC])
def test_e2e_parameter_handling(provider):
    llm = LLMFactory(provider)

    with vcr.use_cassette(f"{provider.value}_parameter_test.yaml"):
        class User(BaseModel):
            name: str = Field(description="Name of the user")
            age: int = Field(description="Age of the user")
            explanation: str = Field(
                description="Explanation of the response in 5th grade math"
            )

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Marry is 25 years old, Jason is 12 years younger than merry. what is the age of jason?",
            },
        ]

        # Test with different temperature values
        completion_low_temp = llm.create_completion(
            response_model=User, messages=messages, temperature=0.2, max_tokens=100
        )
        print(completion_low_temp)

        completion_high_temp = llm.create_completion(
            response_model=User, messages=messages, temperature=0.8, max_tokens=100
        )

        # The responses should be different due to different temperature settings
        assert completion_low_temp.explanation != completion_high_temp.explanation

        # Check that max_tokens is respected
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        assert len(encoding.encode(completion_low_temp.explanation)) <= 100
        assert len(encoding.encode(completion_high_temp.explanation)) <= 100


def test_e2e_error_handling():
    # Test with an invalid API key to trigger an error
    with pytest.raises(
        InstructorRetryException
    ):  # Replace with the specific exception your code raises
        with vcr.use_cassette("invalid_api_key_test.yaml"):
            # set env variable to invalid key
            os.environ.update({"OPENAI_API_KEY": "invalid_key"})
            # os.environ.pop("OPENAI_API_KEY")
            llm = LLMFactory(LLMProvider.OPENAI)
            llm.settings.api_key = "invalid_key"

            messages = [{"role": "user", "content": "Hello, tell me a joke."}]

            resp = llm.create_completion(
                response_model=TestCompletionModel, messages=messages, max_retries=1
            )
            print(resp)


if __name__ == "__main__":
    pytest.main()
