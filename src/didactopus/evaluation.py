from .model_provider import ModelProvider


def generate_rubric(provider: ModelProvider, concept: str) -> str:
    prompt = (
        f"Create a concise evaluation rubric for learner mastery of '{concept}'. "
        f"Assess explanation quality, problem solving, and transfer."
    )
    return provider.generate(prompt).text
