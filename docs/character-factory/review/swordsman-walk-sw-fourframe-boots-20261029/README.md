# Swordsman Walk SW: four-frame boot repaint comparison

**Unapproved partial study, not a complete walk.** Frames 00–01 reuse the prior full-body registered candidates; frames 02–03 use their separate bounded boot repaint proposals. Each correction receipt is checked against the exact earlier master hash. These images are complete 887px review cells with one shared placement per frame; this review applies no additional translation, pose-wise scaling, or separately animated limbs.

The [four-frame comparison](partial-four-frames.gif) overlays selected source foot-skin points (orange right, cyan left) on both the guide and the candidate. The updated raised boot in frames [02](frame02.png) and [03](frame03.png) visually approaches the selected source point. It does **not** establish contact: the selected source vertex may change, brown footwear and bare mesh are different, and the ground/actual painted sole has not been verified. Review motion, knee/boot shape, mask seams, head/body stability, foot size, timing and gameplay before accepting any master.

This GIF repeats only four frames, not the required 16-frame Walk loop. Twelve frames, seven directions, clean alpha, same-frame cutouts, variants and runtime are missing. Repaint donors, masks, original masters and provenance remain in their respective review/painted-candidates folders; generator models/seeds were not exposed.

```sh
python tools/character_factory_v3/review_swordsman_walk_fourframe_boots.py --output /tmp/swordsman-walk-fourframe-boots
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_fourframe_boots.py -v
```

Two source-binding/review tests passed. No canonical or runtime data changed; 2/96 technical imports and 0/6 complete characters remain.
