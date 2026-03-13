from .model_provider import ModelProvider


def generate_practice_task(provider: ModelProvider, concept: str, weak_dimensions: list[str] | None = None) -> str:
    weak_text = ""
    if weak_dimensions:
        weak_text = f" Target the weak dimensions: {', '.join(weak_dimensions)}."
    return provider.generate(
        f"Generate one reasoning-heavy practice task for '{concept}'.{weak_text}"
    ).text
