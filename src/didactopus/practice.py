from .model_provider import ModelProvider


def generate_practice_task(provider: ModelProvider, concept: str) -> str:
    return provider.generate(
        f"Generate one reasoning-heavy practice task for '{concept}'."
    ).text
