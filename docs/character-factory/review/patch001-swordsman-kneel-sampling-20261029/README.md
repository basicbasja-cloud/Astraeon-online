# Swordsman Pickup — source-frame sampling study, 2026-10-29

The previous native `Fixing_Kneeling` capture spent many of its 16 frames on a long repair hold, then rose quickly. This isolated study selects actual source frames `[0,5,10,15,20,25,30,35,125,130,135,140,145,150,155,156]` from the same Mesh2Motion action, mannequin, sword and SW camera. The canonical renderer and production configuration were not changed. No new pose or painted in-between was invented. The 35→125 skip is a deliberate exploratory cut across the held section, not an assumed seamless transition.

[Side-by-side GIF](comparison.gif) uses the old uniform sampling on the left and this selected sampling on the right; 85 ms and the final pause are diagnostic, not the game's 0.65 s contract. Comparing maximum consecutive displacement among the recorded guide landmarks at 240px runtime scale, the largest step falls from 24.41 px to 16.55 px. The 35→125 cut itself is 9.53 px under that measurement. These are not foot-contact, sword-tip, acceleration or perceptual-smoothness proofs. Sword/hand intersections and right-hand grip remain unresolved; the low left wrist does not prove a pickup. **This does not pass as a playable pickup or finished artwork.**

The full isolated guide, job and manifest are retained at `authoring/characters/factory-v3/patch-0.0.1/research/swordsman-pickup-kneel-sampling-sw-20261029/`. The study wrapper uses the pinned canonical renderer with only its source-frame sampling statement replaced; it validates that samples are finite, increasing and within the source action range. Three unit tests passed, and Blender rendered the 16 guide frames. Reproduce with:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_kneel_pickup_sampling_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-pickup-kneel-sampling-sw-20261029/job.json --output <fresh-output-directory>
python3 -m unittest discover -s tests/character_factory_v3 -p test_kneel_sampling_study.py -v
```

The clip and 16-pose count require further timing and grip work before any paint or production binding. Nothing has been imported into the game.
