from typing import Optional
from ava_mosaic_ai.llm_factory import LLMFactory


def get_llm(provider: str, metadata:Optional[dict]=None) -> LLMFactory:
    return LLMFactory(provider, metadata=metadata)