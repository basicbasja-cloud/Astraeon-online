# Coherent tall Archer source studies

Eight raw sheets: male/female × SW/NW/NE/SE, sixteen cells in row-major order.
Each request uses its actual original-human camera guide and matching-direction
identity reference. The earlier tall Swordsman controls style/proportions.
Whole-sheet generation does not certify exact tracing, and these files are not
runtime-admitted art.

`extraction-recipe.json` records one common viewport for all sheets. Reproduce
the complete-body review using a fresh output directory:

```bash
python tools/character_factory_v3/build_tall_archer_review.py --source authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-tall-source-reset-20261026 --output /tmp/tall-archer-review
```

The retained SE process is `Master` → `CleanMaster-v3` → `visible-cutouts-v7` →
pelvis registration → same-pose recovery correction. The cleaning and cutout
folders contain their exact source annotations and implementation snapshots.
BodyCostume is one complete body, not separate limb templates. Cutout labels
remain proposals pending detailed semantic boundary and hidden-surface review.

Latest registered output is under `review/archer-pelvis-registration-v2-20261026`;
latest recovery output under `review/archer-same-pose-recovery-v3-20261026`.
Run `register_annotated_ranged_study.py --help` and
`repair_same_pose_recovery.py --help` for the pinned input arguments. Both reject
existing output directories. Recovery also rejects different source body poses.

`male-ready-no-arrow-raw.png` and `female-ready-no-arrow-raw.png` are corrective
local paint sources, not replacement whole characters. Their matching requests
and local crop inputs are preserved. Only the annotated projectile corridor may
use these pixels; original body/head/legs remain protected outside that region.

Known blockers: release-arm foreshortening, intermediate placement/shape drift,
remaining white fringes and hair/hood/quiver/glove/weapon boundary mistakes.
No hairstyle/costume swap or complete playable Archer is approved by this study.
