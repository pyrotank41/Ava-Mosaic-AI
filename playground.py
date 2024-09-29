import json
import uuid
import instructor
from openai import AzureOpenAI, OpenAI
from pydantic import BaseModel
from ava_mosaic_ai.config.settings import LLMProvider
from ava_mosaic_ai.llm_factory import LLMFactory
from dotenv import load_dotenv


# import httpx

# class CustomHTTPClient(httpx.Client):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.response_headers = {}

#     def send(self, request, *args, **kwargs):
#         print(request.headers)
#         # Generate a unique trace ID if not present
#         if "x-trace-id" not in request.headers:
#             raise ValueError("x-trace-id header is required")

#         response = super().send(request, *args, **kwargs)

#         # Store response headers with the trace ID as the key
#         self.response_headers[request.headers["x-trace-id"]] = response.headers

#         return response

#     def get_response_headers(self, trace_id):
#         return self.response_headers.get(trace_id)

# http_client = CustomHTTPClient()
client = LLMFactory(LLMProvider.PORTKEY_AZURE_OPENAI)
# client = LLMFactory(LLMProvider.AZURE_OPENAI)
# client = LLMFactory(LLMProvider.PORTKEY_ANTHROPIC)

class User(BaseModel):
    name: str
    age: int

trace_id = str(uuid.uuid4())
print(trace_id)

user_info = client.create_completion(
    # model="gpt-4o",
    max_tokens=1024,
    response_model=User,
    messages=[{"role": "user", "content": "John Doe is 30 years old."}],
    extra_headers={"x-trace-id": trace_id}
)
print(user_info)
print(client.get_trace_id(response=user_info))

print(json.dumps(client.get_audit_data(response=user_info), indent=4))
# print(client.http_client.response_headers)
