# BasicAttack SE, iteration 11

## Review status

**Not approved.** The Rokoko guide is the current motion reference. The painted sheet is a rejected pose study and is not a runtime asset.

## Motion source

This one-shot uses the Rokoko `SwordFight_mixamo.fbx` sequence and stops at source frame 511, before the next sword lift. The 16 samples are:

`480, 482, 485, 487, 490, 492, 494, 496, 498, 499, 500, 502, 504, 506, 509, 511`

The source-frame spacing is retained, with a 300 ms recovery hold on the last pose. Timeline duration is 1,336 ms; the GIF encodes 1,340 ms because GIF delays use 10 ms increments. It follows an overhead wind-up into a diagonal downstroke and recovery; it is not forced into a horizontal side cut.

## Character registration

The previous footwear detector missed the boots on the wide-lunge pose and aligned to a point 124 source pixels too high. The revised Swordsman footwear mask finds the brown boots, uses one shared scale (`0.689840`) for all 16 frames, and corrects the final resampling offset after resize. The current 320 px review sheet has root `(160, 264)` in every frame; the measured footwear-baseline error is 0 px and no source character touches a cell edge.

## Paintover result

The current review output is linked below. Its character is larger and its floor anchor is steady, but the painted poses still diverge from the Rokoko guide. In particular, the first three painted poses stay in a low lunge while the guide is upright, and the sword/arm geometry changes independently of the guide. A separate four-pose generation repeated nearly the same pose in all cells; a single-pose generation also changed the guide's arm and sword angle. Those outputs were rejected. Do not cut modular layers from this sheet.

- [Rokoko guide contact sheet](source/rokoko-blender-guide/review/rokoko-basicattack-se-guide-4x4.png)
- [Painted contact sheet, fixed root and shared scale](review/paintover-component-normalized-v4/review/basicattack-se-master-contact-4x4.png)
- [Painted one-shot GIF](review/paintover-component-normalized-v4/review/basicattack-se-master-one-shot.gif)
- [Normalization and frame audit](review/paintover-component-normalized-v4/review/basicattack-se-master-provenance.json)

## Next production step

Repaint each frame against its matching Rokoko pose or use the approved articulated cutout workflow. Compare the blade and both wrists to the guide, then check foot contacts and scale through the GIF. Only after pose fidelity passes should the same-frame `BaseBody`, `HeadHair`, `Outfit`, `Weapon`, `BackAccessory`, and separate `WeaponLight` cutouts be made.
