# Shared reusable authoring rig

## What opens and works

- **shared-authoring-rig.blend**: clean action-free rig, 60 stable named bones, 10 live attachment sockets, two skinned reference meshes and 8 fixed native orthographic cameras. All textures are packed; no external file links are required.
- **shared-authoring-rig.glb**: the same static skinned skeleton, cameras, sockets and embedded textures. It contains no animations. Reimport was checked in Blender.
- **native-walk-example.blend**: one editable 16-sample native walking action, frames 1–16, 80 ms/display frame (25 fps / fps_base 2). All 51 controlled bone world matrices match the checked source before saving and after reopening. No terminal pose was cloned and no per-frame fitting was applied.

Open the walk example and play frames 1–16. Select CAM_S / CAM_SW / CAM_W / CAM_NW / CAM_N / CAM_NE / CAM_E / CAM_SE to inspect real camera angles. Keep these cameras fixed while producing part drawings. The action-free file is the starting point for a new rigged mesh; source motions remain separate.

## Reuse

The skeleton names and hierarchy are shared across class profiles. `.L` and `.R` mean anatomical left/right, not screen position. Bind replacement meshes to existing named deform bones, retaining their rest orientation. Do not rename skeleton bones or rebuild a different skeleton per ordinary humanoid class.

Sockets are bone-parented empties. Parent accessories to SOCKET_head / SOCKET_headgear, SOCKET_weapon_right_hand, SOCKET_offhand_or_shield, SOCKET_back_accessory or SOCKET_cape as appropriate. A bow uses the anatomical left/offhand attachment, with the right hand controlling draw/release; attaching it to the release hand is wrong. The sockets follow their bones under posed rotation in both reopened formats.

The reference body is the existing repository reference mesh. **This is not six finished character meshes, not a female anatomy asset, and not approved final character illustration.** Class/sex profile entries specify skeleton compatibility, not completed outfits or anatomy validation. Missing action sets and sprites are not substituted.

## Part sprite connection

Current painted cutouts remain the authoritative illustration assets. The NE Mage walking sheets are in `../../review/mage-walk-editor-sheets-20261026/`: 4×4 cells at 1536 px/cell with root [768,1100.8]. Composite Weapon, BodyCostume, WeaponHandOccluder, HeadHair in that order before final reduction. Male and female share all three non-head role sheets byte for byte. Use source native controls when authoring replacement heads/outfits; do not fit each cell independently. Other camera/action cells still require finished artwork.

Protected Swordsman parts use their own recorded 768 px canvas and source rig registration. Do not project them onto this rig or scale them to the Mage canvas as if their native captures were identical.

## Repairs and evidence

Two pre-existing coincident faces had different materials/UVs. The derived mesh splits six vertex indices to preserve both faces and every original textured surface and skin weight. No face is deleted. Twelve undefined source corner normals are filled from their face normals; defined shading normals remain within 6.62e-5 vector error. The original canonical rig is unchanged.

See manifest.json, roundtrip-camera-proof.json and native-walk-proof.json. GLB seam vertices are split by its format/exporter, so its vertex count differs from Blender's without implying a different skeleton or missing skin.

The sample motion license evidence is included separately. Its CC0 terms concern Mesh2Motion source motion; they do not relicense the repository's character mesh or textures.

## Rebuild

Run frozen package-source.py with Blender 5.2.2 and the original pinned rig/spec/native controls from the repository, choosing a new output folder. Use verify-source.py for real Blender/GLB reopen checks and bake-native-motion-source.py to reproduce the saved motion example. Both check tools reject overwriting existing proof artifacts. A rig rebuild verifies geometry, bindings and matrices; byte-identical Blender save files are not promised.
