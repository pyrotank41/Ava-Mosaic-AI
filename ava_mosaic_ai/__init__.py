from ava_mosaic_ai.llm_factory import LLMFactory


def get_llm(provider: str) -> LLMFactory:
    return LLMFactory(provider)