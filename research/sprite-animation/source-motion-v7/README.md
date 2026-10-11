# Actual external source rig: walk and sword attack

2026-10-11. Following the user's rejection of the original pose board as unnatural, this study **actually downloaded and imported** Quaternius' current free Universal Animation Library Standard, from the [author](https://quaternius.itch.io/universal-animation-library). CC0 is stated there and in the inspected bundled [license](License.txt) and [README](author-README.txt). It uses no rejected game-branch characters.

The selected [root-motion GLB](UAL1_Standard_RM.glb) has43clips and65bones including articulated fingers. Exact archive/GLB provenance and hashes are in [provenance.json](provenance.json). A pinned2025GitHub mirror was read as discovery only; this study used the current author download because the changelog describes later elbow/clock/directional corrections. No account/payment was used.

[Actual source joint data](source-motion.json) contains world coordinates, measured root travel and an explicit root-relative guide transformation:

| Clip | Source samples / duration | Complete inspected diagrams |
|---|---|---|
| Walk_Loop | 41 / 1.333333s | [Every source pose](Walk_Loop-all-source-samples.png), [eight-view overview](Walk_Loop-eight-views-overview.png) |
| Sword_Attack | 47 / 1.533333s | [Every source pose](Sword_Attack-all-source-samples.png), [eight-view overview](Sword_Attack-eight-views-overview.png) |

Samples use actual glTF input times, not presumed frame count/FPS. Blender FPS is set30**before import**; imported action range is checked against source seconds. All NLA tracks are muted, the chosen action is assigned explicitly, and evaluated bone heads are sampled. Last sample is an endpoint with no invented playback hold. A source-known occluded bone is not a visible-image observation.

[Geometric measurements](mechanics-measurements.json) report hip-height excursion, shoulder–hip yaw difference and knee/elbow angles. World root travels1.30units in the walk and1.5005in the attack. These are useful contrasting mechanics; they do not establish center of mass, correct sole contact, our gameplay speed or a new compact attack. The attack has a travelling step/lunge, which must be reposed if we remove travel.

Diagram conventions: blue anatomical right, orange left, white torso; grey floor line is the nominal source root plane. Fingers come from named source bones. No weapon mesh/hilt contact is verified. Equal-spaced eight-column overview is **not production key selection or a prescribed eight-frame animation**. The drawings are source skeletal diagrams, not rendered imported artwork or an original finished sprite.

Reproduce from repository root:

```sh
blender -b --python-exit-code 2 --factory-startup --python skills/modular-eight-direction-sprites/studies/source-motion/sample-ual.py -- --source research/sprite-animation/source-motion-v7/UAL1_Standard_RM.glb --output /tmp/new-source-motion-study
python skills/modular-eight-direction-sprites/studies/source-motion/draw-source-study.py --input /tmp/new-source-motion-study/source-motion.json
python skills/modular-eight-direction-sprites/studies/source-motion/measure-source-motion.py --input /tmp/new-source-motion-study/source-motion.json
```

This is completed source study; it has **not** retargeted the library to our original chibi proportions, supplied a complete original walk, changed sword ownership/grip geometry or obtained art/naturalness approval. [Natural-motion practice](../../../skills/modular-eight-direction-sprites/references/natural-motion-practice.md) records the concrete re-authoring work needed before final production.
