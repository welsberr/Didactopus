# Course Repositories

Didactopus can ingest a checked-out course repository as a local source bundle.

## Recommended default

Use one repository per course-derived source set.

That keeps:

- license scope clear
- `sources.yaml` course-specific
- attribution and compliance artifacts isolated
- Git history focused on one source set
- removal or relicensing easier if a source needs to be withdrawn

## Recommended repository shape

```text
didactopus-mit-ocw-6-050j/
  didactopus-course.yaml
  course/
    course-home.md
    syllabus.md
    unit-sequence.md
  sources.yaml
  README.md
```

## Manifest file

The root manifest is `didactopus-course.yaml`.

Example:

```yaml
course_id: mit-ocw-information-entropy
display_name: MIT OCW Information and Entropy
source_dir: course
source_inventory: sources.yaml
license_family: CC BY-NC-SA 4.0
generated_pack_dir: ../../domain-packs/mit-ocw-information-entropy
generated_run_dir: ../../examples/ocw-information-entropy-run
generated_skill_dir: ../../skills/ocw-information-entropy-agent
```

## How Didactopus uses it

Didactopus treats the repo as a normal local source directory. The manifest only resolves which paths to use.

Run:

```bash
python -m didactopus.ocw_information_entropy_demo \
  --course-repo /path/to/didactopus-mit-ocw-6-050j
```

That command resolves:

- the source directory
- the source inventory
- the generated pack directory
- the generated run directory
- the generated skill directory

all relative to the checked-out repository.

If you want Didactopus to create the repository structure and copy the current source bundle into it, use:

```bash
python -m didactopus.ocw_information_entropy_demo \
  --course-repo-target /path/to/new-course-repo
```

That bootstraps:

- `didactopus-course.yaml`
- `course/`
- `sources.yaml`
- `generated/pack/`
- `generated/run/`
- `generated/skill/`

and then runs ingestion against that new course-repository directory.

## Multi-course repositories

Do not use a multi-course repository as the default pattern.

If you later need one, treat it only as a container of isolated per-course subtrees:

```text
ocw-collection/
  courses/
    course-a/
      didactopus-course.yaml
      course/
      sources.yaml
    course-b/
      didactopus-course.yaml
      course/
      sources.yaml
```

Each course should still keep its own:

- `didactopus-course.yaml`
- `sources.yaml`
- source tree
- generated attribution/compliance outputs

## MIT OCW example

The current in-repo reference example is:

- [didactopus-course.yaml](../examples/ocw-information-entropy/didactopus-course.yaml)
- [course](../examples/ocw-information-entropy/course)
- [sources.yaml](../examples/ocw-information-entropy/sources.yaml)
