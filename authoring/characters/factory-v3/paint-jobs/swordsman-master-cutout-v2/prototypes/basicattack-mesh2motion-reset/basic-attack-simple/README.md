# BasicAttack — simpler original-rig single-cut review

A new review beside SkillOverhead: one cut, a shallower dip, and no spin/combo. Source: immutable Mesh2Motion CC0 `Sword_Attack`, sampled directly on its original rig using a knuckle-aligned sword proxy.

## Historical decision retained

An earlier Sword_Attack candidate was rejected as thrust-like. This compact native-rig guide/art variant is an explicit re-evaluation with corrected sword-grip projection and shorter holds; it does **not** overwrite that rejection or establish owner acceptance. Compare the actual guide and resulting GIF before choosing it for gameplay.

## Inputs and build

- Real fixed SW/NW/NE/SE cameras; no mirrored views; 16 poses each. Per-view camera settings, source samples and source GLB digest are in `source-guides/manifest.json`.
- Samples: 0,3,6,8,10,11,12,13,14,15,25,28,31,34,37,39. Large held intervals are compacted; poses are unchanged. Painted playback uses an explicit 1.4× cadence and a terminal review hold. It is a one-shot, not a promised seamless attack loop.
- The exact whole-sheet ImageGen prompt and output provenance are retained per view. Native sheet art remains unchanged.
- Per-pose visible pelvis/head/blade annotations live in `manual-annotations.json`. Each pose is translated as a whole onto its matching source pelvis at a fixed 0.5 source-projection scale. No per-frame fitting or body deformation is used. Neighbor-row fragments are excluded.
- Same-frame cutouts: HeadHair, complete BodyCostume, Weapon, hand overlap, and independent front/back FX. Material-assisted semantic edges remain provisional.
- The short recent blade sweep starts at pose7/source13, fades at8, clears at9. Recent tip travel is capped at0.55 blade length. Front/back staging is an explicit per-view art choice, not a claim of mesh-depth reconstruction.
- Sheets: columns SW,NW,NE,SE; chronological rows0–15; 512px cells; 2048×8192. Master and merged WeaponLight are references only.

```bash
python tools/character_factory_v3/layered_action_factory.py --action all
python tools/character_factory_v3/package_layered_factory_review.py --output /workspace/outputs
```

Source guide regeneration (art is not automatically regenerated):

```bash
blender -b -t 2 --python tools/character_factory_v3/render_basic_attack_factory.py -- --output authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/source-guides --size 1024
```

`cutout-audit.json`, sheet checks and factory receipts prove pixel/export properties, not natural motion, stable anatomy or semantic acceptance. Browser interactions were not automated. No runtime asset index is changed.
