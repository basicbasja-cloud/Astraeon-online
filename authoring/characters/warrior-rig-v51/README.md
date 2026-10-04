# Upright Warrior walk candidate v51

The user rejected v50 because its low pelvis made it look like a half-squat walk. This original editable rig raises the pelvis along the supporting-leg arc, adds heel/sole/toe contact roll, and keeps the limb lengths fixed. The supporting knee bends 18.93–28.06 degrees across the sampled keys instead of staying deeply flexed. The swing knee bends separately; shoulders and hips counter-rotate.

Run `tools/author-warrior-gait-v51.py` against the original `gait-rig-v50/walk-reference.blend`. The output has 80 source keys plus a closure. South and east views use one orthographic camera scale, common projected root and identical chronological keys. Mathematical contact checks are recorded in `rig-validation.json`; they do not establish visual acceptance or verify subsequently painted sprites.

`E-eight-pose-guide.png` and `upright-s-e-study.png` are assembled from actual native renders. The illustrated east candidate lives in `../warrior-painted-v51/E`. Its shared canvas transform preserves pose movement without individually anchoring boots.

**Not installed or approved.** Only two native facings and one painted facing are available. All eight facings, character-scale registration, separate run/sprint and other starting archetypes, source-to-painted foot motion, and actual gameplay loops remain to be verified. Do not describe the shipped character animation as fixed.
