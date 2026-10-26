# Reusable rig checkpoint — 26 October 2026

[Open/download the reusable Blender and GLB kit](../../../../authoring/characters/factory-v3/patch-0.0.1/rig-kits/shared-authoring-rig-v2-20261026/README.md).

- 60 bones, 8 fixed actual cameras and 10 live bone sockets, embedded textures.
- Actual Blender + GLB round trips: all bones/cameras/sockets preserved, no unweighted vertices or invalid mesh warnings. Maximum live socket matrix error 4.77e-7 over 3 test poses per format.
- Derived mesh repair preserves both overlapping faces, all UV/material surfaces and skin weights. Six indices are split; zero faces are removed; 12 undefined source normals are repaired. Original source rig/painted art unchanged.
- One saved native walking example: 16 poses × 51 controlled bones. Maximum world matrix difference 1.67e-6, including reopen. No endpoint clone or per-frame pose fitting.
- This is shared authoring infrastructure, not six final class/sex meshes or all completed action sets. Factory coverage remains 2/96 and zero newly complete admitted characters.

## Existing painted part output remains unchanged

![Male Mage walking study](../patch001-native-walk-20261026/male-walk.gif)
![Female Mage walking study](../patch001-native-walk-20261026/female-walk.gif)

These are the previous NE painted cutout studies. The rig reference mesh is not a replacement illustration. [Editable part sheets](../../../../authoring/characters/factory-v3/patch-0.0.1/review/mage-walk-editor-sheets-20261026/README.md).

[Packaging log](package.log), [reopen checks](roundtrip.log), [native action bake/reopen](native-walk.log).

Archer work continues from all 16 real NW source arm poses; the new arm templates require visual and attachment review before any factory import. Completing the rig kit does not approve those drawings.
