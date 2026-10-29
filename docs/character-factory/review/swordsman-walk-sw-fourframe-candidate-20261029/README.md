# Swordsman Walk SW: four-frame combined candidate

**Unapproved partial research, not a complete walk.** This combines four saved complete-master drafts: original frames 00–01, the bounded raised-leg repaint for frame 02, and the follow-up repaint for frame 03. Each complete 887×887 cell receives the previously documented single whole-frame integer translation based on a SAM hair-centroid proxy. No limb is separately positioned by this assembly and no pose-wise rescaling is performed. The head region is checked byte-for-byte against the inputs used to derive the proxy before the transforms are applied.

The [four-frame comparison](partial-four-frames.gif) and frames [00](frame00.png), [01](frame01.png), [02](frame02.png), [03](frame03.png) overlay the source head, right-hand, right-foot and left-foot bone origins. The right-foot marker is closer to the raised painted boot in the repaired poses, but a projected bone origin is **not** a verified painted ankle or planted sole. Hair-centroid alignment is expected from the chosen translation, does not establish body stability, and could worsen other contacts. Inspect actual joint locations, mask seams, body scale, feet and sword motion across a full cycle before advancing the master to cutout.

The GIF repeats only four consecutive poses for review; it is not the 16-frame walk loop. Twelve poses, seven real directions, grounded contact, alpha extraction, full-body source detail, same-frame semantic parts, variants and gameplay remain open. All images are still white-background 887px review cells, not a 768px authoring package. Source, correction and registration receipts are retained in `authoring/characters/factory-v3/patch-0.0.1/review/`. Generator models/seeds were not exposed.

Reproduce from saved inputs:

```sh
python tools/character_factory_v3/review_swordsman_walk_fourframe_candidate.py --output /tmp/swordsman-walk-fourframe
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_fourframe_candidate.py -v
```

Two focused tests passed. No production or runtime asset changed; 2/96 technical imports and 0/6 complete characters remain.
