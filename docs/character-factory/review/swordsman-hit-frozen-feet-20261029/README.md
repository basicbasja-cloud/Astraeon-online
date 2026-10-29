# Swordsman Hit: preliminary source foot geometry

For the isolated object-frozen native `Hit_Chest` study, Blender evaluated all 12 sampled source poses. For each foot, this diagnostic selects source mesh vertices with at least 0.5 weight in that foot's `foot` or `ball` vertex group, then records the lowest selected vertex in world Z. The original source and canonical assets were not modified. The [receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-frozen-feet-20261029/receipt.json) identifies every selected lowest vertex and position.

Relative to tentative `z=0`, left selected minima range from −1.76 to −1.31 mm; the lowest selected vertex remains index 320. Right selected minima range from −3.55 to +0.27 mm, with the lowest vertex changing at sample 10. These are **not verified floor contacts**: a weight-based selection and its lowest point can change with pose, a visible boot and game floor have not been compared, and between-sample movement has not been checked. The negative values require investigation rather than being treated as an automatic pass. Motion, grip, animation, art and actual gameplay remain unapproved.

Reproduce:

```sh
blender -b -t 2 --python tools/character_factory_v3/audit_swordsman_hit_frozen_feet.py -- --output /tmp/swordsman-hit-feet.json
python -m unittest discover -s tests/character_factory_v3 -p test_audit_swordsman_hit_frozen_feet.py -v
```

Two focused selection tests passed. The unchanged 768px [eight-view guide GIF](../swordsman-hit-object-freeze-20261029/eight-view-guide.gif) remains diagnostic; no runtime or final sprite was installed.
