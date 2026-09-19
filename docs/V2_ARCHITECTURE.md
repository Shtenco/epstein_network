# V2 architecture

V2 uses a three-layer model.

1. Upstream clone layer: every canonical source is cloned into a temporary local `vendor/` tree.
2. Repository snapshot layer: graph-relevant files are copied to `vendor_snapshot/<source_id>/`. Huge binary scans are excluded from Git history, but their path, size and SHA-256 are recorded in `vendor_manifest.json`.
3. Master graph layer: the distiller reads the local snapshots, normalizes contact identifiers, records provenance and emits a graph plus entity-resolution mappings.

This design keeps the project reproducible without duplicating multi-gigabyte image/PDF archives into ordinary Git history.

## Entity resolution

Deterministic exact normalization runs automatically. High-confidence token-order variants can be merged automatically. Fuzzy person matches are emitted to `entity_review.csv` for review rather than silently merged.

## Current-source contacts

Archived addresses are facts about the historical source. They are not automatically treated as active/current addresses. Current public professional contacts, if later added, should be stored as separate observations with their own source and observation date.
