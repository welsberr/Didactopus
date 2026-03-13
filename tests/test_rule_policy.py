from didactopus.course_ingest import parse_markdown_course, extract_concept_candidates
from didactopus.rule_policy import RuleContext, build_default_rules, run_rules

SAMPLE = '''
# Sample Course

## Module 1
### Lesson A
- Objective: Explain Topic A.
- Exercise: Do task A.
Topic A body.

### Lesson B
- Objective: Explain Topic B.
- Exercise: Do task B.
Topic B body.
'''

def test_rules_run() -> None:
    course = parse_markdown_course(SAMPLE, "Sample Course")
    concepts = extract_concept_candidates(course)
    ctx = RuleContext(course=course, concepts=concepts)
    run_rules(ctx, build_default_rules())
    assert len(ctx.concepts) >= 2
