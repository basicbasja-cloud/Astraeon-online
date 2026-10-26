# Original tall guide rig and sampled actions

This uses the **original Mesh2Motion human guide mesh and 66-bone skeleton**,
the basis of the earlier Swordsman process. The compact F01 target is not used.
The mannequin is an authoring reference, not six finished class/sex meshes or
final painted character art.

## Files and checks

- `original-guide-actions.blend`: editable FK skeleton, original skinned guide
  mesh, 48 named action samples, eight real orthographic cameras, and nine
  bone-parent socket references. Open the Action Editor and select an action
  named `Guide_Class_Action__jobid`; set the scene end to its frame count.
- `original-guide-actions.glb`: portable reference rig and all 48 sampled
  actions. No external texture dependencies or animation key reduction.
- `manifest.json`: all 796 poses, actual source action/frame references,
  guide/replay hashes and per-action reopen checks. Worst reopened world-matrix
  error: **1.0579824447631836e-6**.
- `glb-roundtrip-proof.json`: all 48 actions / 796 poses imported again and
  compared against actual source skeleton replay. Worst matrix error:
  **3.2782554626464844e-6**.

There are 36 Mesh2Motion jobs and 12 retained KayKit fallback jobs. KayKit bow
poses include the documented original-guide human adaptation and contact IK;
they are not unretargeted Mesh2Motion bow animations. The kit retains the
existing guide geometry, including known visual-review limits. Pose matrix
agreement does not certify natural motion, final hands, painted cutout quality,
or character completion.

`SOCKET_Hand_L/R` are wrist references. `SOCKET_WeaponGrip_L/R` are the actual
index/pinky knuckle midpoint, suitable as a weapon pivot before applying a
weapon-specific local orientation. `socket-proof.json` verifies all nine pivots
in both formats through every pose; worst error is 8.221336736758782e-7 m. This
does not approve a painted glove or weapon fit.

## Timing and cameras

Actions use **uniform 80ms sample-index playback** for authoring inspection.
The source samples can be nonuniform. Production timing, event/release markers,
interpolated poses and gameplay root travel are not authored by this package.
The default cameras come from the Mage/Walk guide. Use each action's pinned
guide manifest for its exact original camera; do not assume the legacy preserved
Swordsman action camera scale is identical.

The action aliases are shared between the three classes and both sexes.
Sharing animation or guide geometry does not approve sharing an incompatible
painted body fit. Head/costume/weapon cutouts still require matching pose, real
camera, placement and fitting metadata.

## Reproduce

From the repository root, use fresh output destinations:

```bash
blender --disable-autoexec -b --python tools/character_factory_v3/package_original_guide_rig_library.py -- --repository-root "$PWD" --output /tmp/tall-guide-replay
blender --disable-autoexec -b --python tools/character_factory_v3/export_original_guide_library_glb.py -- --library /tmp/tall-guide-replay
blender --disable-autoexec -b --python tools/character_factory_v3/verify_native_action_library_glb.py -- --library /tmp/tall-guide-replay --controls-library authoring/characters/factory-v3/patch-0.0.1/research/native-rig-library-20261026 --glb-name original-guide-actions.glb --blend-name original-guide-actions.blend --original-guide-replays --output /tmp/tall-guide-replay/glb-roundtrip-proof.json
```

Use the pinned Blender 5.2 series. Source metadata was independently replayed
with Blender 4.3 earlier; it is not regenerated or modified by these commands.
CC0 evidence for Mesh2Motion and KayKit remains in `motions/legal-evidence/`.
The source GLBs, original artwork and the earlier rig packages are unchanged.

The exact exporter and socket verifier are under `tools/character_factory_v3/`.
Run `verify_original_guide_sockets.py --library <package> --output <fresh-proof>`
with Blender to reproduce the equipment-pivot checks.
