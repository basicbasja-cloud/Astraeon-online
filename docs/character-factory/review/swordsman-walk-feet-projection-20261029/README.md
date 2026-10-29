# Swordsman Walk: projected source foot-skin points

The source foot-skin sampling receipt is projected back into the recorded SW orthographic camera. A validation projects the recorded world-space foot-bone origins and checks them against the saved guide positions within 0.001 source pixel, guarding against an incorrectly configured camera aspect. The projection retains the source-selected foot/ball-weighted vertex index for each frame; that index can change between poses and is not a proven anatomical sole.

The [partial overlay](partial-skin-points.gif) and [frame 02](frame02.png) show the selected right-foot source point below the drawn raised rear boot in the unapproved four-frame candidate. This is a pose discrepancy requiring investigation; it is not an exact painted-foot contact measurement. Frame 03's source right-foot point likewise lies away from the painted boot. The candidate has only four frames, no accepted alpha or cutouts, and no full-loop or gameplay approval.

Reproduce:

```sh
blender -b -t 2 --python tools/character_factory_v3/project_swordsman_walk_source_feet.py -- --output /tmp/walk-source-feet-projection.json
python tools/character_factory_v3/review_swordsman_walk_skin_projection.py --projection /tmp/walk-source-feet-projection.json --output /tmp/walk-skin-review
```

The [projection receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-feet-projection-20261029/receipt.json) retains source hashes and all 16 projected frames. This is not approval of game-floor contact or animation.
