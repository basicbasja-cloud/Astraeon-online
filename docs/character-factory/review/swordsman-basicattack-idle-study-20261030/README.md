# Swordsman BasicAttack: retained samples and Idle transition study

**Source-guide experiment, not an approved animation or playable asset.** The existing tall Swordsman BasicAttack guide uses deliberately nonuniform source samples `[0,3,6,8,10,11,12,13,14,15,25,28,31,34,37,39]`; a standard uniform resample changes the strike and must not substitute for it. The isolated wrapper retains these 16 samples and appends four explicit joint-space poses transitioning from `Sword_Attack` frame 39 to `Idle_Sword` frame 0. The canonical renderer, production jobs, master art and long sword trail remain unchanged.

Across the four real diagonal views, the first 16 candidate poses match the retained guide's recorded source frames and world landmarks exactly, and recorded bone rotations within approximately 0.000003°. The final transition pose matches recorded Idle world landmarks within 0.000000211 m. These are selected rig data, not every mesh vertex or illustrated sprite. The largest projected sword-tip step in the four transition frames is 1.35 runtime px; natural motion and actual timing still require review.

For the SW capture, foot/ball-weighted lowest skin vertices in transition frames 16–19 range from −0.87 to −0.54 mm on the left and −0.13 to 0 mm on the right relative to tentative z=0. These are not verified painted soles or game-floor contacts, and other frames, directions and in-between motion need review. No assumption is made that negative minima establish or disprove a usable contact.

[Four-direction source review](normal.gif) · [slow review](slow.gif) · [strike pose](frame07.png) · [final Idle target](frame19.png). The GIF repeats a one-shot for inspection and uses illustrative timing. Four new transition poses require coherent painted masters and semantic cutouts, correct trail/event timing, actual game transitions and artist review. The existing 16-frame painted BasicAttack was not expanded or admitted.

[Job, source manifest and SW foot diagnostic](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-basicattack-idle-study-20261030/). Reproduce into fresh directories:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_swordsman_basicattack_idle_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-basicattack-idle-study-20261030/job.json --output /tmp/basicattack-idle20
python tools/character_factory_v3/review_swordsman_basicattack_idle_study.py --source /tmp/basicattack-idle20 --output /tmp/basicattack-idle20-review
blender -b -t 2 --python tools/character_factory_v3/render_swordsman_basicattack_idle_contact_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-basicattack-idle-study-20261030/contact-job-sw.json --output /tmp/basicattack-idle20-contact
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_basicattack_idle_study.py -v
```

Three focused sampling/scope tests passed. This study does not change production coverage: 2/96 technical imports and 0/6 complete characters.
