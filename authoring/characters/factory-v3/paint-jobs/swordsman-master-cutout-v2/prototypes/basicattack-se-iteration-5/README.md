# Iteration 5: earlier, thicker SE WeaponLight

**Status: review-only; not runtime art or owner-approved.**

This pass responds to the owner's note that the previous trail appeared too late
and was too thin. It retains the independently generated iteration 4 slash
shape and custom plum-gray → lavender-silver → warm-ivory colors, scales trail
thickness vertically by `1.22`, and raises the base opacity multiplier to
`0.94`. The first low-opacity emission begins during sword acceleration, the
widest/highest-opacity section lands on the audited contact pose, and a faint
remnant fades through follow-through.

The research branch's attack-trail study recommends emitting on the fast forward
cut, allowing a collapsing remnant, and clearing it during recovery. This pass
applies that timing principle to the selected `Sword_Attack` samples. The sample
poses, motion curves, contact marker, and frame durations are unchanged.

## Timing and frame maps

- First emission: phase `0.39`, timeline frame 6, source frame 18 / 754ms,
  opacity multiplier `0.24`.
- Trail builds through the main lateral sweep and peaks on contact: phase
  `0.63`, timeline frame 10, source frame 29 / 1239ms.
- Follow-through remnant: phase `0.735`, timeline frame 12, source frame 34,
  opacity multiplier `0.28`.
- Fully clear at recovery: phase `0.84`, timeline frame 13, source frame 39.

`source/trail-frame-map.json` maps the selected source cells. The companion
`source/frame-opacity-map.json` fades the effect into the cut and out through
recovery; `source/motion-review.json` records the retimed effect window. The
normalized effect remains in a separate transparent `WeaponLight` layer.

## Review outputs

- [One-shot 16-frame SE GIF, 480px review size](review/basicattack-se-weaponlight-one-shot.gif)
- [Over-character contact sheet](review/weaponlight-over-contact-4x4.png)
- [Behind-character contact sheet](review/weaponlight-behind-contact-4x4.png)
- [Transparent 4×4 WeaponLight atlas](layers/WeaponLight/weaponlight-se-4x4.png)
- [Transparent 16-frame vertical WeaponLight strip](layers/WeaponLight/weaponlight-se-16.png)
- Individual frames: `layers/WeaponLight/frames/weaponlight_se_00.png` through
  `weaponlight_se_15.png`.

The GIF plays once, has no loop extension, and holds the character's final
recovery pose for review. The `WeaponLight` is empty outside the slash window.

## Source and rebuild

The raw effect-only atlas and its exact generation prompt are retained in
`source/`; the art is original and does not include Ragnarok pixels. Ragnarok
examples informed the general frame-synchronized separation and sweep timing
only. The reusable normalizer writes source hashes, the per-frame map, alpha
bounds, and exposure data to `review/weaponlight-atlas-provenance.json`.

```sh
python3 tools/character_factory_v3/normalize_weaponlight_atlas.py \
  --atlas authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-5/source/weaponlight-atlas-imagegen-raw.png \
  --frames-dir authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-3/review/frames \
  --timeline authoring/characters/factory-v3/motions/retargeted/16frame-candidate/basicattack.timeline.json \
  --frame-map authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-5/source/trail-frame-map.json \
  --frame-opacity-map authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-5/source/frame-opacity-map.json \
  --opacity 0.94 \
  --thickness-scale-y 1.22 \
  --layers-dir authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-5/layers/WeaponLight \
  --review-dir authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-5/review
```

This is still a single-facing paint test. The base SE master shows red edge
artifacts and blade clipping; a clean 8-direction × 16-frame master, matching
cutouts, game preview, and owner review are still required.
