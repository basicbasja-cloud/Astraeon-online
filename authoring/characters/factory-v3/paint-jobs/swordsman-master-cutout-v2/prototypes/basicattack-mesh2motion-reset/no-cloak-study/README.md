# No-cloak registration study

Owner permits omitting the long cloak when it reduces animation quality. Retain the short gold scarf. This study uses the canonical fixed SE camera, not the earlier approximate SE camera.

`SE-000-guide-white.png` is the canonical Mesh2Motion B frame 0 composited over white without moving or scaling its visible pixels. `SE-000-paint-v1.png` is an original no-cloak illustration study, not production animation or separated equipment.

Visual review: the long cloak is removed cleanly and the costume is legible, but the raised hand and sword are too high relative to the guide. The illustration must not be promoted to a motion-registered master. Removing the cape alone does not solve pose registration or establish temporal stability.

No runtime files are replaced by this study. The source rig and its 60 fixed-camera poses remain authoritative.

## Result of the no-cloak follow-up

Three illustrations were produced: raised guard v1, corrected guard v2, and low follow-through frame 15. Prompt and output provenance is recorded in `complete-generation-provenance.json`. The white guides use the canonical fixed SE camera.

Manual approximate sword annotations after one whole-canvas scale to 1024 show:

| Candidate | Grip error | Tip error | Decision |
| --- | ---: | ---: | --- |
| Guard v1 | 54.64px | 65.82px | Reject for registration |
| Guard v2 | 13.84px | 38.86px | Reject for registration |
| Downstroke follow-through | 120.91px | 91.53px | Reject for registration |

See `registration-review.png` and `registration-audit.json`. The measurements are manually annotated, not an automated anatomical detector. These are pose studies, not animation frames approved for production. A two-frame dissolve or interpolated GIF would conceal neither the incorrect joint placement nor costume drift; no such animation is presented as completed work.

The corrected guard has editable visible cutouts in `editable-cutouts/swordsman-no-cloak-study.ora`: HeadHair, Weapon_VISIBLE_ONLY, and BodyOutfit_UNSEPARATED. Their disjoint original visible pixels recompose to the transparent master with **0 mismatched pixels**. The packaging script rejects annotation canvas mismatches. Clothing and body are still combined; hidden surfaces are not supplied. This is an editable study, not complete interchangeable equipment or a validated animation rig.

Current blocker: independent illustrated generation does not reliably preserve the exact registered source pose, even with numeric landmark constraints and no cloak. Expanding this route to 60 frames would reproduce the reported instability. A source-registered drawing/texture workflow must replace independent frame generation before a final smooth animation can be claimed.
