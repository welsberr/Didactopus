# FAQ

## Why add a draft-pack import feature?

Because the transition from generated draft pack to curated workspace is one of the
places where users can lose momentum.

## How does this relate to the activation-energy goal?

Even when online course contents can be ingested, people may still stall if the next
steps are awkward. Importing a draft pack into a workspace should feel like one
smooth continuation, not a separate manual task.

## What does import do?

In this scaffold it:
- creates or updates a workspace
- copies a source draft-pack directory into that workspace
- makes it ready to open in the review UI

## Is the import workflow validated?

Only lightly in this scaffold. A future revision should add stronger schema checks,
collision handling, and overwrite safeguards.
