import uuid
from pydantic import BaseModel
from ava_mosaic_ai.config.settings import LLMProvider
from ava_mosaic_ai.llm_factory import LLMFactory

# client = LLMFactory(LLMProvider.PORTKEY_AZURE_OPENAI)
# client = LLMFactory(LLMProvider.AZURE_OPENAI)

client = LLMFactory(LLMProvider.PORTKEY_ANTHROPIC, metadata=metadata)

class User(BaseModel):
    name: str
    age: int

# client = instructor.from_openai(portkey)
user_info = client.create_completion(
    # model="gpt-4o",
    max_tokens=1024,
    response_model=User,
    messages=[{"role": "user", "content": "John Doe is 30 years old."}],
)

print(user_info.name)
print(user_info.age)