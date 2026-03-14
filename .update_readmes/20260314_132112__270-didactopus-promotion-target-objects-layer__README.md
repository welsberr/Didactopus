# Didactopus Promotion Target Objects Layer

This layer extends the review workbench and synthesis scaffold by making promotion
targets concrete. Promotions no longer stop at metadata records; they now create
first-class downstream objects.

Added target object families:

- pack patch proposals
- curriculum drafts
- skill bundles

This scaffold includes:

- ORM models for concrete promotion targets
- repository helpers to create and list them
- promotion logic that materializes target objects
- API endpoints for browsing created target objects
- a UI prototype showing promoted outputs

This is the bridge between "interesting candidate" and "usable Didactopus asset."
