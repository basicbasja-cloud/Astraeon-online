# Swordsman V3 separate art concept pilot

**Status:** `SEPARATE_CONCEPT_ART_OWNER_REVIEW_PENDING`

The raw folder contains six distinct transparent PNG concepts: hair, base body,
outfit, golden cloak, sword, and sword-trail effect. The contact sheet in
`review/layer-concepts-v1.png` is only a labeled preview; it is not a character
composite and is not used as runtime art.

These drawings were made from the owner's current high-detail visual direction.
They are original concepts and do not copy Ragnarok sprites. Prompt text and
SHA-256 hashes are retained beside the files.

## Current limits

- The images are separate files, but their canvases and camera views differ.
- The BaseBody concept includes an under-tunic, trousers, and boots that overlap
  the outfit concept. They need a coordinated repaint before compositing.
- This concept-pilot folder itself contains no registered animation sheets. A
  separate review-only sheet set now exists under
  `../imagegen-swordsman-layered-v2/` for Idle and Walk, using five separate
  layers. Those images remain unapproved and are below the continuity warning
  threshold; BasicAttack and its separate CosmeticFX trail are pending.
- The concepts are not registered to the shared 160x160 cell, 112px target
  height, `(80,132)` root, or V3 motion frames.
- They are not a runtime package and have not passed a character preview.

Do not use these files as proof that the current painted-v2 candidate is
modular. The owner has directed a full-character-master-then-cutout workflow:
paint each exact motion frame as a whole, label its visible parts, and extract
those parts from that same frame with
`tools/character_factory_v3/cutout_master_sheet.py`. This keeps camera, pose,
root, and frame registration identical across layers. The separate-sheet
experiment in `imagegen-swordsman-layered-v2` was superseded after visual review.
