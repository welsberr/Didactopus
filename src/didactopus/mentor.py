from .model_provider import ModelProvider


def generate_socratic_prompt(provider: ModelProvider, concept: str, weak_dimensions: list[str] | None = None) -> str:
    weak_text = ""
    if weak_dimensions:
        weak_text = f" Focus especially on weak dimensions: {', '.join(weak_dimensions)}."
    return provider.generate(
        f"You are a Socratic mentor. Ask one probing question about '{concept}'.{weak_text}"
    ).text
