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
The two `before-*` tracking folders are historical diagnostics and must not be
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
