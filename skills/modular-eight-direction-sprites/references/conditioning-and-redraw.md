# From motion research to a drawable sprite contract

Iteration 7, 2026-10-11. The user explicitly allows any useful game, indie project, GitHub implementation or animation research. RO remains an inspiration; the original game's own style determines final appeal. The goal is correct poses first, then drawing over them. Source selection is based on usefulness, not resemblance alone.

## Read sources and what they change

[HandRefiner](https://arxiv.org/html/2311.17957v2), selected method/ablation/limitations sections: a sparse skeleton does not resolve hand depth and occlusion. Reconstructed hand depth plus conditional inpainting improves its evaluated images, but generic depth conditioning can still distort wrists. Very small hands and complex occlusion remain problematic. Its evaluated settings do not establish a universal strength value for our stylized sprites. No model was executed here.

[Giving a Hand to Diffusion Models](https://arxiv.org/html/2403.10731v2), §§III and V: generates hands before body outpainting and uses segmentation/mask expansion to join the regions. It explicitly needs arm–wrist connectivity and substantial hand image area; small hands and lossy latent conversion reduce detail. This suggests reviewing a grip in a larger detail view while retaining its whole-arm relationship. It does not prove our tiny drawn glove is correct. No model was executed here.

[Generative Cutout Animation](https://www-labs.iro.umontreal.ca/~bmpix/pdf/PAPER_CUTOUTS.pdf), selected §§3–5 and Figures 5–8, 11–14: inconsistent generated pose targets can make cutout optimization blur or lose opacity. Multi-pose consistency and boundary treatment matter. Its rigid cutouts use fixed depth order; dramatic perspective rotations need replacement pieces and are outside its demonstrated method. Hands/feet can still be anatomically wrong, and permanently hidden pieces can acquire incorrect content. Therefore this is a useful layering study, not a complete eight-view or hidden-part solution. PDF was read, not executed.

[ControlNet's author repository](https://github.com/lllyasviel/ControlNet) documents image-space condition types. Our current image tool does not expose those ControlNet weights/settings. A future backend must declare its actual supported controls and encoding, then demonstrate correspondence on our proportions. Do not label a prompt attachment an enforced skeletal constraint.

The [pinned LPC implementation audit](conditioning-source-audit.json) inspects renderer/preview/custom-animation/z-positioning code and one repository-local skill. It provides explicit four-row animation mappings, sorting by `zPos`, enlarged weapon cells and an 8 FPS preview loop. Its preview FPS is a tool choice, not a rule for RO or our attacks. Four cardinal rows are not eight oblique views. A single layer order cannot solve every crossed-arm overlap. We read selected code; did not run or import its renderer/art. Its local skill's user-testing instructions apply to edits in that repository, which we did not make.

## New measured guide output

Run `scripts/export-conditioning.py` against a verified completed review build. It reads the existing original unapproved rig proof and publishes into a **new separate directory**, keeping that build immutable. It uses no external character pixels. Each of 64 attack keys has:

- Skeleton and FX-off composite at native 128 × 128, using the actual source guide/camera.
- Full 256 × 256 silhouette, integer visible render-piece ID map and 16-bit packed depth. All use the same 2× coordinate relationship. No bounding-box fitting, mirroring or per-frame depth normalization.
- A diagnostic grip enlargement with its native source rectangle recorded. This detail crop never replaces the full logical animation cell.
- Pose duration, anatomical right-hand ownership, source hashes and unresolved release gates.

Silhouette, part ownership and depth support are checked against each other for every key. These are useful shape/occlusion controls. They do not detect a malformed final drawing, establish finger anatomy or certify motion appeal. `gloves.brown` contains both gloves: its integer part ID is **not** an anatomical left/right surface ID. The skeleton carries ownership; a future articulated hand guide must supply reviewed palm/finger geometry separately.

Depth has a fixed camera-space range of 0–8 units. Background is zero; valid depth is `round((1-z/8)*65534)+1`, nearer brighter. An actual backend may require a different depth convention or bit depth; adapt explicitly while preserving a common range across the whole strip. Don't present this PNG as a plug-and-play trained ControlNet input.

## Authoring sequence for our style

1. Choose a source action for **acting**, and record shot/time/projection/visibility limitations. Split camera cuts. Review every retained frame, not just the attractive hit exposure. External gameplay does not recover a source rig by itself.
2. Block the original character to its approved proportions. Record anatomical limb owners; right does not mean screen-right. Build sparse preparation, weight-load, launch, strike, follow-through and recovery poses. For locomotion, also author support, passing, swing clearance and root travel.
3. Approve rig/silhouette motion before styling. Review hip and chest rotation, support knee plane, counterbalancing arm, head response and planted vs released foot. Exact same bone lengths can still produce poor acting. Don't freeze both legs to stop registration errors.
4. Build the **hand around the particular hilt**, not around a generic fist. Keep a local wrist/palm frame, hilt axis, contact patch, thumb side and finger wrap. Separate one-hand, two-hand and shield grip families. Pose-space correctives or replacement drawings are appropriate at a difficult cross-body strike. A wrist/socket coincidence is insufficient.
5. Give the artist/generator the approved identity plus the complete ordered pose strip, silhouette, occlusion/depth evidence and a hand detail guide. Declare which controls are truly supported. Treat unsupported controls as reference requests and inspect the result accordingly. Never generate unrelated frames and later recenter them to hide drift.
6. Draw in the game's original style on the fixed canvas. Prioritize native-size silhouette, face, hand/hilt readability and consistent material clusters. Inspect torso and stance with FX off. Repair a failed region against its **same** guide, including neighboring joints, rather than allowing wrist-only fixes to break the forearm.
7. For assisted local repair, preserve the reviewed pixels outside a declared repair region by explicit composition and a pixel comparison if the editing tool can change them. Include elbow–wrist–palm–hilt context. Inspect the seam at the wrist, arm/torso overlap and adjacent frames after repair. Masking alone is not proof of preservation.
8. Finish separate **complete** body/head/hair/costume/armor/weapon source parts, including previously hidden content. A visually correct flattened strip is not modular output. Review alternate equipment on the same pose/view key and inspect visible overlap plus hidden-piece completeness.
9. Author blade-history trails only after FX-off anatomy passes. Show trail origin/tip in relation to the blade, emission phase, collapse/expiry, occlusion and cancellation. Body poses can remain sparse while FX exposures change on the same action clock.
10. Export on the shared timeline; validate alpha/depth composition, whole-character view mapping, swap continuity, atlas registration, bounds and actual game rendering. Mark visual approval separately from technical checks. Expand item counts only after one complete character family works at native size and in game.

## Reject or repair with a concrete reason

| Observed defect | Required evidence / correction |
|---|---|
| Apparent hand switch | Trace anatomical shoulder→elbow→wrist→palm→hilt; check view mapping, no mirroring. |
| Twisted glove or detached blade | Review palm orientation and hilt contact, not only joint distance. Repose/redraw the connected chain. |
| Bow-legged/sideways knee | Inspect hip–knee–ankle bend plane and foot lane in that view; revisit rig pose before texture cleanup. |
| Foot sliding | Measure stance contact relative to root/floor motion at game speed. Unknown gameplay camera motion cannot establish a zero-slide result. |
| Shaking silhouette/scale | Compare full registered strips and loop boundary; fix source or redraw. Do not align changing bboxes independently. |
| Hidden hair/body missing after swap | Inspect complete isolated source items and extreme-pose swaps; repaint/remodel hidden material. |
| Trail hides the hand/body | Review FX off, shorten/reshape exposure and inspect all views. Effect brightness cannot approve anatomy. |
| Generated detail changes every key | Repair against one approved identity/strip; simplify native clusters and inspect repeated ornaments. |

An image model may still make mistakes. The usable production promise is a reproducible guide, explicit checks and repair before release. The current original rig, acting and art remain unapproved; the next missing evidence is a real articulated grip, original walk/contact review, approved native art and in-game integration.

The user subsequently rejected the conditioning board as unnatural. Read [natural-motion practice](natural-motion-practice.md): new external source rig samples exist, but this exporter still reproduces the rejected/unapproved original posing as technical evidence. Do not promote it as a production pose seed.
