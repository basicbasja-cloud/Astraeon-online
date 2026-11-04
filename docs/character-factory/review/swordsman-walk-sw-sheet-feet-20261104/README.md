# Swordsman Walk SW — source foot skin overlay

The latest 16-frame sheet is compared at one fixed crop and shared scale to previously exported, camera-projected source foot skin vertices. [Full overlay GIF](overlay-slow.gif) · [frame 00](frame00.png) · [03](frame03.png) · [08](frame08.png) · [15](frame15.png). The same colored source points are drawn in both panels, cyan for source left and orange for source right. In frame 03 the raised rear boot is visibly displaced from the projected orange point. Frame 08 also shows an offset between the cyan source point and the painted raised leg. These are useful places to investigate and correct.

The selected source vertex may change between poses and is not a verified sole or a corresponding painted landmark. Body design also differs from the mannequin. Therefore these overlays are not a contact measurement or proof of size, anatomical, temporal or runtime correctness; no 1-runtime-pixel pass is claimed. The sheet remains a rejected draft and no production coverage is added.

Rebuild from the saved sources, choosing a fresh output directory:

```sh
python tools/character_factory_v3/review_walk_sheet_foot_projection.py \
  --source authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-seam-repair-20261104 \
  --output /tmp/walk-sheet-foot-projection
```

The program checks the guide-manifest hash against the retained Blender projection receipt and records all input hashes; it does not register or resize individual frames. Review GIF timing is diagnostic only.
