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
