# Four-direction attack review

The owner corrected the attack scope to four diagonal views in the requested RO-style presentation: **SW, NW, NE, SE**. This packet contains the gold swordsman in sixteen real illustrated poses per view (64 poses). No view is produced by horizontal mirroring. SW/NW/NE were generated as complete pose sheets using their actual fixed-camera Mesh2Motion guides; the existing accepted SE illustrations are retained. The original artwork, prompts, guide references and manual cutout annotations are included.

## Review

- `four-directions-attack.gif`: all four views at the same source cadence.
- `four-directions-attack-slow.gif`: same animation at 3x-slow cadence.
- Each view has `attack.gif` and `attack-slow.gif`.
- `review.html`: standalone offline viewer; choose direction, toggle head/body/weapon/trail, scrub poses and adjust speed. It loads one direction at a time. Browser interaction has not been automated in this run.
- `four-direction-turntable.gif`: a four-view rotation review of the recovery pose. This is intentionally a view-switching loop, not an attack loop.
- Guard/strike/recovery contact PNGs and `head-cutout-review.png` support still inspection.

All attack GIFs are one-shots with a recovery hold, without a forced final-to-first loop. Sixteen painted poses sample the original sixty-frame source capture; there are no painted-image crossfades or invented intermediate frames.

## Separate sheets and editing

`sheets/` contains transparent **2048x8192** sheets with **512x512** cells. Columns are SW, NW, NE, SE; rows are chronological poses 0–15. `sprite-sheets-manifest.json` provides timing, hashes and layer order. Every one of the 512 cells across eight sheets matches its individual PNG in alpha and visible RGBA.

| Sheet | Role |
| --- | --- |
| HeadHair | Visible face/head and hair, together |
| BodyCostume | Complete clothed body including scarf, gloves and boots |
| Weapon | Visible blade and hilt pixels |
| WeaponLightBack | Trail portion behind the costume |
| WeaponLightFront | Trail portion in front of the costume |
| WeaponHandOccluder | Visible glove overlap support above the trail |
| WeaponLight | Merged effect reference; use Back/Front for actual depth stacking |
| Master | Unmodified full illustration reference |

Each direction also has individual transparent frames, 4x4 per-part sheets and an editable `layered-sprite-sheet.ora`. Stack Back FX, BodyCostume, Front FX, HeadHair, glove support, Weapon. No part receives independent recentering or scaling. No hidden naked-body/clothing surfaces are supplied.

## Source geometry, cutouts and effects

The original Blender scene was opened to export all sixty source poses' world-space torso landmarks. Camera manifests and captured source blade positions come from `../eight-direction-guides/`. Illustrations retain one common native pixel scale; four documented row translations per view correct the generated sheet packing. These packing offsets do not establish a physical root track or exact anatomical registration.

Manual visible head seeds and blade endpoints drive the cutouts, with material colors supporting collar/hilt boundaries. All 64 recompositions have zero pixel mismatches. This proves pixel reconstruction, not final semantic boundaries or naturalness.

Effects remain transparent during wind-up (poses 0–3), emit after the cut at pose 4, fade at 25% opacity at pose 5, then clear. Recent tip travel is bounded by 0.65x painted blade length. The SE effect retains its existing owner-corrected forward sweep. Other views derive their short sweep from the corresponding real camera's source blade, mapped only at the effect level onto the annotated painted contact blade. Source world torso/camera depth separates the front/back ribbon; this is an approximate torso-plane occlusion, not per-pixel mesh depth. All effect frames are in bounds.

## Review findings and scope

`quality-audit.json` reuses the research sprite auditor's alpha-IoU helper and 0.88 warning, and compares manually annotated blade angles with the corresponding guide. A low IoU during a fast cut is a review flag, not proof of jitter. Near-axis/occluded blades are excluded from the angle median.

**NE pose 8** (the ninth displayed drawing) still exaggerates the visible blade length where the guide projects to approximately 8.6px at 1024px. This foreshortening and the head/collar/guard mask edges need visual refinement. This is the requested four-view experiment, not approved game-runtime art. The prior SE alternate-cosmetic experiment remains in `../modular-swaps-review/`; this packet expands the gold skin.

## Rebuild

```sh
python tools/character_factory_v3/build_four_direction_attack_review.py authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/four-direction-attack-review --stage all
python tools/character_factory_v3/build_four_direction_attack_viewer.py authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/four-direction-attack-review
```

`export_motion_world_landmarks.py` reproduces the Blender landmark export from the compressed source scene.
