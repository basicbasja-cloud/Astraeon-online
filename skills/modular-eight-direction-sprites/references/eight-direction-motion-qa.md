# Eight-direction motion QA and residual bounce

2026-10-12, v0.20. User clarification: **สมูท = อนิเมชั่นดูดีขึ้น แต่ชุดเก่ายังเด้งเล็กน้อย**. Preserve that qualitative feedback and the exact v19 W8 pixels. It is not a claim of jitter-free animation, correct contacts or approved production. Latest task requests8walking views, reusable smoothness/frame-continuity tools, then a research plan for additional motions.

## Independent gates

| Stage | Current executable evidence | What it cannot certify |
|---|---|---|
| Source replay | Reopened original67bone rig,64physical view/pose samples,128owner images; original files unchanged | Painted anatomy, recovered hidden RO joints |
| Captured pose order | SHA-bound RO8frames per view and600ms converted clocks | Native client clocks/hidden source rig |
| Vertical/horizontal continuity | Calibrated visible silver-hair centroid, axis steps/range, exposure-aware velocities/second differences, loop seam | Logical root, weight, footplant, anatomical labels |
| Texture/appearance continuity | Farneback forward/backward-consistent foreground, photometric residual on non-uncertain pixels | Semantic limb ownership, pose acting or naturalness |
| Proximal identity | Required actual-pixel connected traces for both sides, unknown-first review, exact-image issue ledger | Hidden hip coordinates merely inferred from a colored garment |
| Contact/root | Explicit separate review state, actual original sole geometry retained | Painted support from clearance or lowest-alpha bounds |
| Production | Complete painted parts/coverage/swap adapter plus artistic acceptance | Any automatic approval from a stable head or file count |

`scripts/sprite-motion-audit.py` recomputes its reports from bound image/source/history inputs. It refuses changed image hashes, source phases, source-owner renders or rig/action hashes. Removing a frame's local issue flag cannot erase its ledger issue in the same pixel/source-phase context. A claim of confirmed limb identity without paired proximal image evidence is rejected. Unknown anatomy/root/contact/parts always blocks production. `--require-production` exits2. Current adapter is the original walking family; arbitrary character rigs/actions require a source adapter and calibrated observation contract.

## A total displacement budget misses bounce

The old20px surface-step warning did not flag W's16.2px vertical jump. New provisional512px warning budgets separate horizontal20px, vertical8px and whole-loop verticalrange12px. These are **review thresholds**, not percentages of correctness. Native action acting may require different values; do not reuse a walk threshold for a deliberate crouch, jump or attack.

In the executed W8case the largest measured verticalstep is16.21px and range20.42px. The actual original source Head coordinate step at the selected comparison phases is1.67px, range3.02px. The surface centroid and Head joint are different features; the difference is a clue to investigate, not exact root-error attribution. Source native duration800ms is kept separately from the600ms comparison clock. We did not fix the artwork by pinning its head, scaling every pose or fitting boot bounds.

Check every adjacent pair and8→1. For one-shot/excerpt use `loop:false` to omit an invented return jump. Keep precise pose durations; halving exposure doubles sample velocity without changing pixel step. Source derivatives in this tool use the selected comparison exposure clock, clearly labeled as such.

## Optical flow is an auxiliary measurement

[Lai et al.'s primary project](https://www.wslai.net/publications/video_consistency/) studies temporal consistency of per-frame processing while preserving appearance. [FlowVid](https://jeff-liangf.github.io/projects/flowvid/) explicitly treats imperfect flow as a supplementary cue alongside spatial conditions. Their neural models were **not installed or run**. Two CVF full-text requests returned403; author project pages were read instead, and the limited reading scope is retained.

Our actual implementation uses installed OpenCV4.11 Farneback, not those research networks. Compute both directions, sample backward flow at the forward endpoint, reject inconsistent/occluded/out-of-bounds pixels, and report their coverage. A low-coverage edge stays inconclusive. Composite alpha in floating point before grayscale: unsigned-byte multiplication would overflow and corrupt the flow input. Warped target pixels exist only inside the diagnostic calculation; shipped/master images remain unchanged. Low warp error does not rescue a wrong leg or a stationary pose.

The current Sdraft is the concrete counterexample: verticalstep2.87px and computable flow, but its visible front contact pattern at frame7 repeats the frame3 lead side instead of the reference's opposite lead. Its status remainsREJECTED. This is a reviewed visible phase discrepancy, not a reconstructed hidden RO hip or an automatic semantic leg-swap classifier.

## Phase correspondence must be reviewed before generating

Initial v20owner guides used original16-key offset4. Frontal foot-lead review exposed a half-cycle mismatch with the RO observational bank. We retained those64poses/128passes and generated a second actual source export using offset12 (`12,14,0,2,4,6,8,10`). No source bone poses or anatomical ownership labels were changed. Only the selected cycle start changed. Corrected phase correspondence is still an approximate artist-reviewed mapping, not recovered RO ground truth for all views.

Seven first facing generations used the initial guide; S/SW were retried with the corrected guide. Both retries still fail visible phase expectations and remain separate failed evidence. Current8view review preserves the first candidates and exact existing W. Rechecking against corrected source does not retroactively change what conditioned the earlier generation. This is a production lesson: source correctness, phase matching, generator compliance and artistic acceptance are separate stages.

## Reproduction workflow

1. Bind an accepted appearance reference and scoped motion feedback. Freeze source pixels and original rejected/accepted history.
2. Export the actual source rig/camera/action at named times for all required views, including dressed and cutaway ownership. Record native clock versus preview clock.
3. Review source/reference phase and direction correspondence before multiplying jobs; no raster mirroring for asymmetric equipment.
4. Generate one complete clip per view using coherent source/appearance inputs. Preserve raw outputs and shared-grid packing. Validate foreground gutters and actual decoded counts/exposures.
5. Calibrate fixed surface ROIs for that character/view, inspect the measured component, retain incomplete results and set action-specific budgets. Whole-view head volume/registration differences still need visual review.
6. Run temporal/image diagnostics and the independent anatomy/contact/parts gates. Record unknown hidden regions. Never rename palette colors into limb ownership.
7. Review natural speed and slow playback, source side-by-side and silhouette/parts, then stop/turn/interruption. Only scoped user/art acceptance can establish the intended appeal.

[Executed8view study](../../../research/sprite-animation/eight-walk-factory-v20/README.md) provides64master frames, GIF/APNG controls, raster viewer, original bone/owner export, actual metrics and retained failures. Flat painted candidates do not supply complete interchangeable hair/clothes/items. [Next-motion research plan](../../../research/sprite-animation/eight-walk-factory-v20/NEXT-MOTION-RESEARCH.md) lists the missing production evidence before wider factory reproduction.
