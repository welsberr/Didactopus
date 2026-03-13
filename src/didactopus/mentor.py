from .model_provider import ModelProvider


def generate_socratic_prompt(provider: ModelProvider, concept: str) -> str:
    return provider.generate(
        f"You are a Socratic mentor. Ask one probing question about '{concept}'."
    ).text
