# Independent painted Mage parts — 25 October 2026 (Asia/Bangkok)

Production checkpoint, **not a complete playable character**. Patch coverage is
still 2/96 imported paint jobs and zero newly complete six-character packages.
This is one male Mage NE casting cycle, not four accepted casting directions.
The existing Swordsman drawings and sword trail are preserved.

## What changed

- Separately painted complete left/right arms and closed torso shoulders replace
  visible-only cuts that produced holes when the casting arm lowered.
- Nine reusable internal pieces follow the original fixed-camera Mesh2Motion
  joints. No per-frame generation, camera change or bounding-box normalization.
- Head transport is rotation/translation only: no scale, shear or reflection.
- A recorded clothing donor fills 70 previously transparent pixels beneath the
  old staff footprint. Existing body pixels are unchanged by that repair.
- Public HeadHair / BodyCostume / whole Weapon preserve hidden body and prop
  pixels. Body includes hand depth order; it is not flattened together with head.
- Two hairstyles share all 64 body/weapon frame files byte-for-byte.
- Eight role-separated runtime review atlas pages, 186 unique pixel objects.
- Five full-cell editor sheets, 160 source cells verified exactly. The alternate
  hairstyle uses its own head sheet and reuses the original body/weapon sheets.

## Evidence

[Interactive compositor review](index.html), [32-pose contact](contact-32.png),
[original hairstyle GIF](mage-auburn-continuous.gif),
[alternate hairstyle GIF](mage-silver-continuous.gif).

- Native staff: 32/32 pass at 1px tolerance; maximum error 0.409889 native pixels.
- All four public layers including Master have equal first/last RGBA; each
  endpoint was rendered from its recorded native pose, not copied afterward.
- Head orthogonality error <=4.45e-16; determinant approximately 1 for all32.
- Public merge differs from nine-piece native render by at most1/255 rounding.
- Actual game compositor: 64 poses × light/dark backgrounds =128 comparisons;
  maximum difference2/255, no page/resource errors. Head/weapon toggles exercised.
- Frozen full-cycle replay:325 files byte-identical (320 native PNGs plus GIF,
  receipt and three exact source files).
- Python factory suite255 pass, including actual Blender geometry/floor checks.
- Direct Node suites: modular40 pass; native composition3 pass.

The compositor test does not certify natural motion or six-character gameplay.
All32 NE frames were inspected on the contact sheet; the independently painted
shoulder caps connect throughout this study. Other cameras, actions, class/sex
variants and ordinary new-character creation remain incomplete. Do not bypass
package admission or silently substitute this NE study for missing actions.

## Reproduction

Canonical paths are under `authoring/characters/factory-v3/patch-0.0.1/`:

1. `build_independent_mage_kit.py`: independent-kit-v2-recipe.json plus the frozen
   canonical-mage-channel-eight-views guide → mage-independent-paint-kit-v2.
2. `render_segmented_mage_action.py`: that kit, base guide, the native
   mage-closed-casting-cycle/canonical-guide and independent-rigid-head-motion
   recipe → mage-independent-final-cycle.
3. `assemble_independent_action.py`: final cycle → public interchangeable roles.
4. `replace_native_action_head.py`: public cycle, recorded native head matrices,
   silver-head-native.png → silver variant; body/weapon are unchanged.
5. `package_layered_hold.py`: both variants → mage-independent-action-atlas.
6. `export_review_part_sheets.py`: sheet-samples.json → editor sheets.

Every stage preserves its exact source code, input digests and receipts. Frozen
replay evidence records what was regenerated, rather than inferring success
from the presence of a script. Browser checker requires localhost server8011.
