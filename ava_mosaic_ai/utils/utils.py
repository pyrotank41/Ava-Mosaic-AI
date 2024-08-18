from ava_mosaic_ai.config.settings import LLMProvider


def get_llm_provider(name: str) -> LLMProvider:
    try:
        return LLMProvider(name)
    except ValueError as exc:
        raise AttributeError(
            f"LLMProvider has no attribute, '{name}' is not supported"
        ) from exc
