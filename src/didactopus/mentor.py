from .model_provider import ModelProvider


def generate_socratic_prompt(provider: ModelProvider, concept: str) -> str:
    prompt = (
        f"You are a Socratic mentor. Ask one probing question that tests whether a learner "
        f"truly understands the concept '{concept}' and can explain it in their own words."
    )
    return provider.generate(prompt).text
