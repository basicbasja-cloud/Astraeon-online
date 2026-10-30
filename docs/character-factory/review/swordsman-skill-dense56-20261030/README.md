# Swordsman SkillAction: 32 vs 56 source-pose samples

**Source study only; not an approved animation.** The existing 32-frame guide uses `Sword_Regular_B` and `Sword_Regular_B_Rec` with four entry and four exit joint-space samples. This separate four-direction capture samples the same source ranges more densely: 56 frames with eight entry, 40 native-action and eight exit poses. The additional frames are evaluated rig poses, not repeated sprites. The canonical guide/config is unchanged.

[32-sample guide](baseline-32.gif) · [56-sample guide](dense-56.gif) · [dense frame 24](dense-frame24.png). Previews use illustrative 70ms and 40ms per frame respectively and repeat one-shots; those timings are not the game timing contract. At SW, the largest adjacent projected sword-tip change is approximately 76.07 runtime px in the 32-sample guide and 47.51 px in the dense guide. The other directions change from 73.51–74.45 px to 44.56–46.14 px. Different samples and timing mean these values do **not** establish the same velocity, a natural strike, a correct wrist or smooth gameplay. The large dense steps and wrist/prop axis need close examination.

There is no painted 56-frame master, approved trail, full-body cutout, variant, or runtime package. Source pose, sword grip, blade volume, contact, effect direction and actual game timing remain open. [Job and source manifest](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-skill-dense56-20261030/).

```sh
blender -b -t 2 --python tools/character_factory_v3/render_patch001_guides.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-skill-dense56-20261030/job.json --output /tmp/swordsman-skill-dense56
python tools/character_factory_v3/review_swordsman_skill_dense.py --dense /tmp/swordsman-skill-dense56 --output /tmp/swordsman-skill-dense56-review
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_skill_dense.py -v
```

Two focused review tests passed. Coverage is unchanged: 2/96 technical imports, 0/6 complete characters.
