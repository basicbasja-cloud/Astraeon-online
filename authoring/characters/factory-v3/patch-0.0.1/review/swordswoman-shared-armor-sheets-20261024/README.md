# Shared covered-armor head variant — draft

64 poses, four real captured directions; 24 separate sprite sheets (six roles
per direction), 768px square authoring cells on 4×4 grids. See `variant.json`
for per-frame part paths, hashes and composition order. Original sword, glove
and front/back trails are reused unchanged. Body pixels are retained; existing
gold collar fragments change ownership from the old HeadHair mask to the body.

This is **not an admitted female base character or a complete patch package**.
Visible neck holes and some head-facing/occlusion mismatches remain. Frozen
2D slot proposals are unapproved. Native projected neck joints differ from the
earlier painted neck placement; the 2D pivot proposals use frozen head masks,
not per-frame body scaling or body fitting. Face-angle labels in the head
library are approximate artistic labels. The native axis convention is rest
world −Y forward, +Z up, not a facial-surface reconstruction certificate.

The independent-head attempt fails as a directly source-aligned pose strip.
Only explicit head-library attachment is demonstrated here. The later NW
full-master context study also changes some rear facings and is not promoted.

## Rebuild from the repository root

No image-generation call, SAM2 checkpoint or Blender is needed to rebuild the
frozen 2D variant. Python requires Pillow, numpy and scipy (the shared helpers).
Choose fresh output directories. Run:

```bash
python tools/character_factory_v3/review_rigid_head_library.py \
  --library authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-female-shared-armor-basicattack/head-angle-library-20261024/library.json \
  --slots authoring/characters/factory-v3/patch-0.0.1/research/retained-sword-sampling-20261024/native-head-slots.json \
  --art-slots authoring/characters/factory-v3/patch-0.0.1/research/retained-sword-sampling-20261024/proposed-art-head-slots.json \
  --source authoring/characters/factory-v3/patch-0.0.1/review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack \
  --output /tmp/my-head-variant
python tools/character_factory_v3/package_rigid_head_variant.py \
  --review /tmp/my-head-variant \
  --source authoring/characters/factory-v3/patch-0.0.1/review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack \
  --output /tmp/my-head-variant-sheets
```

The original male factory import and its unchanged imagery remain separate.
Technical replay/composition success does not imply visual acceptance.
