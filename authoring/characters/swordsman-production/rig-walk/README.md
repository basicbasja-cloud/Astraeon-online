# Articulated authoring walk proof

Candidate 03 passes the internal authoring-rig gate at 38/40 after visual
inspection of all directions and browser playback. This is not owner approval
or a pass for the painted character. Candidate 02's earlier internal pass was
withdrawn: measured knee-to-hip paths showed both knees ahead of the hip through
the entire cycle. The owner's painted-bake feedback exposed that missing
fore/aft gate. Candidate 03 corrects rearward thigh extension and rear foot
lift, and adds a regression check that rejects the old cycle. Mechanical tests
alone still cannot accept the revised visual motion.

No skeleton is added to the game runtime. The owner has not approved painted
Swordsman art. Previous painted Walks remain rejected.

The supplied Ragnarok NPC Walking and Female Novice PNGs were inspected as
motion readability benchmarks only. Their pixels, proportions, individual
poses, layout and playback timing are not imported. Source checksums and the
comparison are recorded in provenance and `rig-quality-report.json`.

A genuine 3D articulated chain has fixed 0.49 m femurs, 0.47 m tibias and
0.28 m feet. Anatomical +Y is the forward knee pole, +X is right and +Z is up.
Heel, sole and toe points form one rigid foot around the ankle. The supporting
foot rolls about its contact pivot; adding virtual root travel cancels its
local stance displacement. The 60% stance fraction maintains double support. The footprint travels from
in front of the pelvis to behind it; swing begins with rearward thigh extension
before the knee passes forward.
The swing clears the floor by at most 65 mm. Loaded flat-foot knees flex about
6–16 degrees; the releasing rear knee folds as it unloads, rather than locking
both legs or creating a crouched stance. A small lateral pelvis shift follows
the supporting side. Arms counter the stride. This is an ordinary 1.12-second
walk cycle, chosen independently of the reference sheets.

Every direction uses the same physical cycle, a fixed orthographic 45-degree
camera, 320×320 canvas and (160,264) root. Direction order remains
S, SW, W, NW, N, NE, E, SE. Views are rendered individually, never mirrored.
Actual evaluated Blender joints and transformed heel/toe points are checked
against the fixed-length analytical chain. Mechanical tests cover dense cycle
samples, continuity, stable poles, clearance and world-space foot planting.

Open `candidate-03/preview.html` for direction, normal/quarter speed, frame
stepping and gameplay-size controls. It plays baked authoring PNGs. The
continuous-contact GIF is an offline diagnostic diagram of the same cycle.
The tracking floor moves by virtual actor travel; planted contacts move with
that floor. Browser evidence covers 64 distinct phases, both speeds, all views,
stepping, gameplay size and a mobile viewport.

Candidate 01 is retained as a compact lossless comparison with its editable
rig and exact cycle source. It was superseded because its heel roll began after
the sampled up phase. Candidate 02 started heel rise earlier but failed rearward thigh extension.
Candidate 03 changes the stance fore/aft trajectory and completes plantar
flexion at rear lift before preparing heel contact. There were no
image-generation calls during this rig work.

Reproduce current proof from repository root:

```sh
blender --background --factory-startup --python tools/build-swordsman-walk-rig.py -- --candidate candidate-03 --cycle-source authoring/characters/swordsman-production/rig-walk/candidate-03/cycle-source.py
python3 tools/review-swordsman-walk-rig.py --candidate candidate-03
python3 tests/swordsman_walk_motion.py
# With the repository served on port 8011:
python3 tests/swordsman_walk_rig_browser.py --candidate candidate-03
```

The immutable `cycle-source.py` and `shared-cycle.json` establish the pose
source for painted baking. Rebuilding a proof resets its visual status to
pending: mechanical checks do not automatically accept changed motion.
Painted conversion uses one documented leg-chain anthropometric scale and
keeps the original painted upper-body identity. It must pass its own modular
and visual gates; the neutral proxy is not a replacement character design.
