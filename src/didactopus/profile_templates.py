from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ProfileTemplate:
    name: str
    required_dimensions: List[str]
    dimension_threshold_overrides: Dict[str, float]


def resolve_mastery_profile(concept_profile, templates, default_profile):
    if concept_profile is None:
        return default_profile

    template_name = concept_profile.get("template")
    if template_name:
        base = templates.get(template_name, default_profile)
        profile = {
            "required_dimensions": list(base.required_dimensions),
            "dimension_threshold_overrides": dict(base.dimension_threshold_overrides),
        }
    else:
        profile = default_profile.copy()

    if "required_dimensions" in concept_profile:
        profile["required_dimensions"] = concept_profile["required_dimensions"]

    if "dimension_threshold_overrides" in concept_profile:
        profile["dimension_threshold_overrides"].update(
            concept_profile["dimension_threshold_overrides"]
        )

    return profile
