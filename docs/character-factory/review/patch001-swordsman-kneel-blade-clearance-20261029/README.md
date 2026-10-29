# Swordsman kneeling Pickup — blade centerline diagnostic

Compared the same 16 native Mesh2Motion source poses in Blender with a sword-idle finger pose in both cases: (1) unadjusted right upper arm and (2) the bounded X −30° arm proposal. The evaluated mannequin's **surface mesh** was queried using a BVH. For every pose the tool raycasts the thin sword proxy centerline from 0.12 m to 0.8 m beyond the grip, excluding the grip/guard, and samples nearest-surface distance at 18 positions along that segment. A separate line through the torso is the positive control.

| Diagnostic | Unadjusted | Adjusted |
|---|---:|---:|
| Pose samples | 16 | 16 |
| Torso positive-control hits | 16 | 16 |
| Blade centerline surface hits | 1 (frame 7) | 0 |
| Lowest sampled distance to mannequin surface | 0.00524 m | 0.06764 m |

See [frame 7 comparison](frame07.png), [baseline records](baseline-clearance.json), [adjusted records](adjusted-clearance.json) and the [eight-direction motion preview](../patch001-swordsman-kneel-arm-grip-20261029/eight-directions.gif). The 16 SW images from the diagnostic render matched the earlier eight-view capture as decoded RGBA arrays. Five focused validation tests passed.

These results support choosing the adjusted arm for **continued study**. They are not full collision clearance: the probe is a line, nearest distance is sampled, the hilt is excluded, the floor and final painted costume are absent, and intersections between samples or inside geometry may be missed. Finger grip, wrist anatomy, left-hand pickup contact, timing and return to ready remain unapproved. The repeated GIF is a diagnostic and no production binding or art was changed.

The wrapper has an optional `study_blade_clearance` flag and freezes the evaluated pose during render. Source code SHA-256: `08bf2d485894e50e5fe8f2ba5d1ea1f677ec9ab9a933a65af2f824aed70514dc`; canonical renderer SHA-256: `618d7728b3304572d0211644ca21d8a94092e784d48432db324abb2d6a5e1e19`. Both saved jobs and generated reports are in this directory. Reproduce either using a fresh destination:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_kneel_arm_grip_study.py -- --job docs/character-factory/review/patch001-swordsman-kneel-blade-clearance-20261029/adjusted-job.json --output <fresh-output-directory>
python3 -m unittest discover -s tests/character_factory_v3 -p 'test_kneel*study.py' -v
```

No completed Swordsman action or playable character is implied by this study.
