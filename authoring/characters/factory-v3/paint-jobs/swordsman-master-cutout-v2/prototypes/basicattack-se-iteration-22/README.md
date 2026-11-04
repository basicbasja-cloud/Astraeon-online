# BasicAttack SE, iteration 22

## Review status

**Review only; not approved for runtime.** This is the most stable pose-following study so far. It replaces a 32-pose 30 fps preview with 63 actual Blender samples at 60 fps, using half-frame samples from the same Rokoko FBX. The contact point, trail timing, and body art still need owner review; the art quality remains below the supplied reference.

## Motion and registration

- Source: `SwordFight_mixamo.fbx`, frames 480–511 at 30 fps, sampled every 0.5 source frames. Blender evaluates the original animation at subframes; no painted poses are duplicated or interpolated.
- Only the review guide and projected landmarks are included; the raw FBX remains local. Rokoko's source-page terms and the missing receipt/license-file note are recorded in [motion license evidence](../../../../motions/legal-evidence/rokoko-13-free-fight.md).
- The SE one-shot has 63 poses, a 1,330 ms GIF duration, and a 300 ms final recovery hold. It does not loop.
- A single left support foot anchors the entire clip. The same +10 px raster correction gives 0 px sole-baseline error in all 63 frames.
- Two-bone IK follows the previous-frame solution and adapts projected segment lengths within 0.78–1.12× the master lengths. Head/neck/waist maximum step is 1.05/0.96/0.93 px; knees are 1.17/1.56 px. The right sword hand reaches its target exactly. The right elbow still has a 14.52 px maximum step at 60 fps.
- The non-sword hand misses its Rokoko target by up to 16.82 px; the non-support foot misses by up to 10.40 px because the donor art proportions do not match the source rig.

## Trail

- `WeaponLight` stays in its own transparent layer and follows the sword proxy's actual 2D path.
- Consecutive high-speed samples are grouped into one downward strike: the trail begins at sprite frame 37/source frame 498.5, reaches a 28 px maximum width at frame 38/source frame 499, and fades through frame 49.
- The plum-gray, lavender-silver, and warm-ivory gradient is original. The trail stays behind the face and sword, but still covers too much of the chest and tunic.

## Review files

- [Painted one-shot with trail](review/basicattack-se-rokoko-research-surface-with-trail-one-shot.gif)
- [Rokoko and painted one-shot side by side](review/rokoko-vs-swordsman-one-shot.gif)
- [63-frame comparison contact sheet](review/rokoko-vs-swordsman-contact-4x16.png)
- [Strike sequence close-up](review/rokoko-vs-swordsman-strike-detail.png)
- [Consecutive 497.0–497.5 elbow-step close-up](review/elbow-transition-497-to-497p5.png)
- [Painted contact sheet](review/basicattack-se-rokoko-research-surface-contact-4x16.png)
- [Separate WeaponLight sheet](layers/WeaponLight/weaponlight-se-4x16.png)
- [Motion and limb audit](review/basicattack-se-rokoko-research-surface-provenance.json)
- [Trail timing and path audit](review/weaponlight-path-provenance.json)
- [Blender guide contact sheet](source/rokoko-blender-guide/review/rokoko-basicattack-se-guide-4x16.png)
- [Research donor layers and pose landmarks](source/research-template/)

## Remaining failures

- The research donor is only 320 px and is visibly softer than the owner's high-resolution fantasy reference. The torso, non-sword arm, and cape still differ from the Rokoko pose.
- The cape is baked into `Outfit`; hidden surfaces and a swappable hand are incomplete.
- The broad trail still obscures too much of the torso. Only the SE view exists; equipment-swap and in-game/map previews have not passed review.

Do not ship this iteration or treat its cutouts as final artwork.
