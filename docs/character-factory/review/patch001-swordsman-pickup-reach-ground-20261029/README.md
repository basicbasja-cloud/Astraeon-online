# Swordsman Pickup — bounded 3D reach and ground review

This is an **isolated motion proposal**, not a finished action. Starting with the 16 actual `Fixing_Kneeling` source samples, the study applies a phased 15° local spine bend, a phased Y +30° right-upper-arm adjustment, the native sword-idle finger pose, and a left two-bone arm IK target (3 cm lower and 10 cm inward) with a −30° left-wrist local rotation. The elbow keeps the source bend side and the solver clamps unreachable targets; source bones, rig file, production ledger and runtime assets remain untouched. No limbs are assembled from separate images.

[Eight-direction GIF](eight-directions.gif) shows 128 actual rendered guide view-frames with a constant crop. It repeats at diagnostic 85 ms per frame plus a final pause; this is not the gameplay timing. [Arm alternatives](arm-comparison.png) show the rejected X/Z candidates alongside Y. The [job](job.json), [manifest](manifest.json) and [geometry records](geometry.json) are included.

## Findings

- Lowest sampled left distal-finger bone tail is **1.53 cm above z=0**, versus 22.67 cm in the unadjusted reach study. A bone endpoint is not the visible fingertip surface, an item target or evidence of grasp. Maximum left IK reach clamp for the chosen samples is **0 m**.
- On the 128 view-frames the torso positive control hit in every frame. The thin blade centerline showed zero evaluated mannequin surface hits, and the lowest sampled blade proxy including its 2.2 cm radius was 11.95 cm above z=0. This does not certify blade volume, hilt, between-frame sweep or final clothing clearance.
- **Ground contact fails**: the lowest evaluated mannequin mesh vertex is 3.61 cm below z=0 at frame 4. That vertex is weighted 0.74 to `calf_r` and 0.26 to `thigh_r`; other frames have low right-foot/toe vertices. This identifies likely right knee/leg and foot regions, not a complete sole/contact audit. Correct the rig in 3D and recheck both legs and the finger target; do not translate whole painted frames to conceal this.
- The 35→125 source-frame cut, elbow bend, wrist, finger grip, prop contact, actual game event/timing, recovery and camera-specific occlusion remain unapproved. This is not a ready-to-paint master or an action accepted into the game.

The wrapper source SHA-256 is `f6c56e7e27b6176b065f6123aa182678cd177b4a638bc28ac964f3febdfeede5`; the reach helper is `370612416b3f42d3033cdca75705cd8ff415fdcda69a43ddecf7f168be0b832b`. Seven focused tests passed on the current code. A full 409-test factory suite also passed before the final addition of mesh-vertex weight instrumentation; it is not a substitute for visual approval. Reproduce with the pinned source and a fresh output:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_kneel_arm_grip_study.py -- --job docs/character-factory/review/patch001-swordsman-pickup-reach-ground-20261029/job.json --output <fresh-output-directory>
python3 -m unittest discover -s tests/character_factory_v3 -p 'test_kneel*study.py' -v
```

The underlying 19-action Swordsman remains incomplete.
