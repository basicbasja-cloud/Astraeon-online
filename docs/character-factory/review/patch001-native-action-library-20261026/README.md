# Native action rig coverage — 26 October 2026

[Blender/GLB library, source bindings and usage](../../../../authoring/characters/factory-v3/patch-0.0.1/rig-kits/sampled-native-action-library-v2-20261026/README.md).

- All 48 current source families replayed against original source capture landmarks. The special nonuniform Swordsman BasicAttack samples are retained through their pinned explicit sampler.
- 796 poses × 51 bone matrices baked and checked after reopening Blender: maximum matrix component error 2.03e-6.
- All 48 GLB actions imported and checked at every pose: maximum matrix component error 4.30e-6. Default animation reduction lost a small idle movement; it is disabled in the delivered library. Checks were not relaxed.
- Six class/sex profile maps contain 114 reusable action bindings. This is shared rig/pose coverage, not six class-specific character meshes or completed sprite imports.
- 36 Mesh2Motion source families and 12 explicitly identified retained KayKit fallbacks. Owner reaffirmed Mesh2Motion preference.

**Not finished:** gameplay timing/events, root travel application, final motion/anatomy acceptance, all required illustrated actions/directions, costume/hair demonstrations for each class and six-character gameplay admission. Current actual sprite import coverage remains 2/96, zero newly complete characters. The rig library uses a sample-index preview timeline; it does not claim native/production timing preservation.

Existing painted modular walking study, unchanged:

![Mage male walk](../patch001-native-walk-20261026/male-walk.gif)
![Mage female walk](../patch001-native-walk-20261026/female-walk.gif)

[Bake/reopen evidence](bake-and-reopen.log), [animated GLB reopen](glb-reopen.log).

Owner correction: the fragmented Archer limb assembly is rejected. Resume coherent whole-action masters and cut BodyCostume (including limbs), HeadHair and Weapon from matching frames/views. None of the separate-limb proposals counts as a production component.
