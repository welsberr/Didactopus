from didactopus.course_ingest import parse_markdown_course, extract_concept_candidates

SAMPLE = '''
# Sample Course

## Module 1
### Lesson A
- Objective: Explain Topic A.
- Exercise: Do task A.
Topic A body.

### Lesson B
- Objective: Explain Topic B.
Topic B body.
'''

def test_parse_markdown_course() -> None:
    course = parse_markdown_course(SAMPLE, "Sample Course")
    assert course.title == "Sample Course"
    assert len(course.modules) == 1
    assert len(course.modules[0].lessons) == 2

def test_extract_concepts() -> None:
    course = parse_markdown_course(SAMPLE, "Sample Course")
    concepts = extract_concept_candidates(course)
    assert len(concepts) >= 2


def test_extract_concepts_captures_distinctions_and_constraints() -> None:
    sample = """
# OCW Slice

## Broader Applications
### Thermodynamics and Entropy
- Objective: Explain how thermodynamic entropy relates to, and differs from, Shannon entropy.
- Exercise: Compare the two entropy notions and identify what is preserved across the analogy.
Entropy is a measure of uncertainty in the source model. The analogy is useful but dangerous when used loosely.

### Channel Capacity
- Objective: Explain channel capacity as a limit on reliable communication over a noisy channel.
- Exercise: State why reliable transmission above capacity is impossible in the long run.
"""
    course = parse_markdown_course(sample, "OCW Slice")
    concepts = {concept.id: concept for concept in extract_concept_candidates(course)}

    entropy = concepts["thermodynamics-and-entropy"]
    assert entropy.source_role == "nuance"
    assert entropy.distinctions
    assert entropy.definition_candidates
    assert entropy.qualification_candidates

    capacity = concepts["channel-capacity"]
    assert capacity.constraint_candidates
