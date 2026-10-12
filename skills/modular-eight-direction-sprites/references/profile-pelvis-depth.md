# Profile walking: pelvis ownership, contour interruption, and reusable checks

Iteration 12, 2026-10-12. The user rejects the E pose 3 correction again: moving the teal cloth is not proof that the forward thigh belongs to the right hip. They request better E/W depth, an accurate checking tool, and durable knowledge for other characters. The user then approves **exactly** `exec-8aaa73f6-b135-4e5b-b908-b3de6bc8b594.png` as correct, but rejects pose 3 of the later `exec-ea566918-4777-4e08-be60-51fabc8b0bf5.png`. Keep these different images and decisions separate.

## The user's contour rule

The [recorded interpretation](../../../research/sprite-animation/profile-depth-v12/evidence/user-contour-rule.json) comes from their rough drawing labeled “ซ้ายนำ” and “ขวานำ”. For the W-facing example, anatomical L is near and R is far. When L leads, its nearer thigh contour continues into the leading leg and the far trailing contour disappears behind it. When R leads, the leading thigh emerges from behind the nearer trailing L thigh: the far contour stops at the overlap, while the near contour continues. **Changing the leading foot does not change hip ownership or the near/far side.**

A leading leg does not require an exposed internal hip joint. Clothing can hide it. The drawing needs a readable pelvis-to-upper-thigh origin and appropriate contour interruption/occlusion boundary. A bare joint marker, fixed boot position, recolored panel, darker leg, or continuous calf stroke alone cannot establish ownership. “Both hips visible” is not a universal requirement: the far hip may naturally be hidden.

For this source/camera, E has R near and W has L near throughout the four poses. This is **measured for this rig**, not a universal naming convention. Recompute camera-space ordering for a different skeleton, rest basis, camera, or turning action.

## Sources studied and how they changed the pipeline

[Source fetch audit](../../../research/sprite-animation/profile-depth-v12/evidence/research-source-audit.json) records byte hashes and actual reading scopes.

