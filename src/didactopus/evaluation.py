from .model_provider import ModelProvider


def generate_rubric(provider: ModelProvider, concept: str) -> str:
    return provider.generate(
        f"Create a concise evaluation rubric for mastery of '{concept}'."
    ).text
