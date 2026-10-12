# Upright, compact original walking — v17 practice

The user rejects v16 smoothness versus RO and asks why our character must sneak instead of standing/walking upright. **A generic preset's forward lean is optional acting, not a sprite or rig requirement.** Establish the desired posture in the source before drawing over it. Do not try to remove a hunch only through timing, head registration or additional frames.

## Evidence and source study

The retained RO Swordman W capture contains eight native poses. The community conversion is 8×75ms; this is not a universal original-client clock. Native order and the earlier manual eye/belt uncertainty are retained. Comparing it with the rejected v16 sheet suggests compact pose spacing and an upright attitude are useful targets. It does not recover RO's hidden bones, exact contacts or motion curves.

Opened written primary tutorials this iteration:

- [Animation Mentor: basic human walk](https://www.animationmentor.com/blog/tutorial-animating-human-walk-cycle/) discusses contact/down/passing/up blocking, linear planted-foot translation, curve cleanup and overlapping arms. We apply source-first blocking and linear flat stance; its film frame counts and mirroring advice are not our sprite contract.
- [Animation Mentor: sneak walk](https://www.animationmentor.com/blog/tutorial-animating-sneak-walk-cycle-with-personality/) distinguishes the same phase structure from intentionally lowered knees, tiptoe contacts and curved torso. We use the distinction to remove unwanted sneak acting. Embedded videos were not watched or captured this iteration.

No external tutorial/game artwork is an imagegen input. Both new jobs use original source guides and owned original character appearance. No model/preset download or new external video capture is claimed.

## Reusable construction

1. Lock the body's neutral rest axes. For this original rig, use neutral-rest spine/neck/Head and thigh-parent attachment, not the preset's forward-leaning local rotations. Upright does not require a perfectly vertical internal neck joint or locked knees.
2. Author small in-place foot paths and root travel together. This exercise uses .42 world units per two-step cycle, .8s duration, .60 stance fraction, .040 swing height and .004 pelvis-bob amplitude. These are design parameters for this rig, not values extracted from RO or defaults for every character.
3. Keep flat-stance backward foot movement linear so it cancels root travel. Match swing endpoint tangents with a cubic Hermite curve and use a smooth zero-height lift at release/landing. Heel/toe roll needs separate actual surface contact review.
4. Solve fixed-length two-segment legs with anatomical knee poles. If a target is unreachable, refuse the bake and re-author the target/pelvis; never stretch a leg to conceal it. The first upright .584 pelvis-height trial was unreachable. .570 with the neutral thigh attachment succeeds. Small walking knee flexion does not imply a crouched spine.
5. Bake, reopen and sample the actual mesh between keys. Check sole penetration, both-feet-elevated candidates, actual fixed-vertex flat-support drift and the cyclic in-place joint endpoint. A changed lowest vertex is not a stable world contact point.
6. Render all chronological source phases at one fixed camera/root/scale. Preserve anatomical L/R; never mirror this asymmetric character. Produce a coherent clip and compare every actual new drawing, including the seam, with its guide.
7. Independently check drawn posture, proximal leg origins, spacing, stable volume and cloth continuity. A small hair-centroid step is not an anatomy or acting pass. A source check never transfers to generated pixels.

## Tool scope and actual results

`author-compact-walk.py` creates a fresh `.blend` and new active action `original.compact.contact-walk`; it never edits v9. `compact_gait_math.py` owns the endpoint curves. `compact-gait-check.py` hashes the ground receipt, mesh and motion before computing source diagnostics. Each new character needs its own rig basis, reach envelope, camera, stride and explicit budgets.

For v17:129 bake samples /257 dense sole samples /16 actual exported poses. Sagittal pelvis→neck tilt is4.1215–4.1224°, minimum evaluated soleZ is.0009604, no both-feet-elevated candidates at.015 world threshold. Fixed heel vertex drift within independently sampled flat intervals is at most.00000355 world. One initial right-foot boundary sample has insufficient interval coverage and remains unevaluable. The in-place endpoint joint error is.000000688 world.

These numbers certify only the named source checks. They do not certify support forces, balance, rolling foot contact, game-speed contact, painted posture/limb ownership or aesthetics. Historical template metadata in `motion.json` remains explicitly scoped in the evidence sidecar; its old source clip/old diagnostic fields are not new measurements. Select the new active action when exporting again.

**Both redraws fail promotion.** First: upper torso is more upright, but lower-row lean, wrong/repeated phase shapes and40.66px4→5/32.20px8→1 hair-region jumps remain. Second: whole-cycle edit repeats poses and fails equal-grid packing at frame1. Keep raw inputs, outputs and failures. Do not repair scores through per-frame fitting, changing thresholds or invented hidden joints. Until temporal drawing control actually preserves the source, this is an authored-source exercise and failed art experiment, not an accepted mass-production backend.

Reproduction commands and exact-bound receipts: [v17 study](../../../research/sprite-animation/ro-gait-v17/README.md). The source remains16 samples; the art test uses8 independently generated poses to test sparse RO-like phase economy. It is not a same-pixel16→8 control. Source and old/new art use the800ms equal-cycle viewer; native600ms RO timing is labeled separately.
