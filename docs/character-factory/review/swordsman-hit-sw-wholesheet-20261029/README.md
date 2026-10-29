# Swordsman Hit SW: full-sheet paintover study

**Draft rejected for production; no cutouts or game asset.** This is a single generated 12-frame sheet following the corrected object-frozen `Hit_Chest` SW guide and the preserved tall Swordsman seed. It uses 12 actual source poses, not interpolated frames. The fixed source camera is orthographic; a single `[448,520,1088,1160]` square crop and uniform resize were used only to create the review grid. The same crop contains the rendered guide in all 12 frames.

An earlier attempt used a 640×680 crop resized to 384×384, stretching X relative to Y by 6.25%; both its guide and result are preserved as **rejected**. The square-crop result is also not approved. In the guide, frames 00 and 11 are pixel-identical source poses; in the drawing their head/facial orientation visibly differs. Foreground pixel differences also flag a change but cannot isolate anatomy, and one-shot gameplay must transition to actual idle rather than simply loop frame 11 to frame 00. Inspect [frame 00](frame00.png), [frame 11](frame11.png), [normal](normal.gif), and [slow](slow.gif). The GIF repeats a one-shot for inspection at provisional timing.

Sword grip and orientation, body landmarks, the foot contacts and scene scale still need explicit review. Seven directions are missing, as are clean alpha, same-frame layers, underpaint, variants and gameplay. The generated sheet provides roughly 362 source pixels per slot, not a 768px per-frame master; enlargement does not restore detail. The image generator did not expose its model or seed.

Reproduce the source guide and review into fresh outputs:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_swordsman_hit_frozen_study.py -- --job authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw-wholesheet-20261029/source-job.json --output /tmp/swordsman-hit-sw1536
python tools/character_factory_v3/review_swordsman_hit_sw_sheet.py guide --source /tmp/swordsman-hit-sw1536 --output /tmp/hit-sw-guide.png
python tools/character_factory_v3/review_swordsman_hit_sw_sheet.py review --output /tmp/hit-sw-review
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_hit_sw_sheet.py -v
```

A local guide contact replay matched byte-for-byte; three focused checks passed. Reproduction of the stochastic paint is not guaranteed. Source prompts, input/result sheets, and source job/manifest are retained in `authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-hit-sw-wholesheet-20261029/`. No canonical or runtime assets were changed. Coverage remains 2/96 technical imports and 0/6 complete characters.
