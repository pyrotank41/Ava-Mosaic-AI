import uuid
from pydantic import BaseModel
from ava_mosaic_ai.config.settings import LLMProvider
from ava_mosaic_ai.llm_factory import LLMFactory

# creating metadata for portkey client. This is optional
metadata = {"_user": "karan@test.dev",
            "environment": "development",
            "session_id": str(uuid.uuid4())}

client = LLMFactory(LLMProvider.PORTKEY_AZURE_OPENAI, metadata=metadata)
# client = LLMFactory(LLMProvider.AZURE_OPENAI)
# client = LLMFactory(LLMProvider.PORTKEY_ANTHROPIC, metadata=metadata)

class User(BaseModel):
    name: str
    age: int

# client = instructor.from_openai(portkey)
user_info = client.create_completion(
    # model="gpt-4o",
    max_tokens=1024,
    response_model=User,
    messages=[{"role": "user", "content": "John Doe is 30 years old."}],
    metadata=metadata,
)

print(user_info.name)
print(user_info.age)
