# Frame continuity, registration and reusable production review

Reviewed 2026-10-12, draft v0.14. [Actual experiment, comparisons and failures](../../../research/sprite-animation/continuity-v14/README.md).

The user accepts v13 W leg readability and rejects its jerky continuity. These are independent decisions, bound to its exact eight images. New v14 pixels do not inherit either v12 or v13 approval. Preserve anatomical owners when repairing motion, but do not require byte-identical principal frames if their spacing/proportions prevent a coherent whole clip. Keep previous accepted drawings and every attempted replacement separately.

## Learn from the complete sequence

Read [Animation Mentor's walk workflow](https://www.animationmentor.com/blog/tutorial-animating-human-walk-cycle/): contact, down, passing and up have distinct jobs; hips/chest/arms participate. A useful breakdown specifies how a foot travels between contacts. It is not another maximum-stride pose. Their splining guidance treats planted-foot translation differently from the torso. Do not apply a smoothstep to every channel or every exposure.

The [King Lucas developer account](https://www.devilishgames.com/2016/12/14/como-animar-a-un-rey-que-ha-perdido-a-sus-hijas/) describes changing walk attitude and avoiding hand changes from flipping directions. Our existing decoded first/second walk GIFs have13/16 exposures at30ms:390/480ms. They change both acting and duration; they are not a controlled demonstration that more frames alone improve motion. Study actual frames, not only the developer's description.

The audited RO male Swordman W loop has8 exposures at75ms in a community conversion. Its head/upper body vary modestly while the boots pass through ordered stride windows. The loop starts at a different gait phase than our source. The v14 board shifts the RO sequence by two entries for approximate visual comparison. It does not identify hidden RO bones or exact contact events. The complete unshifted sequence remains available.

Tree of Savior's retained33-exposure trailer window has original PTS, moving scenery and substantial leg occlusion. It is useful for whole-body/costume motion, unsuitable for asserting hidden knees or a stationary world foot. Fyna's retained example is idle, with missing timings in several decoded exposures: do not relabel it as a timed walk control.

## Diagnose before editing

1. Bind source rig, camera, times, original dimensions, art hashes and source origins. Check every interval, including last→first. Distinguish source and playback clocks.
2. Separate ground registration, body acting, limb ownership, phase spacing, scale/costume coherence and contact/root-speed matching. Passing one gate never approves another.
3. Inspect the observations too. Plot measured points on enlarged coordinate grids before comparing them. A hidden buckle stays unknown. One v14 marking attempt placed pupils near ears and inflated the jump; its66px claim is revoked and the failed inputs retained.
4. Track the same identifiable visible surface. Two screen-sorted ankle bands may measure unsigned spread, but cannot supply anatomical left/right velocities. Never relabel a foot because it moves to the other side of the screen.
5. Measure body placement from declared surface tracks and actual pixels, preserving intended bob/rotation. Do not repeatedly bbox-center, fit each frame to the ground's lowest alpha pixel, rotate, mirror or change per-frame scale to manufacture smoothness.
6. Audit loop values and spacing together. [Spine's graph](https://esotericsoftware.com/spine-graph) shows repeat boundaries and distinct interpolation modes. [Spine ghosting](https://esotericsoftware.com/spine-ghosting) explains neighboring poses, motion vectors and travel offsets. A comparison without root travel cannot prove world-space foot-lock.

## Executable contract for another character

`scripts/walk-continuity.py --init-from-frames ... --frame-ms ... --out ...` creates a fresh SHA-bound observation file. Every landmark starts unknown. The constructor refuses overwriting an existing contract. Specify actual exposure durations; the default75ms is a convenience for this study, not an industry rule. The [Aseprite Frame API](https://www.aseprite.org/api/frame) stores per-frame duration in seconds; retain the authoritative timeline through every exporter.

Populate only observations that can be verified on actual images. Calibrate body-height reference, camera/facing, source-phase mapping and provisional warning budgets per character. The logical ground root comes from source/export metadata; the head, belly, changing sprite bounds and lowest boot pixel are not interchangeable roots. Unknown root observations remain unresolved.

The checker computes exposure-aware cyclic displacement/velocity/second differences for explicitly tracked surfaces. These are sparse sample differences, not a recovered continuous motion curve. It keeps raw and uncertainty-adjusted values separate. Uniform color changes, turned faces, obscured features or untracked points can invalidate matching.

Optional independent image diagnostics:

- Fixed-ROI SIFT/RANSAC estimates reference-to-frame surface similarities without warping pixels. Require enough inliers; this study remains INCONCLUSIVE on both complete clips. Do not lower its criteria to force a green result.
- A calibrated palette-region probe measures actual occupancy, centroid and bounds. This hero's silver/lavender hair palette detects a48px old jump and11px new jump. It is a surface proxy, not recovered Head geometry. Its20px warning budget is specific to this512px study. Recalibrate for another hair color, outfit, facing, light or occlusion.
- Unsigned ankle spread can be compared with the real rig's projected spread using one whole-clip normalization. A0.15 profile-difference budget is provisional. Differences identify poses to inspect, not swapped identities or acceptance probabilities. Both current clips retain spacing warnings.

For anatomical chains, use `leg-continuity.py`, actual visible/amodal owner and depth exports, and `image_leg_audit.py` separately. Review pelvis-to-thigh origins, continuous near contours and terminated far contours. Missing proximal evidence must block a semantic pass. The image-structure comparator requires same character/view/phase; it cannot replace temporal review.

## Apply findings and reproduce safely

Mixing three generated drawing batches produced inconsistent registration in v13. In v14 a whole-eight redraw with four-pose appearance references still repeated stride poses and clipped a cell. Geometry-first editing using the real eight-phase guide plus one appearance frame improved placement and intermediate pose variety. All failures, prompts and exact origins are retained. Whole-sheet generation is useful, not deterministic pose control.

Use a phase plan and one coherent art pass, then shared-grid normalization. Preserve raw returned dimensions:1774×887 needs fractional443.5px cell extents. Alpha margins, all decoded frames and times must be verified. Do not interleave prettier frames from different batches until their anatomy, proportions, registration and temporal neighborhoods have passed independent review.

Preview equal-duration before/after clips and native reference timing. Keep an in-place review separate from traveled playback. [Kovar, Schreiner and Gleicher](https://graphics.cs.wisc.edu/Papers/2002/KSG02/) address footplant constraints; the [original solver documentation](https://research.cs.wisc.edu/graphics/Gallery/FootskateSolver/footskate.html) requires explicit planted toe/heel intervals. We studied those requirements, not integrated that solver. Sole clearance is not contact-lock. Reusing a1.333s walk at600ms changes the speed required to match its root travel.

Before mass reproduction, require reviewed phase spacing, visible limb ownership, stable character proportions, coherent torso/cape motion, contacts at actual game speed, loop/stop/turn transitions, and complete replaceable painted layers with hidden coverage. Current W output is a flat candidate with unresolved spacing and new-pixel anatomy review. Documentation, source count and passing regression/file/browser checks cannot certify production readiness.
