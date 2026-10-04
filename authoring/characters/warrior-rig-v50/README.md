# Original Warrior rig study — not installed

**USER REJECTED: half-squat walk.** All eight native facings and the derived painted strips are now rejected pose studies. The low 1.03-unit pelvis kept the supporting knees bent. Passing ankle/contact tests did not establish a human gait. The upright replacement is `../warrior-rig-v51`; do not install or generate more production strips from v50.

`warrior-walk.blend` is an editable original full-body model derived from the controlled pose guide. It retains the Warrior's silver hair, gold cape, cream split tunic, green scarf, bronze armor and sword as identity cues. Its appearance is **too simple compared with the shipped illustration** and has not passed visual acceptance. Nothing here replaces game artwork.

`tools/author-warrior-gait-v50.py` runs against `authoring/characters/gait-rig-v50/walk-reference.blend`. It creates fixed-length thigh/shin and arm segments, 80 linearly sampled source keys plus a closure, and joined cape deformation. The eight `S-*.png` files are actual south-facing renders; `south-walk-study.png` assembles those renders at a common scale and origin.

`rig-validation.json` records actual evaluated ankle positions at every source key. The maximum ankle target error is about 2.98e-8 units; maximum stance travel after adding virtual root travel is about 7.31e-8 units. These checks establish this rig's sampled kinematics, not the quality of the shipped sprites or a production-ready running/sprinting animation. Only walking and one rendered facing are present in this study.

Do not align individual rendered frames by the lowest boot. Preserve the shared projected root coordinate and one body scale. Contact-foot retraction relative to the body is necessary to cancel forward travel. Remaining work includes final character modeling/art quality, all eight facings, separate running/sprinting and other starting archetypes, correctly registered runtime frames, and actual gameplay video inspection.
