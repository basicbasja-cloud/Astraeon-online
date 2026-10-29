# Swordsman Walk SW: adjacent-pair paint and registration study

**Unapproved four-frame research; not a walk loop or usable sprite package.** Two separate generation calls each painted two consecutive source poses, with the second call referencing the first pair. Both retain complete clothed bodies and their weapons. Each generated sheet is 1774×887, giving 887-pixel cells; this is more source detail per cell than the earlier 16-cell sheet but does not by itself meet the 768×768 authoring canvas contract or certify image quality. The source guides use the same square 696×696 crop from the locked 1536px guide for all four poses, not independent bounding-box fits. Generated model and seed were not exposed.

SAM2 mask 2 proposes a hair region for each frame. It excludes much of the face, so its centroid is **not** an anatomical head landmark. Relative to the projected source head-bone movement, the provisional hair centroid residual between frames 01→02 is approximately 2.54 runtime px, and between 02→03 approximately 4.25 runtime px. Mask differences, hair shape and source-bone offsets can contribute; these numbers flag a problem rather than establishing an exact head error. The [mask proposals](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-sw-pair-head-sam-20261029/proposals.png) show what was selected.

An exploratory registration translates each **complete frame** by one integer delta derived from that hair proxy, without per-part scaling or warping. A near-zero hair-proxy residual after this operation is expected by construction and does not validate the motion. In [frame 02](frame02.png) and [frame 03](frame03.png), the yellow right-foot bone-origin overlay remains outside or near the edge of the painted raised boot in both the original and proposal. A bone origin is not a sole contact, but this indicates anatomy/pose must be inspected and potentially repainted; a whole-frame shift cannot be accepted on hair alone. Magenta is source head, red source right-hand bone, yellow source right-foot bone and cyan source left-foot bone. [Partial four-frame review](partial-landmark-review.gif) repeats four frames for comparison and is **not** a complete walk animation.

The original sheet, prompt, raw results, SAM masks and translated proposals are retained under the corresponding `painted-candidates`, `research` and `review` directories. The seed artwork hash is `5d7efd1f7f04b47eb0bfc48ddb2c850d3efd5ca6ba5827872c402ab826795a0b`. Other 12 walk frames, seven directions, actual foot association, stable dimensions, clean alpha, same-frame cutouts, variants and runtime remain open.

Reproduce guide and downstream proposals with the saved inputs:

```sh
python tools/character_factory_v3/build_swordsman_walk_pair_guide.py --start 0 --output /tmp/walk-pair-guide.png
/workspace/.venvs/astraeon-cutouts/bin/python tools/character_factory_v3/propose_swordsman_walk_pair_heads.py --checkpoint /workspace/.tools/SAM2/sam2.1_hiera_tiny.pt --output /tmp/walk-pair-sam
python tools/character_factory_v3/propose_swordsman_walk_pair_registration.py --output /tmp/walk-pair-registration
python tools/character_factory_v3/review_swordsman_walk_pair_landmarks.py --registered /tmp/walk-pair-registration --output /tmp/walk-pair-landmarks
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_pair_registration.py -v
```

The first guide pair reproduced byte-for-byte; two helper tests passed. The SAM checkpoint and environment are local dependencies. No baseline or runtime was changed; 2/96 technical imports and 0/6 complete characters remain.
