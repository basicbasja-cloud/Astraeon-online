# BasicAttack motion reset, iteration 24

## Decision

The Rokoko `SwordFight_mixamo.fbx` segment at source frames 480–511 is rejected as the BasicAttack paint guide. Its fixed-camera guide reads as raising and lowering the sword; the trunk and feet barely support a strike. Do not repaint the previous 32-pose art against that segment.

The owner identified the OpenGameArt `Sword Attack I` and `Sword Attack II` motions as attacks. Both were compared from fixed Blender cameras. `Sword Attack II` has the clearer lateral cut and is the current **motion study**; `Sword Attack I` remains a secondary attack candidate. These motions are from the OpenGameArt Lowpoly Dummy Character CC0 package already recorded in `motions/legal-evidence/opengameart-lowpoly-dummy-character.html`.

## Evidence

- [Sword Attack I, 12-sample comparison](review/oga-sword-attack-i-motion-contact.png)
- [Sword Attack II, 32-pose fixed-camera contact](review/oga-sword-attack-ii-motion-contact.png)
- [Sword Attack II, one-shot motion GIF](review/oga-sword-attack-ii-motion-one-shot.gif)
- [Sword Attack II, alternate three-quarter camera GIF](review/oga-sword-attack-ii-alternate-camera-one-shot.gif)
- [Alternate camera 32-pose contact](review/oga-sword-attack-ii-alternate-camera-contact.png)
- [High-detail contact paint probe, rejected](review/contact-paint-probe-rejected.png)

The Sword Attack II review samples source frames 1–50 at 32 even intervals using a fixed orthographic camera, Blender Workbench, and a 5.2 orthographic scale. Its GIF plays the 31 motion intervals at approximately 30 fps and holds the final pose for 300 ms. This is a motion diagnostic, not a layered or runtime sprite.

The alternate camera, positioned on the other three-quarter side, keeps both boots visible and the sword tip inside the frame throughout the 32-pose review. It is a stronger pose guide than the first camera, where the legs overlap. The source motion's torso and foot action still needs a native-size animated review before artwork is approved.

The paint probe has a complete blade after a wider guide capture, but it changes the 3D pose, has red/yellow edge fringes, and is not an approved master. No new production art, cutout set, trail, eight-direction action, or target-map preview is accepted from iteration 24.

## Next gate

Select the angle and full-body motion that keep both legs readable, body weight transfer credible, and the complete sword inside the capture. Then create exact-pose high-resolution art for adjacent attack poses and confirm that costume, body, glove back, sword axis, and cape stay coherent in an animated comparison before cutting layers or drawing the trail. Maintain `WeaponLight` as a separate effect following the painted sword path.
