# BasicAttack SE, iteration 16

## Review status

**Review only; not approved for runtime.** This is the most stable retarget study so far. It improves the first-pose match and uses all 32 source frames, but the 320 px research artwork is below the requested reference quality and the body, hand, and cape still need a faithful repaint.

## Motion

- Guide: [iteration 14 Rokoko guide](../basicattack-se-iteration-14/source/rokoko-blender-guide/review/rokoko-basicattack-se-guide-4x8.png)
- Source: Rokoko `SwordFight_mixamo.fbx`, source frames 480–511 at 30 fps, sampled at native cadence.
- Playback: non-looping 1,320 ms GIF, including a 300 ms recovery hold on the final pose.
- The decisive diagonal strike is source frame 499 (sprite frame 19), where the projected blade turns 121.7° in one source frame. The original-gradient `WeaponLight` starts on this strike and fades through sprite frame 25.

## Stability changes

- Fit the initial painted pose 75% toward the first Rokoko pose, then apply subsequent native-frame deltas.
- Keep the same projected support foot (left) throughout the sequence, with a single shared +10 px raster correction. All 32 measured sole baselines have 0 px error.
- Limit painted limb segment ratios to 0.78–1.12× their source lengths. The GIF uses a shared palette without frame dithering.
- Keep `WeaponLight` as its own full-canvas transparent frame set. The pose layers remain separately selectable under `layers/`.

## Review files

- [Rokoko-to-paint comparison contact sheet](review/rokoko-vs-swordsman-contact-4x8.png)
- [Rokoko-to-paint comparison GIF](review/rokoko-vs-swordsman-one-shot.gif)
- [Painted one-shot GIF with trail](review/basicattack-se-rokoko-research-surface-with-trail-one-shot.gif)
- [Painted 32-frame contact sheet](review/basicattack-se-rokoko-research-surface-contact-4x8.png)
- [Layered contact sheet with trail](review/basicattack-se-with-path-trail-layered-4x8.jpg)
- [Pose, root, and weapon audit](review/basicattack-se-rokoko-research-surface-provenance.json)
- [WeaponLight path and timing audit](review/weaponlight-path-provenance.json)

## Remaining failures

- The source template begins in a different, more crouched pose than the guide. The pose fit narrows that gap, but some body and hand landmarks still diverge.
- Source art is only 320 px and visibly softer than the owner-supplied reference. It is not the final painted master.
- The right hand/grip needs a clean, stable glove silhouette. The cape remains fused into `Outfit`, and there is no reconstructed hidden surface for equipment swaps.
- The trail follows the actual blade sweep and starts on contact, but it still covers too much of the torso. Its shape and opacity need another paint review.
- Only SE exists. Other directions, in-game preview, and owner review are not complete.

Keep this iteration as an internal stability and motion-alignment study. Do not package it as production artwork.
