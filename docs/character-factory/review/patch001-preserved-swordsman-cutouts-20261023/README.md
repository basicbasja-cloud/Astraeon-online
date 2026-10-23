# Earlier Swordsman retained: camera and cutout review

The owner stated on 23 October 2026 that the earlier Swordsman was already okay.
The earlier illustrated BasicAttack and SkillOverhead remain the visual baseline.
Original art is preserved; it is not replaced by the current Archer experiments.

## Actual changes and evidence

- Hash-pinned 896 original master/part/FX files; all remain unchanged.
- Edge cleanup is bounded to the outer two-pixel band. 96,002 pixels across 128
  poses receive estimated white-spill recovery; protected interiors are unchanged.
- The original actions used different camera scales and root positions. Their
  camera orientations match the target. One isotropic scale per action maps both
  to the canonical 768px canvas/root `[384,550.4]`. Only recorded source root travel
  is extracted; no painted figure bounds or anatomy deformation.
- Body/head/weapon/hand cutouts compose exactly. A bounded blade-outline ownership
  proposal removes missed outline pixels from the body while protecting the
  grip/head. It changes labels, never the complete-master drawing.
- Original independent front/back trails retain their timing and share the
  character's camera/root transform.
- Actual `modular-sprites.js` draw checks all 128 poses twice: base-only and with
  trail. All 256 comparisons have zero changed pixels; page errors are empty.
- Atlas packing reduces 768 bindings to 530 distinct pixel objects. Each binding
  retains its pose and placement; shared bytes do not grant pose compatibility.
- `part-sheets/` contains 48 separate 3072px editor sheets: six roles per view,
  four views per action, two actions. All 768 full-canvas cells match their source
  RGBA images exactly. `part-sheets/manifest.json` records source poses and hashes.

## Reproduce

Run from the repository root, using fresh output directories:

1. `review_preserved_swordsman.py --output <edge-review>`
2. `register_preserved_swordsman.py --cleaned <edge-review> --output <camera-review>`
3. `package_preserved_swordsman_review.py --source <camera-review> --output <atlas-review>`

Scripts are under `tools/character_factory_v3/`. Serve the repository on
localhost:8011 and run this folder's `capture.py` to reproduce browser evidence.
`samples.json` retains source paths and hashes, atlas rects and offsets.

## Remaining limits

This is two male Swordsman actions, four actual views each, not all actions or
a completed character. Old source sampling differs from current patch guide jobs
and is explicitly retained. These assets are not silently imported under those
jobs. Head/collar/hilt boundaries, hidden surfaces, wardrobe swaps, skill entry/
exit motion and NE blade foreshortening still need review. Zero root mapping
error is a coordinate result, not independent art-motion approval. The six-
character patch remains incomplete.
