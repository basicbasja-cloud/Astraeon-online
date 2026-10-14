# Repair a faulty existing motion key without regenerating its neighbors

[Executed v39case](../../../research/sprite-animation/recovery-key-v39/README.md), [exact workflow](../../../research/sprite-animation/recovery-key-v39/KNOW-HOW.md).

Establish the initial animation as a coherent strip. If repeated whole-strip repairs alter unrelated keys, a targeted edit of one existing key can preserve the established bank; this is different from generating an entire animation independently frame by frame. Freeze non-target textures, pose records, clocks, transforms, thresholds and actual render passes before requesting the repair.

Use a full silhouette guide at the intended pose, with reference boots/root/camera, not only a coordinate dot over an incorrect pose. Internal rig/neutral-derived transforms and stencils are conditioning, never selected final art. Repaint a complete connected body with the native tool. Keep body-with-outfit as one logical slot, head style separate; do not return to mandatory limb equipment.

If a single-key edit uses a larger square reference plate, normalize only from known canvas placement/resolution. Never fit its resulting silhouette/feet/collar to the target. V39uses2×scale/`[128,0]`translation in1024square, then inverse sampling`[W/512,0,W/8,0,H/512,0]`. Retain actual raw output and the receipt. A locally packed verification atlas is not native whole-strip generation; verify the complete derivative chain independently.

`scripts/isolated-key-review.py` checks exact non-target records and actual full/body/head/collar pixels, unchanged clocks/body/head scale/limits, input hashes and known-canvas normalization. A changed clock, relaxed budget, non-target attachment or feature-fitted offset must fail. Actual target pixels changing is necessary but not an anatomical/acting proof. Re-run neck/contact/source-phase/two-axis checks and inspect the complete clip after any new drawing.

V39corrects a real10.68pxleftward recovery hitch to0while retaining seven other keys exactly and the unchanged bounded forefoot ranges. Eight newregressions/19browserchecks plus explicit exact-image agent review cover one sparse crouch/reach/return view. Production/user-art/concept-proportion/all-action/view approval remains unproved. Keep the failed v38case frozen as a negative control; do not retroactively rename it accepted. MiniMaxpaused/oldownattacks excluded/same solebranch authorization persist.
