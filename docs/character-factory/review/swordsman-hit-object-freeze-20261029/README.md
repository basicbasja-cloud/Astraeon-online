# Swordsman Hit: armature object transform study

**Experimental 3D guide, not painted art or an approved game action.** In historical guide `97bca857f2dea9909fa2`, the visible mannequin appears offset above its sword: [SW frame 05 comparison](sw-frame05-before-after.png). Blender inspection found `Hit_Chest_Armature` has object-level location curves constant at approximately `(0.26517, 0.16, 0.575876)` for source frames 0–10. In the existing renderer, the projected grip is calculated after setting the rig matrix, but Blender reevaluates the armature object's animation during rendering. The mesh consequently appears displaced relative to the world-space sword proxy and recorded landmarks.

An isolated wrapper leaves the shared renderer unchanged and, **only for an explicit native Hit_Chest study**, mutes the object location/rotation/scale curves and places the unparented source armature at the origin. Bone animation remains enabled. The regenerated 768px diagnostic comprises 12 source-sampled frames in each of eight actual directions. The sword proxy returns to the area of the hand in the visual review. [SW before/after GIF](sw-before-after.gif) · [eight-view guide GIF](eight-view-guide.gif). These GIFs repeat a one-shot for inspection and do not prove a transition to idle.

The projected distance from the hand bone origin to the finger-midpoint grip ranges from 2.0 to 16.13 authoring pixels; that is not a closed-grip or contact measurement. Body contact, natural response, prop axis, limb intersections, foot placement and all gameplay transitions require review. Suppressing object curves is a source-specific experiment and may discard meaningful object motion in other clips; it is not a generic root-motion fix. Historical guide and baselines remain untouched.

A separate repeat of the SW capture reproduced frame 05's decoded RGBA exactly, although the Blender PNG byte hashes differed. The [job and manifest](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-object-freeze-20261029/) record source and implementation hashes. The 96 Blender PNGs are regenerated into a fresh directory; the review GIFs are retained here. The production source-guide target remains 1536px, so this 768px diagnostic is not final authoring output.

```sh
blender -b -t 2 --python tools/character_factory_v3/render_swordsman_hit_frozen_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-object-freeze-20261029/job.json --output /tmp/swordsman-hit-frozen
python tools/character_factory_v3/review_swordsman_hit_frozen_study.py --source /tmp/swordsman-hit-frozen --output /tmp/swordsman-hit-review
python -m unittest discover -s tests/character_factory_v3 -p test_render_swordsman_hit_frozen_study.py -v
```

Two focused wrapper tests passed. No painted or runtime asset was admitted; overall status remains 2/96 technical imports, 0/6 completed characters.
