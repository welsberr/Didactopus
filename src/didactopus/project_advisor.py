from .model_provider import ModelProvider
from .role_prompts import project_advisor_system_prompt


def suggest_capstone(provider: ModelProvider, domain: str) -> str:
    return provider.generate(
        f"Suggest one realistic capstone project for mastery in {domain}.",
        role="project_advisor",
        system_prompt=project_advisor_system_prompt(),
    ).text
