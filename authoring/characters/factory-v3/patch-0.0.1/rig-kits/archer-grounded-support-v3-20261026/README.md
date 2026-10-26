# Archer grounded-support V3 — editable rig study

Open `sampled-native-actions.blend`, select `ARM_FantasyCharacter01`, and choose `CF_Archer_BasicAttackGroundedSupportV3__2fed9f286cdd5c5ffbf4`, frames1–16. `sampled-native-actions.glb` contains the same action and embedded reference skin/textures. The rig has60 bones, eight fixed cameras and ten sockets. Constraints remain disabled; the action is editable FK animation. It is one reference mesh, not male/female Archer production models.

This is an explicitly authored target-rig contact/support adaptation of KayKit CC0 bow motion. Both feet keep fixed support XY; their actual weighted soles contact the plane. Upper-body and foot orientations retain the parent controls. The anatomical knee bend plane is transported before solving the new ankle axis. Original motion files, original captures, the shared48-action library and accepted Swordsman art are unchanged. V2’s knee-reversal candidate is rejected.

Timing is an80ms/sample authoring preview, not production release/damage metadata. Final painted sprite actions and gameplay are not approved by this kit. Mesh2Motion remains the preferred general provider; no dedicated bow clip was found in Mesh2Motion or the uploaded ActionForge bundle.

Rebuild from repository root:

```sh
blender --disable-autoexec -b --python tools/character_factory_v3/bake_native_controls_library.py -- --rig authoring/characters/factory-v3/patch-0.0.1/rig-kits/shared-authoring-rig-v2-20261026/shared-authoring-rig.blend --controls-library authoring/characters/factory-v3/patch-0.0.1/research/archer-anchored-support-v3-20261026 --output /tmp/archer-grounded-v3-replay --export-glb
```

Then run `verify_native_action_library_glb.py` with that library, the same controls-library and a fresh proof path. `glb-roundtrip-proof.json` checks all16×51 pose matrices after GLB import. Parent source/control/anchor hashes and frozen repair code are under the controls-library folder. No missing final drawings are substituted by this reference mesh.