| Source | Reading and useful distinction | Executed change / limit |
| --- | --- | --- |
| [Li & Malik, Amodal Instance Segmentation, ECCV 2016](https://arxiv.org/abs/1604.08202) | Abstract: visible region and complete region including occlusion are distinct targets. | Export both actual dressed visibility and complete isolated leg/pelvis geometry. These source surfaces are known; hidden parts of a generated drawing are not recovered by that render. |
| [pix2gestalt, 2024](https://arxiv.org/abs/2401.14398) | Abstract: reconstructs plausible whole objects from partially visible images, including art. | A generatively completed hidden hip remains an inference. No model was run and no generated cutaway is treated as ground truth. |
| [Spine draw-order keys](https://esotericsoftware.com/spine-keys#Draw-order) and [clipping attachments](https://esotericsoftware.com/spine-clipping) | Actual draw order and clipping can control which attachment interrupts another. | Ownership belongs to bones/slots; visible contour interruption belongs to compositing. A hue change is neither. No Spine runtime is executed here. |
| [Lowe, Distinctive Image Features from Scale-Invariant Keypoints, IJCV 2004](https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf) | Feature localization/orientation, descriptor matching and geometric verification sections. | New OpenCV SIFT/RANSAC torso registration precedes a bounded edge-distance comparison. One positive similarity transform, no reflection or leg-specific fit. This checks image structure, not semantic limb classification. |

Blender manual requests returned HTTP 403/404; no unavailable passage is claimed as read. One initially queried arXiv identifier was unrelated and discarded after checking its title. The depth evidence below is an actual executed render and numerical comparison, not a literature claim.

## What we executed

`export-profile-depth.py` reopens the original SHA-bound v9 rig without pose changes. E/W at source indices 0/10/20/30 produce **8 poses × 5 modes = 40 render passes**: dressed, garment/arm cutaway, isolated R, isolated L, and isolated pelvis/torso. Bone weight groups identify ownership. The body torso is the original simple source mesh, not a detailed anatomically recovered pelvis.

`pack-profile-depth.py` preserves float32 scene-unit depth, integer IDs and shaded surfaces. Display depth uses one fixed **[3.6, 5.4]** range across views/poses, never per-frame normalization. Where isolated R/L overlap and the cutaway visibly belongs to a leg, the nearer isolated Z agrees with the visible leg: **14,421 pixels, zero mismatches**. This validates source visibility only. Projected hip depth differences are about 0.096–0.101 scene units. Near/far hip roles do not change with the lead foot.

The sampled far proximal leg region has no same-owner pixels visible in the dressed source in these eight poses; much of the near region is covered too. This shows why a correct skeleton under clothed renders did not supply enough readable painted-root evidence. The sample is a 24px neighborhood of the source hip projection, not a claim that a joint should be visible through its surface.

The checker now requires independently observed pelvis-edge→upper-thigh→knee paths for **both** legs and a paired contour/T-junction depth review. A covered joint may use a readable occlusion boundary. Unreadable origins, duplicate side traces, unsupported paths, or a wrong near-side claim remain blocked/rejected. A calf trace that matches an annotated foreground owner now reports **`foreground_order_only`**, not `reviewed_match`, unless proximal identity is also established. Old v11 match claims are withdrawn; the latest E correction remains user-rejected.

## Independent image check, with an honest scope

`scripts/profile-structure.py` checks actual candidate RGBA against the exact user-approved W pose 3. It does **not** use the rejected-image flag to produce its structural result. The reference has a SHA-bound approval receipt, source view/time, torso registration ROI, and reviewer-selected pelvis/thigh ROIs.

SIFT descriptors and RANSAC estimate one diagnostic torso similarity. Insufficient correspondences, weak inlier support, excessive scale/rotation, or incompatible canvases produce `INCONCLUSIVE` or an input error. After registration, symmetric Canny-edge distances in the declared pelvis/thigh regions report differences. No pose/leg warp is allowed and the shipped art remains unchanged.

The actual new rejected W pose 3 produces **`STRUCTURAL_DIFFERENCE_REQUIRES_REVIEW`**: the proximal overlap region has a 95th-percentile edge distance about **17.74px**, exceeding the provisional 8px review budget. The approved reference and bounded brightness/translation controls remain within budget. This is useful independent image evidence, **not proof that a learned detector identifies swapped anatomy**. Garment edges, permitted redesigns and changes in drawing style can also differ. No confidence/accuracy percentage is established by one positive and one negative art pair.

A structural match cannot approve unknown anatomy. A different character, costume silhouette, camera or source phase needs its own source maps and approved reference/regions. If a new figure has no approved image, start with source ownership/depth and explicit review; do not use this character's texture edges as a universal anatomy detector.

## Approval is separate from unobservable measurement

The new W sheet is **user-confirmed correct for leg readability** and may serve as a scoped positive reference. Its exact raw SHA and four derived frame hashes are recorded. Unknown internal hip coordinates remain unknown; the checker reports user visual acceptance separately from measurement incompleteness. It does not falsely reject that approval merely because the joint is hidden, and does not transfer it to another image or another direction.

The E candidate remains unapproved. Trying the approved W sheet as a whole-character appearance reference for another E generation instead returned a W-facing drawing; it also clipped a cell boundary and the user rejects its third pose. Preserve this failure. An approved facing image can dominate the pose/view prompt; generate opposite views from actual source geometry and inspect their orientation before packaging. Never mirror this asymmetrical character to hide that failure.

## Reuse for other characters

1. Define rest-basis anatomical R/L, bone parents, complete geometry and garment slots. Derive near/far from camera depth, never screen sorting or a costume color.
2. Export fixed-camera skeleton, visible IDs, isolated complete legs/pelvis, and metric depth at the exact clip times. Keep near/far roles and lead-foot phase separate.
3. Stage garments so the near pelvis-side seam and overlap are readable. A hidden far root may be communicated by correct contour interruption; do not expose impossible joints through the body.
4. Paint from the same underlying pelvis and both leg chains, then cover them with separately owned garment layers. For production, keep complete replacement pieces and immutable bone/slot identity. A flattened whole-character generation cannot prove those hidden pieces.
5. Check pelvis→thigh, near/far contour interruption, knee→shin, root/contacts and loop timing independently. Moving a panel or adding a shadow is not an identity correction.
6. Bind each review and approval to actual pixels. Use user-approved examples as positive fixtures and confirmed errors as negative fixtures; avoid copying inferred source coordinates into art observations.
7. Use structural image comparison only within its reference/view/phase/appearance contract. Review false positives and collect varied held-out labeled cases before claiming automatic semantic accuracy.
8. Retain unobservable anatomy and failed generation as explicit outcomes. Source depth, image evidence, user visual acceptance, motion contacts and complete modular release are different gates.

## Commands

```bash
blender -b -t 4 --factory-startup --python-exit-code 2 \
  --python skills/modular-eight-direction-sprites/studies/walk-test/export-profile-depth.py -- \
  --blend research/sprite-animation/walk-test-v9/original-modular-walk.blend \
  --output /tmp/new-profile-depth
PYTHONPATH=/tmp/sprite-render-deps python \
  skills/modular-eight-direction-sprites/studies/walk-test/pack-profile-depth.py \
  --renders /tmp/new-profile-depth --output /tmp/new-profile-package

python skills/modular-eight-direction-sprites/studies/walk-test/review-profile-depth.py
PYTHONPATH=/tmp/astraeon-vision-deps python \
  skills/modular-eight-direction-sprites/scripts/profile-structure.py \
  --reference research/sprite-animation/profile-depth-v12/evidence/W-pose-3-structure-reference.json \
  --candidate research/sprite-animation/profile-depth-v12/evidence/user-rejected-new-W-pose-3-diagnostic.png \
  --out /tmp/new-image-structure-check

PYTHONPATH=/tmp/astraeon-vision-deps python -m unittest discover \
  -s skills/modular-eight-direction-sprites/scripts/tests -q
node skills/modular-eight-direction-sprites/studies/walk-test/verify-profile-depth-ui.cjs
```

Dependencies: Blender 4.3.2, NumPy/Pillow, OpenEXR 3.5.2 for packing, OpenCV headless 4.11.0.86 for image comparison, Playwright/Chromium for UI checks. OpenCV may be installed in an isolated dependency directory with `python -m pip install --target /tmp/astraeon-vision-deps --no-deps opencv-python-headless==4.11.0.86`. Without it the six image-comparison unit controls explicitly skip; do not report them as executed.
