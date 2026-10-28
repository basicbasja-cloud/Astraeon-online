# Cutout import preservation — 2026-10-28

The cutout importer previously reused an existing output directory, potentially overwriting earlier bindings and derived material. It now rejects an existing destination, including a dangling symlink, and creates a fresh directory exclusively after validating the source guide and manifest. This protects existing job output; it does not provide an atomic transaction. A failed new import can still leave a partial new directory or orphaned content-addressed objects, which require inspection before retrying.

Validation performed:

- Three focused preservation cases cover an existing output with sentinel files, a dangling symlink, and an invalid guide without a newly created folder.
- The complete `tests/character_factory_v3` unittest suite passed 396 tests, including Blender integration.
- An isolated replay of the retained Swordsman source using its **existing retained guide** reconstructed 64 poses, 384 part bindings, and 269 distinct objects with identical asset IDs, metadata, and bindings; baseline inputs remained unchanged. This is a reproduction check, not a new guide capture or visual approval.

No new artwork or character package is accepted by this checkpoint. The prior status remains 2/96 technical imports and 0/6 complete characters; visual stability, semantic cutouts, variants, and gameplay still require the plan's gates.
