from typing import Any


def resolve_mastery_profile(
    concept_profile: dict[str, Any] | None,
    templates: dict[str, dict[str, Any]],
    default_thresholds: dict[str, float],
) -> dict[str, Any]:
    default_profile = {
        "required_dimensions": list(default_thresholds.keys()),
        "dimension_threshold_overrides": {},
    }
    if not concept_profile:
        effective = dict(default_profile)
    else:
        template_name = concept_profile.get("template")
        if template_name and template_name in templates:
            tmpl = templates[template_name]
            effective = {
                "required_dimensions": list(tmpl.get("required_dimensions", default_profile["required_dimensions"])),
                "dimension_threshold_overrides": dict(tmpl.get("dimension_threshold_overrides", {})),
            }
        else:
            effective = dict(default_profile)

        if concept_profile.get("required_dimensions"):
            effective["required_dimensions"] = list(concept_profile["required_dimensions"])
        if concept_profile.get("dimension_threshold_overrides"):
            effective["dimension_threshold_overrides"].update(concept_profile["dimension_threshold_overrides"])

    thresholds = dict(default_thresholds)
    thresholds.update(effective["dimension_threshold_overrides"])
    return {
        "required_dimensions": effective["required_dimensions"],
        "dimension_threshold_overrides": dict(effective["dimension_threshold_overrides"]),
        "effective_thresholds": {dim: thresholds[dim] for dim in effective["required_dimensions"] if dim in thresholds},
    }
