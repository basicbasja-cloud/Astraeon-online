# BasicAttack motion reset, iteration 24

## Decision

The Rokoko `SwordFight_mixamo.fbx` segment at source frames 480–511 is rejected as the BasicAttack paint guide. Its fixed-camera guide reads as raising and lowering the sword; the trunk and feet barely support a strike. Do not repaint the previous 32-pose art against that segment.

The owner identified the OpenGameArt `Sword Attack I` and `Sword Attack II` motions as attacks. Both were compared from fixed Blender cameras. `Sword Attack II` has the clearer lateral cut and is the current **motion study**; `Sword Attack I` remains a secondary attack candidate. These motions are from the OpenGameArt Lowpoly Dummy Character CC0 package already recorded in `motions/legal-evidence/opengameart-lowpoly-dummy-character.html`.

The owner subsequently specified a **top-down slash with visible body weight transfer**. Sword Attack II is a lateral cut and therefore no longer the target BasicAttack motion. The search below is open; no overhead clip has passed yet.

## Evidence

- [Sword Attack I, 12-sample comparison](review/oga-sword-attack-i-motion-contact.png)
- [Sword Attack II, 32-pose fixed-camera contact](review/oga-sword-attack-ii-motion-contact.png)
- [Sword Attack II, one-shot motion GIF](review/oga-sword-attack-ii-motion-one-shot.gif)
- [Sword Attack II, alternate three-quarter camera GIF](review/oga-sword-attack-ii-alternate-camera-one-shot.gif)
- [Alternate camera 32-pose contact](review/oga-sword-attack-ii-alternate-camera-contact.png)
- [High-detail contact paint probe, rejected](review/contact-paint-probe-rejected.png)
- [CC0 Sword Charge Attack, 32-pose fixed-camera contact](review/oga-sword-charge-attack-motion-contact.png)
- [CC0 Sword Charge Attack, one-shot review GIF](review/oga-sword-charge-attack-motion-one-shot.gif)

The Sword Attack II review samples source frames 1–50 at 32 even intervals using a fixed orthographic camera, Blender Workbench, and a 5.2 orthographic scale. Its GIF plays the 31 motion intervals at approximately 30 fps and holds the final pose for 300 ms. This is a motion diagnostic, not a layered or runtime sprite.

The alternate camera, positioned on the other three-quarter side, keeps both boots visible and the sword tip inside the frame throughout the 32-pose review. It is a stronger pose guide than the first camera, where the legs overlap. The source motion's torso and foot action still needs a native-size animated review before artwork is approved.

The paint probe has a complete blade after a wider guide capture, but it changes the 3D pose, has red/yellow edge fringes, and is not an approved master. No new production art, cutout set, trail, eight-direction action, or target-map preview is accepted from iteration 24.

## Overhead motion search (21 October 2026)

- Downloaded the same author's [OpenGameArt CC0 Lowpoly Dummy Character Sword Charge Attack](https://opengameart.org/content/lowpoly-dummy-character10-animations) from its documented direct ZIP. The raw FBX is `motions/raw/oga_sword_charge_attack/Lowpoly Dummy Character Sword Charge Attack.fbx`, SHA-256 `b7fd93fdff47b2f3e11d271af42444f5ea81093270d87268db49d0257e36071b`. **Correction after inspecting all 85 source frames:** this is one overhead charge followed by a real spinning strike, an extended follow-through, and recovery. The initial 32 evenly spaced frames over-emphasized its long wind-up and follow-through holds. The decisive slash and spin occupy approximately source frames 45–55. This is a viable **spinning heavy attack study**, not merely a raised-sword pose. Its jumping/rotating support needs a separate decision before using it as the ordinary BasicAttack.
- Reviewed the repository's CC0 Quaternius `swordAttackJump` motion. The body rises and pitches forward, but the available character clip has no registered blade, so the sword arc and hand grip cannot be validated as a single motion. **Not selected.**
- A broader Rokoko fight source scan found torso movement outside frames 480–511, but the segment around frames 257–321 combines a lift/lower with several unrelated actions, and its sword is only a wrist-derived proxy. **Not selected.**
- [MoCap Online's free T.C. Sword pack](https://mocaponline.itch.io/free-3d-sword-animation-pack) lists a 55 MB ZIP with FBX among its formats. Its motion is a priority for a real-performer comparison once the pack is downloaded and the actual clips can be reviewed. The site listing alone does not establish that a particular clip is a weighted overhead strike.
- [Adobe's Mixamo](https://www.mixamo.com/) is free with an Adobe ID according to [Adobe's FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html). Search its sword-slash motions and inspect the actual FBX and sword grip before selecting one. A catalog name is not a motion pass.

### Corrected Sword Charge review

- [34-pose trimmed spin one-shot GIF](review/oga-sword-charge-trimmed-spin-one-shot.gif)
- [Selected source-frame contact sheet](review/oga-sword-charge-trimmed-spin-contact.png)

The 34-pose review retains original source poses in chronological order, samples the motion densely at 45–58, and skips redundant holds before and after the strike. It plays 33 ms per pose with a 250 ms recovery hold. It does not change the underlying FBX curves and is not yet an approved production animation. The sword follows the actual attached weapon through the spin; pose-painted glove, support-foot contact, trail direction, and native-size timing still require review.

## Next gate

Select the angle and full-body motion that keep both legs readable, body weight transfer credible, and the complete sword inside the capture. Then create exact-pose high-resolution art for adjacent attack poses and confirm that costume, body, glove back, sword axis, and cape stay coherent in an animated comparison before cutting layers or drawing the trail. Maintain `WeaponLight` as a separate effect following the painted sword path.
