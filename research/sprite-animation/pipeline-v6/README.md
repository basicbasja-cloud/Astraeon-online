# Iteration 6 — executable review builds and anatomical guides

The [v0.6 skill](../../../skills/modular-eight-direction-sprites/SKILL.md) now has a [build/check/pack CLI](../../../skills/modular-eight-direction-sprites/scripts/README.md) and timed reference extraction. This is one original modular attack adapter, with reusable build safeguards. The prototype's artwork remains unapproved and its appearance has not reached the user's target.

## Review artifacts

- [review.zip](review.zip): 432 hash-verified files, including editable source, actual modular color/depth strips, the standalone swapping preview, GIFs and all 64 skeleton/overlay guides. Extract and serve the directory with `python -m http.server 8772`.
- [All eight directions × eight guide poses](pose-guide-review.png), [SE cut skeleton](SE-04-skeleton.png), [SE cut overlay](SE-04-overlay.png).
- [Guide coordinates and limitations](pose-guides.json), [completed full-build receipt](pipeline-receipt.json), [32 browser checks](browser-qa.json), [six invalid contract fixtures](contract-check.json), [reopened source weights/action check](source-rig-check.json).
- [External motion study archive](../motion-reference-v6/README.md), separate from the original character ZIP.

The committed receipt describes **the full local build**, including raw EXRs and intermediate files; these are not all shipped in the ZIP or this small Git review folder. Inside the ZIP use `package-manifest.json` for the shipped subset's hashes. To reproduce the full checks, run a fresh build. Serving/unpacking this package is preview only, not importing it into the game's asset system.

## Actual executed verification

A fresh build in `/tmp/astraeon-sprite-pipeline-v6` completed in **108.44 seconds**. It regenerated all 1,088 part frames and 96 independent full-scene checks. Required mechanical gates passed, including real source-hand attachment and **64** projected guides. Guide maximum right-wrist/weapon-origin discrepancy was **0.00001079 native pixels**; maximum limb-length error was **0.0000001933 world units**. These are source-coordinate measurements, not a guarantee of attractive palms or correct finished drawings.

Chromium exercised all 32 current checks, including held-body FX decay/expiry and actual swaps. A second build request verified all **4,175** recorded artifacts and returned `VERIFIED_HIT`. The review ZIP was written and hash-verified. An actual truncated NE hair strip in a separate copy was rejected by integrity checking while the completed source build remained intact. Repeated packing of the preceding completed build produced identical ZIP SHA-256. The final browser run additionally confirms that README and guide links resolve. Release packaging returned **exit 2**, explicitly refusing current failed/unapproved gates. Eight failure-boundary tests pass. FFmpeg extraction was additionally exercised with a local lossless three-frame video: 32×32, 200 ms per frame, 600 ms total.

The first development run stopped when the overlay drawer incorrectly assumed every pose already had an independent-reference composite. Only the four reference keys existed. It preserved its failure log; the fixed drawer now composes each required pose from real exported parts before adding the guide. The subsequent fresh full build passed. No approved artifact or prior proof was replaced by that failed run.

## Still blocked

Exact-color composition differs at **six source pixels**, maximum channel difference 90. Visibility/alpha/depth pass independently; there is no tolerance hiding or post-pixel patch. The rig's model aesthetic, finger/palm surface contact, animation acting and ribbon effect remain unapproved. There is no original walk/idle action family in this adapter, no accepted eight-view art turnaround and no production-game renderer test.

The user wants sparse poses that look good and remain anatomically correct. These guides are an inspectable foundation for that work; a successful CLI or coincident wrist socket does not itself satisfy that visual requirement. [Pose-guide practice](../../../skills/modular-eight-direction-sprites/references/pose-guide-practice.md) makes those separate checks explicit.
