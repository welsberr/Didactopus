# FAQ

## Why add import validation?

Because reducing startup friction does not mean hiding risk. A user still needs
a clear signal about whether a generated draft pack is structurally usable.

## How does this support the activation-energy goal?

It removes uncertainty from the handoff step. Users can see whether a draft pack
looks valid before committing it into a workspace.

## What does the preview check do?

In this scaffold it checks:
- required files
- basic YAML parsing
- key metadata presence
- concept count
- overwrite conditions

## Does preview guarantee correctness?

No. It is a safety and structure check, not a guarantee of pedagogical quality.

## Can import still overwrite an existing workspace?

Yes, but only if overwrite is explicitly allowed.
