# Swordsman kneeling Pickup — isolated arm and hand study

This is a **candidate guide**, not approved art, a completed action, or a production motion binding. It builds on the native Mesh2Motion `Fixing_Kneeling` 16-pose sampling study. Six bounded right-upper-arm rotations (±30° on X, Y, Z) were rendered in SW; [arm comparisons](arm-variants.png) show frames 6 and 8. An X −30° proposal places the projected sword line farther from the free left hand in this view. It then copies only the 15 native right-finger local poses from frame 0 of `Idle_Sword`; it does not copy a torso, arm, wrist or leg from another frame. [Finger comparison](finger-compare.png).

The arm correction ramps from zero at source frame 0 to its selected angle by frame 30, then back to zero by frame 156. All base joint motion remains sampled from `Fixing_Kneeling`; the 35→125 hold cut from the previous study remains. Blender's render dependency graph is frozen at each evaluated pose to keep the study arm/finger change visible. The chosen proposal was rendered in all eight real directions: [eight-direction GIF](eight-directions.gif). It uses the same fixed crop and diagnostic 85 ms/frame plus a final pause; this is not a gameplay timing contract.

## Checks and limits

- On SW frames 3–11, the minimum **2D projected** distance from the left-hand bone origin to the sword grip→tip segment changed from 2.39 to 10.99 runtime pixels in the open-finger study. This is a view-specific screening metric, not mesh clearance or proof of hand-object contact.
- In SW, root, head, pelvis, left hand and both foot world landmarks match the unadjusted selected samples; right-hand position changes by up to 0.283 m. Across the eight views, the recorded world landmarks match each other exactly. This does not certify foot contact or every bone.
- A separate SW capture and the SW frames within the eight-view capture matched in all 16 decoded RGBA images. PNG file hashes differed, so byte-level reproduction is not claimed. No crop clipped nontransparent pixels in this capture.
- Five focused sampling/parameter tests passed. The wrapper and Blender rendered all 128 view-frames; the [job](job.json) and [manifest](manifest.json) are retained. The preview uses generated mannequin guides, not painted sprites.
- The blade can still intersect the leg or floor in 3D; the free hand's reach and actual finger contact, wrist anatomy, arm pose, temporal smoothness, shortened hold, one-shot recovery and game timing remain unverified. The copied finger pose is a hypothesis, not evidence the sword is correctly gripped. All eight views need visual and geometry review.

Reproduce from repository root with Blender and a fresh output directory:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_kneel_arm_grip_study.py -- --job docs/character-factory/review/patch001-swordsman-kneel-arm-grip-20261029/job.json --output <fresh-output-directory>
python3 -m unittest discover -s tests/character_factory_v3 -p 'test_kneel*study.py' -v
```

Wrapper SHA-256: `523c76e57414d688425d500ef52f2ad7ad5526e1f49ff2861950daa01390ac6e`. Canonical renderer SHA-256: `618d7728b3304572d0211644ca21d8a94092e784d48432db324abb2d6a5e1e19`. No source rig, original baseline, production ledger or runtime asset was modified. This study does not satisfy the request for all playable Swordsman actions.
