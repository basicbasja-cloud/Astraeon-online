# BasicAttack SE, iteration 23

## Review status

**Rejected for character continuity and weapon alignment; not approved for runtime.** This study has 32 high-resolution full-character paintings on a Rokoko SE action. The output root is numerically registered, but the independently painted poses change costume and silhouette shape, and the sword does not follow the Blender proxy consistently. Semantic character cutouts are not present.

## Motion and registration

- Source: Rokoko `SwordFight_mixamo.fbx`, frames 480–511, sampled from the self-contained Blender guide in `source/rokoko-blender-guide/`.
- The one-shot review uses 32 poses, preserves source timing, runs for 1,330 ms, and holds the recovery pose for 300 ms.
- Output frames are 1280×1280 at root `(640,1056)`, which maps to `(160,264)` in the 320px motion-guide cell. The requested visible head-to-floor target is 600 px.
- The normalizer independently scales each painted frame to the corresponding Rokoko guide. Painted source head-to-floor measurements range from 790 to 1,186.5 px and scale factors range from 0.5284 to 0.8177. The final root coordinate is shared, but this normalization does not correct the underlying changes in body proportions and pose.
- Anchoring every image to its screen-right shoe was tested in `experiments/support-foot-anchor-001/`; it shifts the assembled figure left in the cell and is not accepted.

## Weapon and trail findings

- The original full-character set has a clear directional pop at source frame 498.5: frame 498.0's sword is approximately −43° and matches the wind-up guide, while the original frame 498.5 sword points almost vertically down instead of following the Rokoko proxy at about +11°.
- A guide-based 498.5 paintover corrects the sword direction, but also changes the cape and full character silhouette. Comparable paintovers at 498.0 and 499.0 still miss their guide sword angles. The three-frame comparison is in `experiments/guide-painted-multi-frame-001/`.
- `WeaponLight` exists as its own transparent layer, with an original plum-gray, lavender-silver, and warm-ivory gradient. The current ribbon follows the iteration-22 research weapon path, not the sword painted into these iteration-23 frames. In the composite it floats above and to the side of the character. It is rejected until the sword art and effect use the same per-frame weapon path.

## Latest continuity work (2026-10-20)

- [Continuity normalization 002](experiments/continuity-normalization-002/README.md) re-runs all 32 raw poses on the 1280px canvas at root `(640,1056)`. The head-to-floor output is exactly 1.1× the corresponding guide measurement in every frame; no frame is canvas-scale-limited. This fixes frame-size jumps caused by the previous canvas margin.
- The new registration result is still **NOT APPROVED**. Its source paintings have scale factors from `0.505962` to `0.819327`, and direct visual review still shows body-pose mismatches at the lead-in and strike plus cape-shape changes. Stable root and matched height do not establish pose or character continuity.
- [Guide-locked four-pose probe](experiments/guide-locked-four-pose-001/README.md) improves costume and identity consistency across four key poses. The exact guide match is partial, the sword is omitted, and it does not cover the in-between frames. A separate 480–483 test collapses four small motion changes into one repeated drawing and is rejected.
- Continue from one stable character master with pose-matched registered layers or a deformation method that passes visual review. Do not use the current 32-frame normalized paintings or four-pose probe as runtime art.

## Review files

- [32-frame one-shot GIF](review/basicattack-se-one-shot.gif)
- [32-frame painted contact sheet](review/basicattack-se-normalized-contact.png)
- [Rokoko guide versus painted contact sheet](review/basicattack-se-guide-comparison.png)
- [Painted sequence with the current trail overlay](review/basicattack-se-with-path-trail-over-4x8.jpg)
- [Layered sequence with the current trail](review/basicattack-se-with-path-trail-layered-4x8.jpg)
- [Normalization audit](review/normalization-audit.json)
- [Latest 32-frame continuity audit](experiments/continuity-normalization-002/review/continuity-audit.json)
- [Guide-locked four-pose comparison](experiments/guide-locked-four-pose-001/normalized/review/basicattack-se-guide-comparison.png)
- [Separate sword layer proof](experiments/weapon-layer-proof-001/README.md)
- [Trail pose audit](source/trail-input/weaponlight-pose-audit.json)
- [32 selected Blender guides](source/rokoko-blender-guide/motion-guide-manifest.json)
- [Painted 498.0 / guide paintover 498.5 / painted 499.0 comparison](experiments/guide-painted-multi-frame-001/review/guide-paintover-498p5-adjacent-frames.png)
- [Screen-right shoe anchoring trial](experiments/support-foot-anchor-001/review/basicattack-se-normalized-contact.png)
- [Guide paintover source and review record](experiments/guide-painted-multi-frame-001/provenance.json)

## Required replacement work

1. Establish one high-resolution character master and preserve its body, costume, and palette through the action.
2. Paint or deform registered cutouts against each matching Blender frame; keep `HeadHair`, body/outfit, `Weapon`, and `BackAccessory` independently editable.
3. Keep a shared scale and root for the complete action. Verify the planted support foot and head/torso landmarks in the animated view.
4. Measure the painted sword pivot, axis, and tip against each matching Rokoko guide. Generate the separate `WeaponLight` from that same painted blade path and keep its broad section thick and early without crossing the character.
5. Recheck the full-resolution contact sheet and one-shot GIF, then recompose the cutouts and inspect them in the target game map before any production approval.

See the [production status](../../../../../../../docs/character-factory/PRODUCTION_FACTORY_V3_STATUS.md) and [V3 swordsman master prompt](../../../../identities/swordsman_master_prompt_v3.txt) for progression and authoring requirements.
