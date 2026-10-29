# Swordsman Walk: source foot-skin sampling

Blender replayed the native `Walk` source at the 16 recorded guide frame times. Projected-independent world positions for the head and both foot bones matched the saved guide within 0.1 mm before the mesh was sampled. For each side and pose, the diagnostic records the lowest evaluated vertex with at least 0.5 weight in that foot or ball group. The [receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-source-feet-20261029/receipt.json) records selected vertex indices and world positions.

At frame 02, the right selected minimum is −7.5 mm relative to tentative world z=0; at frame 03 it is +59.7 mm. This supports treating the latter as a visibly lifted-foot candidate during review, but the lowest weighted vertex is not a verified sole, the measured point changes between poses, and ground contact cannot be determined by height alone. The native guide is in place with no recorded horizontal root displacement. Foot slip must be assessed with actual game velocity and identified contact phases rather than assuming a stationary world foot. Frames 01 and 09 also show selected minima approximately 16.5 mm and 15.6 mm below the tentative plane, requiring source mesh/contact review.

This is a source geometry measurement, not approval of the painted four-frame proposal, all eight directions, animation or runtime. [Partial painted/guide comparison](../swordsman-walk-sw-fourframe-candidate-20261029/partial-four-frames.gif) is a four-frame review only.

```sh
blender -b -t 2 --python tools/character_factory_v3/audit_swordsman_walk_source_feet.py -- --output /tmp/swordsman-walk-source-feet.json
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_walk_source_feet.py -v
```

Two scope checks passed. The GLB importer emitted duplicate F-Curve warnings for `Sword_Regular_C_RM`; this test does not validate that unused action. No production assets were modified.
