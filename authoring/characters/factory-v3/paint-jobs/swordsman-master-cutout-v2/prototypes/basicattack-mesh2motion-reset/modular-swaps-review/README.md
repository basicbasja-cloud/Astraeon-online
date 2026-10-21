# Same-frame cosmetic swaps and sword trail

Built from the sixteen SE no-cloak frames the owner liked. The source animation cadence and accepted frame packing remain unchanged. The alternate Moon Knight illustration is generated as one full sheet, then cut into corresponding visible components. Exact prompt and source reference are in `generation-provenance.json`.

## Inspect

- `five-way-swaps-slow.gif`: original, head only, outfit only, weapon only and all swapped, at 3x-slow cadence.
- `all-swapped.gif`: alternate head, outfit and weapon with the trail at normal cadence.
- `forward-trail-slow.gif`: gold and Moon Knight versions with the owner-corrected forward sweep, side by side at 3x slow cadence.
- `head-only.gif`, `outfit-only.gif`, `weapon-only.gif`: isolated cosmetic changes.
- `review.html`: standalone offline viewer. Choose head, costume and weapon independently (eight combinations), toggle trail, scrub frames and change speed. It embeds all images and has no external dependencies. Browser interaction has not been automated or validated in this run.
- `swap-contact.png`: guard, strike and recovery comparison.
- `cutout-layer-review.png`: visible component separation at the strike.

## Editable art

Each `gold/` and `moon/` folder includes sixteen registered transparent 512x512 PNGs for each part, matching 4x4 sheets, and `layered-sprite-sheet.ora` for Krita or another OpenRaster editor.

| Part | Meaning |
| --- | --- |
| HeadHair | Visible face/head and hair together, cut separately for each pose |
| BodyCostume | Complete visible clothed body, including scarf, gloves and boots |
| Weapon | Visible blade, guard and exposed pommel; gripping glove stays with the costume |
| WeaponLight | Independent transparent trail; clear outside the attack window |

This follows the owner's practical RO-style proposal: replace the complete drawn clothed body for each pose. It does not claim an independently naked base body underneath clothing, or separate hair from face. No unseen surfaces are fabricated.

## Registration and evidence

The manual pose-specific polygons and blade annotations are editable JSON. The weapon boundary combines its annotated region with reference material colors; it is a reviewed prototype mask, not a semantic model. Revised head contours avoid including the surrounding scarf and sleeve. Both skins use exactly the accepted per-frame packing translations; no part is independently rescaled, moved or warped. Every original recomposed frame is byte-identical in RGBA to the accepted transparent frame. Both skins recompose their visible master pixels with zero mismatches across all 32 pose/skin combinations. This checks pixel registration; it does not prove every semantic mask edge is final.

The original plum/lavender/silver/ivory trail uses the accepted **painted** grip and tip annotations rather than overlaying the differently posed mannequin trail. It starts at frame 2, emits through frame 4 and fades through frame 6. Angular blade interpolation with a 0.9-frame history produces a curved swept ribbon; every sampled endpoint remains on its annotated painted blade. The owner corrected the first effect because it swept behind the character. The current effect maintains a clockwise forward winding through the strike and renders **in front of BodyCostume**, then behind the head, gripping glove and weapon. `WeaponHandOccluder` is a small copy of visible costume glove pixels supporting this occlusion, not a cosmetic slot. All effect frames remain within bounds. The projected angle interpolation is an approximation between sixteen sampled drawings, not recovered 3D blade motion.

## Scope

This is a cosmetic-swap review prototype for sixteen SE poses. There is no game-runtime replacement, eight-direction alternate set, separate hair-only interface, unseen body surface or final wrist/guard-edge approval. The new Moon Knight skin is an alternate original design; the owner's existing gold skin remains preserved.

Rebuild from repository root:

```sh
python tools/character_factory_v3/build_modular_swap_review.py authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/modular-swaps-review
python tools/character_factory_v3/build_modular_swap_viewer.py authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/modular-swaps-review
```

The assembly script verifies original frame equality, per-skin recomposition and effect bounds, and records these checks in its audit.
