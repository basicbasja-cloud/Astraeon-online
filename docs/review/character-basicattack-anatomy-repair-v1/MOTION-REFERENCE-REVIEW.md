# Anatomy and motion reference review

Status: **OWNER VISUAL APPROVAL PENDING**. This is a visual comparison, not a biomechanics certification or a claim of exact RO ACT timing.

The owner requested this check before the final checkpoint. The assembled attack was reviewed without attachments first, then with Head, Hair, sword and Cape, at native frame indices and normal/half speed. Anticipation, acceleration, contact, immediate follow-through and the return were checked across S, SW, W, NW, N, NE, E and SE.

## References actually inspected

- The retained [RO1 rendered-reference manifest](../../../authoring/characters/motion-templates/ro1-swordsman-male/rendered-reference.json) and newly reacquired nine-frame attack sequences, action80+direction, sword view2, from [ragassets](https://assets.latam-tools.com.br). Decoded frames match the checkpoint hashes in every direction: [reinspection receipt](ro1-reinspection.json). This renderer repeats adjacent direction outputs (S/SW, W/NW, N/NE, E/SE); it provides four distinct projected sequences, not eight independent anatomical measurements. ASTRAEON retains eight independent painted directions. Raw ACT files were not inspected. Reference imagery stays in the ignored private research folder and never enters runtime or committed review artwork.
- Vincent's actual one-handed sidesword cut, [Dissecting a cut](https://blog.subcaelo.net/ensis/dissecting-cut/), including the animated demonstration, phase observations and published tracked-angle data. The demonstration was visually inspected through browser captures. It supports a raised preparation, extension through a descending arc, continued movement after the impact position and active deceleration. It is one practitioner's cut, not a universal template. Its real timing was not imposed on this game's 450ms presentation.
- Thorsten Renk's [Cutting mechanics](https://science-and-fiction.org/swordfighting/cuts.html), which reports filmed cuts and distinguishes preparation, acceleration, travel through impact and deceleration. This supplies a phase-order check, not a source for ASTRAEON joint coordinates or game timing.
- The owner's Alchemist Swords sheet, SHA256 `d29efbef479addd6730971d574dcd0e5aa1878d6d9842de0322eb255c1a784aa`, was inspected after the initial body painting pass. It contains separate weapon orientations, grip gaps in some views, and separate slash-effect wedges/arcs at the bottom. The PNG alone does not establish ACT placement, frame order or delays. No RO weapon or effect pixels were imported.

## Comparison and corrections

| Phase | Motion-reference observation | ASTRAEON check and result |
| --- | --- | --- |
| Ready / anticipation, 0–5 | Raised hand with a bent elbow; stance and torso establish the cut before extension. | Existing good poses remain; SW/W loading arms were repainted where shoulder/elbow structure was compressed. Head identity and stance pixels outside the limb masks remain original. |
| Acceleration, 6 | Shoulder, elbow and hand continue one connected chain; fast motion does not excuse an extra or detached limb. | NE6's extra glove/arm was removed. Assembly inspection caught SW6's painted sword arm passing through the skull/hair and leaving a detached-looking blade. A further arm painting exposes a continuous ivory upper arm and bent elbow outside the skull; the body pose is repaired before registering the sword. |
| Contact, 7 / 170ms | The blade travels through the cutting plane; the hand remains attached to the same arm and hilt. | All eight contact arms have localized new paintings. SW7 and NW7 now have their own painted arms instead of borrowing frame8's arm. The hilt follows the painted palm, with an opening in our own weapon artwork and foreground body fingers. |
| Immediate follow-through, 8–11 | The cut continues in the same direction while the limb starts to bend/decelerate; it does not become a separate thrust or reverse at impact. | SW/W/NW extension and elbow progression were re-authored. W10 and W11 now have distinct arm painting. Other retained good source phases were inspected in sequence. |
| Recovery, 12–15 → 0 | Recovery bends and returns the same arm; returning the weapon alone cannot hide a waist-held body hand. | New painted raised return arms in14/15 replace the waist-held tail in every direction. Owned swords return to the ready angle and ready view. The original torso, head and stance remain: their last-to-first changes are still a limitation for owner review. |

The broad action grammar remains the RO-derived overhead/diagonal cut. The painted retarget uses ASTRAEON's anatomical right hand and its own proportions; this is not pixel-for-pixel or angle-for-angle reconstruction. A fast 6→7 hand displacement is checked as acceleration, while the overlay's 2D lengths are treated as projected estimates, especially for rear-view occlusion.

The review found and corrected a visible SW6 defect before final packaging. It does **not** establish owner approval. Remaining questions include arm volume/seams in slow close-up and the retained torso/stance transition at the attack loop boundary. The focused owner GIF and body-only strips are the acceptance evidence; numeric pivot checks cannot certify anatomy.

## Scope preserved

MotionTemplate, durations, direction identities, contact marker, gameplay state and engine code are unchanged. Only BasicAttack arm painting and downstream MainHand presentation metadata/owned hilt openings change. Head, Hair and Cape artwork remain original. FX remains an independent optional slot; no slash art is admitted to conceal anatomy.

The newly requested [sprite-gen skill](https://github.com/aldegad/sprite-gen/blob/9935d674128e512ea9727168252bb544e68c8f69/SKILL.md), version 2.43.0 at revision `9935d674128e512ea9727168252bb544e68c8f69`, is installed locally for this project. Its independent `inspect-motion` command reads the exact 16-frame descriptors and original millisecond durations. It supplies duplicate/bounds/timing evidence and does not rewrite frames, mirror directions or certify anatomical realism. Earlier arm generation and surgical mask integration use this project's native authoring tools, not sprite-gen's generation pipeline.

All eight inspector reports retain `needs-review`: planted-foot contact/stride was not supplied or certified. Six directions retain the existing identical frame4/frame5 loading hold; SW has a near-silhouette hold and W has no exact duplicates. No frame or duration was removed. All 128 assembled frame bounds stay inside the source canvas. The final frame13→14 recovery remains brisk, and the preserved stance changes across frame15→0 remain visible. These findings are retained in the report rather than converted into a visual pass.
