# Whole-body frames with independent head, weapon and trail

The user rejects the delivered segmented appearance: bending makes the knees/leg volume disappear and the figure looks cut apart. This supersedes the appearance approval implied by v56's finite numerical gates. Preserve the old evidence; do not retroactively change a report to hide the failure.

The new production boundary is four logical slots:

| Slot | Includes | Authoring requirement |
|---|---|---|
| body | torso, full arms/hands, thighs, knees, shins, boots, outfit, cape, scarf | Draw the whole posed body together per frame. No runtime cuts at elbows, knees or ankles. |
| head | complete face, ears, hair and head accessories | Pose-appropriate head drawing and an authored neck connection. Hair is not separate from the head in this simplified adapter. |
| weapon | complete equipped weapon | Frame-specific hand socket, grip and orientation. Front/back passes may be needed. |
| trail | weapon arc/trail and associated effect | Independent clock and explicit front/back occlusion. It must not deform the body. |

The original source rig can still provide pose guides. It must not serve as a paper-puppet renderer for the final body. Flattening an already broken segmented render into a PNG does not fix the pose. Outfit swaps require another coherent body bank or a separately reviewed production process; this design deliberately gives up arbitrary runtime limb/outfit assembly.

RO inspiration is the action-frame body plus independent head/equipment model. An ACT frame may itself contain multiple drawing layers; it is inaccurate to claim that every RO body is literally one raster layer. Our single complete body raster is an implementation choice that prevents runtime limb seams. Existing v51 references establish sampled action/direction behavior, not a universal layering claim.

The immediate experiment is a single-pass, sixteen-pose front pickup strip, using the original neutral as the visual reference. The generation must redraw bent knees and the full costume coherently. Two native attempts are retained. Attempt2 is a sixteen-frame motion candidate and remains rejected, never automatically accepted because its canvas, alpha, foot contour or connected components pass. Do not extend it to all views or attacks until actual image and motion review succeeds.

For head separation, first verify the whole figure, then extract complete head/hair without painting or geometrically moving any pixels. Recomposition must reproduce the full frame exactly. Actual head replacement additionally needs matching pitch, neck position and collar occlusion; exact recomposition alone does not validate a different head.

No weapon or trail art is claimed for the empty-hand pickup prototype. The four-slot contract supports those logical layers without inventing attachment or swing evidence.

## Current executable proof

Open `four-slot-review.html` (self-contained) to toggle the whole body and head, seek all16frames, and play1×/¼×. `prototype-browser-review.json` records actual browser draw/composition checks. There are exactly two active images per frame for this empty-hand action and no runtime joint transform. `extraction-review.json` proves visible RGBA identity to the newly generated full figures. The manually drawn head masks remain provisional and include gold costume fragments; do not use them as approved interchangeable heads.

`motion-review.json` and `contact-review.json` correctly reject the new animation. Native source packing and boot locations drift, the recovery contour jumps, and neutral endpoints differ. No per-frame normalization hides these problems. `review-decision.json` makes the current production rejection explicit. The goal of this prototype is to prove the simpler rendering boundary while preserving failed art evidence, not to repeat the earlier false appearance approval.

Run `python build-prototype.py` only while authoring this case; after publication preserve it as read-only. `python check-prototype.py` exercises the actual browser, pixel roundtrip and invalid-fragment controls, and confirms the retained motion/contact failures. These are different results: architecture PASS, production FAIL.
