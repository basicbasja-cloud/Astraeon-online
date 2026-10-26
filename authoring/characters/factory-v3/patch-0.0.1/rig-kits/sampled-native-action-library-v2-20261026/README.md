# Reusable sampled native action library

## Delivered

`sampled-native-actions.blend` contains all 48 source-pose families from the current patch ledger on the common 60-bone rig. `sampled-native-actions.glb` exports those same 48 actions. Both include the fixed native cameras, live sockets and embedded reference textures from the shared rig kit.

The library contains 796 sampled poses, each with 51 checked body/finger bone matrices. Every pose was checked after saving/reopening Blender and after importing the exported animated GLB. See manifest.json and glb-roundtrip-proof.json. Animation key reduction is disabled: default reduction discarded a small movement in the Archer CombatIdle source and failed the strict pose check; the delivered export retains it.

Mesh2Motion remains preferred: 36 native source families use it. Twelve retained KayKit fallback families are separately labelled. ActionForge is being studied as an additional source and has not silently replaced these actions.

## Use

Open the Blend file, select ARM_FantasyCharacter01 and choose an action starting with `CF_` in the Action Editor. Use that action's frame range (usually 1–16; see manifest). Mage Walk is selected by default. All eight named cameras are fixed actual views, not mirrored alternatives. Attach a new mesh to the existing deform skeleton; use the bone sockets for accessories.

`class-action-bindings.json` maps all 114 requested action instances across the six class/sex profiles to the 48 reusable native families. These bindings mean skeleton/pose reuse, **not six finished meshes or sprite packages**. The reference mesh remains a single existing repository model; female anatomy and class costumes are not delivered by this rig library.

## Timing and gameplay boundary

Playback here uses a uniform **sample-index authoring timeline** (80 ms per sample). It is not production timing. Original source action names and source frame numbers are preserved per pose, including the retained nonuniform Swordsman BasicAttack sample list. Multi-action timing, contact/release markers, cross-state recovery, root travel application and gameplay transitions still require authoring. Source root travel is retained in the raw source-control snapshots and is not applied to gameplay by this kit. No terminal pose was invented to close a cycle.

Bone matrix preservation does not establish natural weight bearing, finger-grip quality, smooth final drawing, clean sprite cuts or final gameplay readiness. The existing painted parts remain separate and authoritative; never substitute this reference model for approved Swordsman illustration.

## Reproduce

From the repository root, with Blender 5.2.2:

```sh
blender --disable-autoexec -b --python tools/character_factory_v3/bake_native_controls_library.py -- --rig authoring/characters/factory-v3/patch-0.0.1/rig-kits/shared-authoring-rig-v2-20261026/shared-authoring-rig.blend --controls-library authoring/characters/factory-v3/patch-0.0.1/research/native-rig-library-20261026 --output /tmp/native-action-library-replay --export-glb
```

Then run tools/character_factory_v3/verify_native_action_library_glb.py on that output with the same controls library and a new proof path. Frozen baker/verification sources accept --repository-root when run outside their original tools folder. Rebuilds promise checked pose/skin/camera semantics; byte-identical Blender binary saves are not promised.

The source-control research folder retains original source skeleton snapshots, canonical controls, original guide metadata and logs. No original guide frame PNGs or character drawings were modified by this bake.
