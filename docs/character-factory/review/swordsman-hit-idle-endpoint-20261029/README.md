# Swordsman Hit-to-Idle: recorded rig endpoint comparison

The final pose of the eight-view floor-IK Hit-to-Idle study is compared with frame 0 of the retained native `Idle_Sword` guide. The maximum difference among recorded world-space landmarks is 0.000000211 m; maximum projected landmark and sword guide endpoint difference after resolution normalization is 0.000112 authoring pixels; maximum recorded bone quaternion angle difference is 0.000024°. All eight views use the same motion-source hash. These tiny floating-point differences support that the **recorded selected rig landmarks and prop endpoints** match the intended Idle guide.

This does not compare every rig joint or mesh vertex and does not establish the actual game uses that Idle, that the illustrated Idle matches, that feet contact terrain, or that the transition looks natural. The intermediate [IK guide GIF](../swordsman-hit-floor-ik-20261029/eight-views.gif) remains a diagnostic study, with grip, timing, image work and runtime unapproved.

[Per-view receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-idle-endpoint-20261029/receipt.json). Reproduce:

```sh
python tools/character_factory_v3/audit_swordsman_hit_idle_endpoint.py --output /tmp/swordsman-hit-idle-endpoint.json
python -m unittest discover -s tests/character_factory_v3 -p test_swordsman_hit_idle_endpoint.py -v
```

Two focused tests passed. No production data was altered or admitted; 2/96 technical imports and 0/6 complete characters remain.
