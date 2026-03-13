# Mastery Profile Templates

Domain packs can define reusable mastery profiles.

Example:

```
profile_templates:
  foundation_concept:
    required_dimensions:
      - correctness
      - explanation

  critique_concept:
    required_dimensions:
      - correctness
      - transfer
      - critique
```
Concepts can reference templates:

```
mastery_profile:
  template: critique_concept
```
Concepts may still override thresholds or required dimensions.
