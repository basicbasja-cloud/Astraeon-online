# Flat-ground walking, fractional sampling and independent image review

Draft v0.15, reviewed2026-10-12. [Executed16-frame experiment](../../../research/sprite-animation/ground-walk-sixteen-v15/README.md). This extends [spacing/registration practice](walk-spacing-and-registration.md), not a claim of an automatic anatomy detector.

## What the user's frame5 rejection teaches

More drawings can make errors more visible. A source rig's correct crossing pose does not prove the generated knee/calf belongs to the correct hip. Bind every user rejection to the actual raw bytes and slot; retain the raw layout failure as well. A new image never inherits earlier scoped approval. Review the chain4→5→6, its opposite-leg counterpart12→13→14 and the loop seam before judging a single attractive pose.

In the actual W source, LEFT is nearer the camera and RIGHT is farther. At phase5 the near sole is close to the ground while the far knee travels forward and its calf folds behind. Treat silhouette continuity, proximal thigh origins and occlusion order as separate evidence from sole height. Do not label a boot from screen-left/screen-right, cloth color or a manually repositioned badge. Do not infer hidden pelvis geometry as measured truth.

The current second drawing changes the passing-leg bend but its supporting knee and overlapped thigh still require review. An anchor at its sole is circular evidence for registration, not independent proof of leg ownership. The floor checker must not turn this case green for anatomy.

## Diagnose perceived hopping in the source and the art separately

1. Reopen the authoritative rig/action. Evaluate actual sole geometry and camera at the export times. Include dense between-key samples and the endpoint; clearance at eight keys can miss a real overshoot.
2. Keep floor proximity, physical support, balance and world foot-lock distinct. Height nearZ0 is only a candidate. A source with no both-feet-airborne height event may still have incorrect weight, heel/toe roll or skating.
3. For each observed source sole point `(x,y,z)`, project both the actual point and `(x,y,0)` using the actual camera. Near and far soles on the same world plane generally have different imageY under an oblique orthographic camera. Never force both onto one screen line.
4. Declare one clip-wide source-to-paint display transform. Draw its floor projection on the actual artwork. Review small visible heel/toe contours independently. Whole-character bbox bottom is not a contact observation.
5. Inspect heel strike, toe-off, passing and double support. A raised heel during toe-off is normal; a painted stance toe detached from its corresponding projected plane may merit a warning. A swing foot is not forced down to the floor.
6. Mark hidden/clipped/uncertain soles unknown. ROI lower-edge clipping must be INCONCLUSIVE because its measured contour is truncated. Check enlarged observation overlays before trusting values.
7. Keep calibration observations out of independent validation. A second visible sole in an anchor frame is still an independent observation; do not exclude the whole frame automatically.

`scripts/ground-contact.py` implements SHA-bound source/image validation, actual-pixel contour measurements, per-observation calibration exclusion and warning residuals. It does not estimate depth, weight or semantic leg identity from the picture. Wrong identity/ROI/scale can produce a wrong warning. Its budgets are declared study parameters, not universal correctness thresholds or accuracy percentages.

## Increase frames without changing the experiment's clock

Evaluate16 genuinely distinct times from the source, not eight duplicated poses. Source positions2.5/7.5/etc require fractional frame evaluation; a nearest-integer exporter biases spacing. Exclude the repeated final endpoint from the cyclic sprite bank but inspect it for continuity.

Build an eight-frame control from the even entries of the same16-art bank. Play both at the same total duration. Comparing older eight-frame artwork to new16-frame artwork changes art, registration and count together; label it accordingly. Keep native source timing available. Increasing exposure count does not fix a discontinuous pelvis, changed proportions or incorrect contact.

GIF has10ms delay units. Quantize cumulative exposure boundaries so the overall loop is preserved. At600ms/16, full-color files can use37/38ms while GIF uses30/40ms; the browser can display37.5ms intervals. Verify actual decoded frame counts, durations, alpha and visible pixels, calling the decoder's load before reading animated WebP duration. Animated WebP may discard RGB underneathalpha0 even with lossless visible pixels. Do not describe that as byte-perfect RGBA.

## Recover layout without hiding drawing errors

First reject equal-grid crops that clip figures. If the returned sheet contains complete figures in nonuniform rows separated by empty gutters, a documented shared-row registration can be a bounded recovery: one global sourcepixel scale and one translation shared by every figure in each row. Record boundaries, raw hashes, selected anchor ROIs, source phase and calibration exclusions. Verify no foreground is cut at panel boundaries or output edges.

Never silently crop away overlapping content, fit each character separately, mirror, freeze the head or shift a single pose until the floor score improves. Recovered authoring layout is not recovered physical contacts. Our current panel recipe uses512canvas/4columns and an explicitly declared source-floor presentation; it requires independent adaptation for another character. The packer now rejects foreground-crossing gutter cuts and nonfinite scale, and replaying its strengthened checks reproduces identical master pixels. A1254square16-panel generation has less pixel detail per character than a larger eight-panel result; upscaling to512does not restore source detail.

## Reproduction contract

Export a new character-specific rig/camera/sole/source-time receipt first. Then initialize observations with no copied landmarks:

```bash
python skills/modular-eight-direction-sprites/scripts/ground-contact.py \
  --init-from-frames path/to/character/frames \
  --source path/to/character/source-ground.json \
  --shared-scale 1 --shared-translation-y 0 --warning-budget 6 \
  --out /tmp/new-character-ground-observations.json
```

The numerical transform/budget above are placeholders to declare for that character, not recommended universal settings. Allheel/toe ROIs startnull, identityunconfirmed and calibrationfalse. The initializer refuses overwriting observations and mismatched phase counts/canvases. Annotate only visible contours, declare uncertainty and identify actual calibration samples before auditing. Unknown samples never approve contact.

After any new art, source/camera or timing edit, invalidate stale hashes and make fresh observations. Combine this report with proximal ownership review, body/garment acting, scale consistency, world-speed contact testing and complete interchangeable painted parts. Source height, a stable hair centroid and passing tool tests do not satisfy those other gates.

## Primary knowledge applied here

No new internet audit is claimed in v15. This is a new executed test of previously retained primary evidence:

- [Animation Mentor walk tutorial](https://www.animationmentor.com/blog/tutorial-animating-human-walk-cycle/): distinct contact/down/passing/up phases and coordinated body motion.
- [Kovar, Schreiner and Gleicher2002](https://graphics.cs.wisc.edu/Papers/2002/KSG02/) and [footplant solver documentation](https://research.cs.wisc.edu/graphics/Gallery/FootskateSolver/footskate.html): explicit toe/heel planting constraints; height alone is insufficient. That solver is not integrated here.
- [Spine graph](https://esotericsoftware.com/spine-graph) and [ghosting](https://esotericsoftware.com/spine-ghosting): interpolation, neighboring poses and traveled versus in-place review.
- [Our audited RO/King Lucas/ToS frame comparison](../../../research/sprite-animation/continuity-v14/README.md): native exposures, approximate phase mapping and visibility/camera limits, without game art as image-generation inputs.
