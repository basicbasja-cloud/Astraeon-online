# Original art studies — not production approval

Generated using the built-in image generation tool on 2026-10-09 and 2026-10-10. RO1 source pixels
remain in ignored private reference storage and are not part of these images.

1. `turnaround-camera-rejected.png`: initial eight-view rebuild. Prompt used actual
   RO1 Idle for anatomy/directions and historical ASTRAEON art only for costume and
   identity. Rejected internally because the camera was too level.
2. `turnaround-candidate.png`: camera correction to an elevated orthographic RO1
   view, compact proportions, same original costume. Some pixels crossed declared
   grid boundaries; not suitable for fixed-cell production export.
3. `turnaround-padded-candidate.png`: requested generous transparent padding and
   preserved eight-view order/costume/camera. This source passes the shared normalizer
   using `neutral-normalization.json`. This establishes a neutral art study only.
4. `south-keypose-study.png`: six complete original body/head/sword study poses,
   prompted against actual assembled South RO1 attack and raw RO1 body silhouettes:
   ready, anticipation, acceleration, contact, follow-through, recovery. This is
   not a final animation or separated part atlas. It crosses some source cell
   boundaries and the follow-through/recovery trajectory still needs review.

No geometric limb warps or source pixels from the rejected character candidates
are inputs to the new neutral art. Existing costume design is a visual identity
reference, not reused pose geometry. Generation prompts emphasized connected
shoulder/elbow/wrist anatomy, stable limb proportions, actual visible sword grip,
one-handed overhead motion and original imagery with no copied RO costume/pixels.

All studies remain OWNER VISUAL APPROVAL PENDING. The final full production master,
separated part atlases, all eight attacks and Walk are still to be authored and
validated. Do not label the neutral turntable as completed attack animation.

## Additional original studies

- `body-neutral-candidate.png` and `head-neutral-candidate.png` are newly generated
  parts, not exact masked extractions. Their original placement differed and the
  neutral-fit configuration records the authored registration. Head includes hair.
- `contact-board-rejected.png` has direction and sword-hand errors.
- `contact-guide-painted-candidate.png` follows the original derived 3D guide but
  still has a Southeast hand error. `contact-guide-painted-v2.png` corrects that
  specific hand ownership; it is an identity/pose reference, not a finished atlas.
- The attempted 48-pose generation produced only seven rows and was rejected.
  Its generated-file identifier is `exec-2f268d31-46be-42a2-b514-42425ca9a10d`.
- `*-six-phase-candidate.png` are independent directional six-pose studies from
  this session. Northwest includes a targeted correction to hide the far sword
  arm at impact rather than switching to the near empty arm.
- `northeast-six-phase-padded.png` and `southeast-six-phase-padded.png` supersede
  their corresponding candidate sheets for review export, fixing cross-cell
  blades. They are newly generated layouts, not guaranteed pixel-preserving edits.

`attack-study.json` records the chosen sources, uniform scales/origins and explicit
held-pose mapping to the shared 450 ms BasicAttack clock. The review receipt records
source SHA256 hashes, exact extraction rectangles, pixel hashes and bounded alpha
noise cleanup. Sources remain unchanged. No rejected limb warp or old WeaponPoseSet
was used to create these studies.

The animation is combined art. A clean export does not establish correct painted
anatomy, stable feet, exact facing, correct blade trajectory or modular swapping.
The production master remains unfinished and unapproved.

## Generation specification / prompt set

Tool: built-in image generation, transparent-background mode. Each direction was
requested separately as six complete original sprites on a 1536×1024, 3×2 sheet.
References: actual private RO1 rendered attack captures for compact anatomy and
motion; the original gold-armoured/silver-haired contact study for identity;
original VISUAL_DERIVED projection guides for missing distinct view planning.
RO source pixels are reference inputs only and are not packaged as original art.

Common request: original ASTRAEON gold armour, cream split tunic, teal neck scarf,
brown trousers, gold boots, silver/lavender hair; crisp RO1-like painted sprite
readability, elevated orthographic camera; connected shoulder/elbow/wrist and closed
right-hand grip; ready, anticipation, acceleration, contact, follow-through and
recovery in reading order; fixed feet registration and uniform scale; transparent
padding; no slash, ground shadow, labels, glow or extra figures.

Direction-specific instructions:

| Direction | Projection and ownership instruction |
| --- | --- |
| S | Front/down, sword arm originates screen left, blade descends in front |
| SW | Front three-quarter/down-left; maintain the same anatomical sword hand |
| W | Left profile; blade starts behind the head toward screen right, then cuts down-left |
| NW | Rear three-quarter/up-left; right shoulder screen right; impact arm hidden on far side, near left arm stays empty |
| N | Straight back; right arm screen right, impact mostly hidden by body/head |
| NE | Rear three-quarter/up-right; near right arm cuts down-right |
| E | Right profile; near right arm, blade initially left then down-right; independently rendered rather than mirrored |
| SE | Front three-quarter/down-right; right arm starts screen-left shoulder and crosses in front to lower-right grip |

Targeted padding prompt for Southeast: recreate all six at approximately 60% source
scale inside central 300×300 regions of 512px cells, generous transparent gaps,
preserve relative anatomy, phases, hand ownership and complete swords. The tool
did not guarantee the requested coordinates; the explicit review registration
records what was actually consumed.
