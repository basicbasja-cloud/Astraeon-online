# BasicAttack SE, iteration 17

## Review status

**Review only; not approved for runtime.** This is the current stability and sword-alignment candidate. Two-bone IK keeps the sword hand on the Rokoko path while holding limb proportions constant. The art and full-body motion still need a high-resolution repaint.

## Motion and timing

- Guide: [iteration 14, 32 native Rokoko frames](../basicattack-se-iteration-14/source/rokoko-blender-guide/review/rokoko-basicattack-se-guide-4x8.png)
- Source: `SwordFight_mixamo.fbx`, frames 480–511 at 30 fps.
- The non-looping review GIF is 1,320 ms and holds source frame 511 for the final 300 ms recovery.
- The strongest blade turn is 121.7° between source frames 498 and 499. `WeaponLight` appears at sprite frame 19/source frame 499, then fades through frame 25.

## Stability and motion alignment

- The initial research pose is fitted 75% toward the first Rokoko pose; all later poses use the matching native source-frame delta.
- Two-bone IK holds every painted segment at 1.12× its fitted source-pose length for all 32 frames.
- The same left support foot anchors the clip. A shared +10 px raster correction leaves 0 px measured sole-baseline error in every frame.
- Sword-hand position error averages 0.05 px and peaks at 0.81 px. The support foot error is 0 px. The other hand still misses by up to 19.41 px because the research template's left arm is too short; the non-support foot misses by up to 6.71 px.
- Small exposed skin pixels below the boot silhouettes are removed from the visible base layer while covered skin remains beneath the outfit.
- GIF frames use one shared color palette without dithering to avoid palette shimmer.

## Review files

- [Rokoko and painted animation side by side](review/rokoko-vs-swordsman-one-shot.gif)
- [32-frame comparison contact sheet](review/rokoko-vs-swordsman-contact-4x8.png)
- [Painted one-shot with the separate trail](review/basicattack-se-rokoko-research-surface-with-trail-one-shot.gif)
- [Painted contact sheet](review/basicattack-se-rokoko-research-surface-contact-4x8.png)
- [Layered trail contact sheet](review/basicattack-se-with-path-trail-layered-4x8.jpg)
- [Pose, root, and reach audit](review/basicattack-se-rokoko-research-surface-provenance.json)
- [Trail frame and timing audit](review/weaponlight-path-provenance.json)

## Remaining failures

- The 320 px research art remains visibly softer than the owner reference. Pose fitting narrows the starting-pose gap but the torso, non-sword arm, and cape still do not match the Rokoko guide closely enough.
- The trail follows the real blade sweep and stays off the face, but its 28 px crescent still covers too much of the chest and tunic.
- Cape motion is not a separate painted surface; `Outfit` still contains the cape. Concealed surfaces and a clean swappable glove/hand are not complete.
- Only the SE view exists. Other directions, equipment-swap previews, in-game/map preview, and owner approval remain open.

Do not ship this iteration or treat its cutouts as final artwork.
