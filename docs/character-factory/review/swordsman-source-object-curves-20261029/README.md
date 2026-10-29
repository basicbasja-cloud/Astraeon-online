# Swordsman source armature object-channel audit

The configured Swordsman actions reference 19 distinct Mesh2Motion actions. In the imported `Armature` actions, all 19 were found. `Hit_Chest` alone has keyed object-level transform channels: three location curves, with keyed values approximately `(0.26517, 0.16, 0.575876)` across the action's frame range. The other 18 actions have no object-level location, rotation or scale curves in the imported actions. These results do not certify their rendered poses or paint quality.

This does not establish whether source object motion should be removed from other sources. Key values alone do not constrain interpolation; parent transforms, skin, contact, actual rendering and weapon attachment also require inspection. The source importer emitted duplicate F-Curve warnings for `Sword_Regular_C_RM`; this audit does not validate or repair that unused action.

[Receipt with source, configuration and script hashes](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-source-object-curves-20261029/receipt.json). This audit supports the isolated [Hit guide study](../swordsman-hit-object-freeze-20261029/README.md); it does not change the canonical guide or runtime.

Reproduce:

```sh
blender -b -t 2 --python tools/character_factory_v3/audit_swordsman_source_object_curves.py -- --output /tmp/swordsman-source-object-curves.json
python -m unittest discover -s tests/character_factory_v3 -p test_audit_swordsman_source_object_curves.py -v
```

Two focused tests passed. No artwork, animation or completed character was added.
