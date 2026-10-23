# Archer male BasicAttack NW: source-first paint and cutout study

Status: source-aligned canvas study, **not a completed import or playable character**.

Sixteen retained1254px individual paintovers follow the locked Blender source first.
`selected-frame-repairs.json` selects repairs for6,7,14,15. The9th timeline slot
uses certified source pose8. Ready/recovery head pixels0/15 are identical;
frame15 removes only the arrow inside its recorded bounded repair mask.

From the repository root:

```sh
python authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study/assemble-review.py
python authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study/build-game-preview.py
```

The shared viewport is inverted once into the canonical canvas. No per-frame
figure fitting, body warping or pose interpolation occurs. Detail PNGs, GIFs and
canonical masters now share the same certified pose map. The1000ms game preview
is a proposed retiming; it is not admitted runtime timing.

`temporal-head-current` contains CPU SAM2 proposals for the current detail PNGs.
The folders with `before` in their names are historical diagnostics and must not be
imported. Masks preserve source RGBA pixels; exact reconstruction does not prove
correct semantic ownership. Head size/pose continuity still needs review.

`ready-cutout-study` separates HeadHair, BodyCostume and Weapon for0/15, with
zero visible reconstruction differences. The bounded weaponless donor contributes
only beneath fully opaque weapon pixels. Original visible hands remain unchanged.
Glove/arrow/string ownership and body remnants still require edge refinement.
This is not a full action cutout set. Raw generation inputs/prompts, local repair
masks and receipts remain alongside the proposals.

No owner approval, runtime admission, four-view completion or hairstyle/costume
variant completion is claimed here.

## Current three-part action sheets

`separate-sprite-sheets` contains16 canonical768px frames for each of HeadHair,
BodyCostume and Weapon, three transparent4×4 sheets, a sheet map and normal/slow
layer GIFs. Current `action-layer-proposals` use explicit hand/neck corrections;
older action tracking passes are retained with rejection notes. Seven inspected
local probes protect the ivory sleeve, gripping fingers, draw glove and neck.
These probes are not a complete semantic-mask certification.

Canonical masters explicitly restore near-opaque alpha245..254 to255; RGB and
softer edge alpha remain unchanged. Original generated paintings and detail
references remain untouched. This uniform matte cleanup changes177,072 alpha
pixels across16 canonical masters and allows actual hidden body pixels beneath
opaque equipment. No pose, figure scale or source guide changes. Bounded donors
retain142/95 hidden canonical body pixels in ready/recovery; other poses still
need hidden-surface authoring. Exact recomposition refers to the cleaned masters.

The actual browser compositor matches all16 masters when both use the same
native-canvas/final-resize path. Direct PNG resizing is a separate browser filter
baseline:1,391–1,624 changed pixels per frame, maximum composited channel delta
28/255 over grey. It is retained in the report, not hidden by the matching-path
comparison. Rendering equivalence is not a sharpness, anatomy or gameplay pass.

Head-only repair donors001 and002 were not selected: the latter also has a collar/
upper-body dip, requiring a source-first whole-pose correction. No per-frame body
fit, pixel warp or invalid boot/head reuse was applied.
