# Licensed anatomy source study — asset-fit-04

**Internal NO-SHIP.** This is a fresh static source study, not the approved
character, an accepted rig, or a completed production factory. The original
painted concept remains the only approved design. No rejected model or
independently generated limb image has been resumed.

Quaternius's free Standard FBX supplies connected anatomical geometry and
inherited skin groups. Static source-space fitting brings it toward the measured
concept pose. The original ASTRAEON costume, hair, cape, material atlas and
weapon remain editable surfaces. The compatible Ranger boots and trousers were
tested but remain hidden inspection references because they intersect this body.
Current garments are extracted from this body and given surface clearance;
they are not separate image tiles assembled around joints.

Eight headings share the same 320 canvas, camera, scale and root (160,264).
Game-scale review displays those images at 160, with root (80,132), without
independent per-view fitting. `renders/*-final-static.png` is the latest static
set. `SE-final-static-large.png` and matching SE/W/NW/N grip diagnostics show
the source in detail. Earlier fitting/surface renders are intermediate evidence.

`equipped-layer-*.png` contains the visible pixels of this equipped combination.
Physical hand/costume holdouts omit covered weapon pixels. These five logical
layers are not arbitrary-substitution assets: outfit removal is re-rendered from
the actual source; complete body-only frames retain concealed anatomy. No action
coverage is assigned to these static checks.

Run source03's build → detail → coat, import the free references into separate
scenes, then `fit-free-character-study.py` → `refit-free-character-costume.py` →
`refine-free-character-style.py` → `repair-free-character-grip.py` →
`close-free-character-costume-gaps.py` → `finish-free-character-surfaces.py` →
`inspect-free-character-grip.py` → `bake-free-character-source-checks.py`.
Scripts run through safe-mode Blender MCP. This sequence is recorded, but has
not yet passed a clean-room end-to-end reproduction test. Do not describe it as
a validated factory. The import archives stay in the ignored local asset cache.

The editable working project is saved locally under
`.character-tools/checkpoints/asset-fit-04-native.blend`. It is not a distributable
standalone asset package. This Save Copy includes source03 and separate asset
inspection scenes; the active asset-fit-04 scene itself has zero armatures.
See `FREE_ASSET_PROVENANCE.json` for archive hashes,
creator credits, exact license evidence, and the differing current site terms.

Before rigging: resolve inherited joint triangles/poles, validate deformation
loops, normalize/review weights, create actual controls, and pass pose/grip QA.
Existing donor weights are interpolation guides here, not an accepted bind.
There are zero armatures/actions in this scene. Likeness and painted finish
remain below the approved concept, and the NW blade remains occluded.
