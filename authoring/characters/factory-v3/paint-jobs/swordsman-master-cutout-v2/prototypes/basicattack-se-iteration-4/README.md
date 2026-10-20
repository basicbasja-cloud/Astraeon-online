# Iteration 4: SE lateral slash and WeaponLight

**Status: review-only; not runtime art or owner-approved.**

This pass responds to the owner's rough 4×4 Ragnarok-style slash reference. It
keeps the effect independent as `WeaponLight`, with a low horizontal brush
sweep colored by an original plum-gray → lavender-silver → warm-ivory gradient. The preview draws that layer over the character so the sweep stays
visible; a behind-character composite is included for draw-order comparison.

## Motion audit

The selected Mesh2Motion `Sword_Attack` was rechecked against the sampled
trajectory. The strongest lateral blade sweep crosses the body in source frames
24–33. The old contact event at phase `0.50` / frame 8 came before this section.
The candidate event is now phase `0.63` / frame 10 / 1239ms; follow-through is
phase `0.735`. The motion curves, sampled poses, frame durations, and one-shot
playback are unchanged. The original pose-guide timeline is preserved beside
the guide provenance.

The generated atlas itself is remapped to the observed sweep window. In
zero-based timeline indexes, frames 8–13 use atlas cells 4, 5, 7, 8, 10, and 11;
all other frames are transparent. This starts the trail as the lateral sweep
begins, peaks at contact, tapers through follow-through, and fades as recovery begins.
The previous and candidate event positions are recorded in
[`source/motion-review.json`](source/motion-review.json).

## Preview and layers

- [One-shot 16-frame SE GIF, 480px review size](review/basicattack-se-weaponlight-one-shot.gif)
- [Over-character contact sheet](review/weaponlight-over-contact-4x4.png)
- [Behind-character contact sheet](review/weaponlight-behind-contact-4x4.png)
- [Transparent 4×4 WeaponLight atlas](layers/WeaponLight/weaponlight-se-4x4.png)
- [Transparent 16-frame vertical WeaponLight strip](layers/WeaponLight/weaponlight-se-16.png)
- Individual frames: `layers/WeaponLight/frames/weaponlight_se_00.png` through
  `weaponlight_se_15.png`.

The GIF plays once and holds the recovery pose for review. It has no loop
extension; the production clip remains a one-shot that transitions to Idle.

## Source and processing

The raw effect-only atlas is
[`source/weaponlight-atlas-imagegen-raw.png`](source/weaponlight-atlas-imagegen-raw.png).
Its alpha channel is real transparency. `source/trail-frame-map.json` records
the source-cell mapping; `source/color-ramp.json` records the original
post-process palette. `review/weaponlight-atlas-provenance.json` records the
input hashes, cell bounds, per-frame phase, alpha bounds, timeline, and output
paths. Rebuild the registered layer and previews with:

```sh
python3 tools/character_factory_v3/normalize_weaponlight_atlas.py \
  --atlas authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-4/source/weaponlight-atlas-imagegen-raw.png \
  --frames-dir authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-3/review/frames \
  --timeline authoring/characters/factory-v3/motions/retargeted/16frame-candidate/basicattack.timeline.json \
  --frame-map authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-4/source/trail-frame-map.json \
  --layers-dir authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-4/layers/WeaponLight \
  --review-dir authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-4/review
```

This remains a single-facing paint test. The underlying SE master still has
edge artifacts and blade clipping in the strike segment; the eight-direction
full master, frame-matched cutouts, gameplay preview, and owner review remain
open.
