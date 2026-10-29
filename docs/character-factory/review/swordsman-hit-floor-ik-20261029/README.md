# Swordsman Hit-to-Idle: bounded 3D foot IK study

**Candidate source guide; not an approved animation or finished asset.** The prior joint-space Hit-to-Idle transition placed selected foot/ball-weighted mesh vertices up to 18.17 mm left and 23.39 mm right below tentative world `z=0`. This study applies a bounded two-bone 3D leg solve only during the seven intermediate transition poses, preserving knee bend side, ankle X/Y target and the foot's world orientation. It raises each selected ankle only enough to bring its selected lowest foot/ball vertex to the tentative floor, with a maximum allowed correction of 40 mm. The root, locked camera and 2D sprite transforms are not adjusted.

Across 56 intermediate corrections (seven frames × eight cameras), selected low points after correction were within approximately 0.001 mm below zero in the sampled poses; no reach clamp was required. These are floating-point results for selected mesh vertices, **not verified contact with a game floor**. Some negative minima still exist in unmodified source frames and the unmodified final Idle pose. Foot sliding, knee shape, authored animation intent, feet between samples, terrain, sword/grip, costume and final painted poses remain to be checked. The actual final idle frame is deliberately not corrected, to preserve the original target pose.

[SW before/after](sw-comparison.gif) · [eight-view candidate](eight-views.gif) · [SW frame 15](sw-frame15.png). GIF timing is illustrative and the repeated one-shot is a review display, not the gameplay transition. In the SW capture, all 12 non-transition images and the final idle image decode to identical RGBA before/after. An independently rendered SW-only run reproduced all 20 SW image pixels from the eight-view run. These checks do not certify the visual result or other directions.

[Job, source manifest and diagnostic](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-floor-ik-20261029/). To reproduce into fresh paths, first render the uncorrected baseline using the previously recorded `job-20.json`, then:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_swordsman_hit_floor_ik_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-floor-ik-20261029/job-eight.json --output /tmp/hit-floor-ik
python tools/character_factory_v3/review_swordsman_hit_floor_ik.py --baseline /tmp/hit-trim20 --candidate /tmp/hit-floor-ik --output /tmp/hit-floor-ik-review
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_hit_floor_ik.py -v
```

Two focused scope/endpoint tests passed. Baseline, production config, painted sprites and runtime bindings remain unchanged. Coverage remains 2/96 technical imports and 0/6 complete characters.
