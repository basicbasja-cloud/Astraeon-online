# Swordsman Hit: thin sword-guide clearance

On the isolated object-frozen `Hit_Chest` rig, Blender sampled the same 12 source poses. For each, a ray representing the sword proxy's centerline was tested against the evaluated mannequin surface, from 0.12m to 0.8m beyond the finger-midpoint grip. No sampled centerline surface hits occurred; a separate ray through the torso hit the mesh in all 12 samples as a positive control. The test follows the renderer's sword-axis convention.

This does **not** establish collision clearance: the test excludes blade thickness, hilt/guard, the swept volume between samples, clothing, hair, underlayers and trail. It does not prove a closed grip or natural motion. [Per-frame receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-blade-clearance-20261029/receipt.json). [Eight-view guide GIF](../swordsman-hit-object-freeze-20261029/eight-view-guide.gif) is a source study, not finished art.

Reproduce:

```sh
blender -b -t 2 --python tools/character_factory_v3/audit_swordsman_hit_blade_clearance.py -- --output /tmp/swordsman-hit-blade-clearance.json
python -m unittest discover -s tests/character_factory_v3 -p test_audit_swordsman_hit_blade_clearance.py -v
```

Two focused scope checks passed. No source asset or runtime was modified, and no action is marked complete.
