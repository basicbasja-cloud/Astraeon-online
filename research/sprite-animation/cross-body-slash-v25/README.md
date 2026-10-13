# v25 cross-body slash pilot

**Unapproved experimental attack. Current image audit remains incomplete.**
The user rejected [v24](../stable-hand-sweep-v24/README.md). This iteration studies
the actual SLYNYRD/Saint11 frames and pinned RO attack/layer selection code, then
changes the original source arm path before three whole-sheet redraw experiments.

Review [attack GIF](attack-loop-demo.gif), [RGBA animated master](attack.png),
[body without FX](body-only.gif), [eight poses](attack-eight-poses.png), or download
[standalone Canvas review](review.html). The review compares the source, body-only
art and body+tail on the same clock, with pause/step, slow motion and markers.
Source bone markers appear only on the source; painted observations are manual
contour estimates, not recovered bones. No SVG or game integration is involved.

## Changes and evidence

- New source: anatomical-right hand crosses from its own shoulder toward the
  opposite waist; pelvis/chest turn together, both modeled feet remain grounded,
  arm/leg segment lengths fixed. A rendered conditioning sword guides the grip;
  the saved runtime source and final painted actor omit a rigid steel blade.
-8 sparse exposures,680ms, holds100/80/50/50/80/100/100/120ms. Final ready is an
  exact copy of first ready. The loop demo adds800ms idle,1480ms total; the one-shot
  action remains680ms. These are authored timings, not a universal RO clock.
- Attempt2's strike/follow palms were only16.97px apart and failed the new
  uncertainty-aware gesture check. The source intermediate wrist was revised,
  then attempt3 redrawn:86.98px distinct cut→follow displacement; source/observed
  movement direction dot0.992. This is contour/source agreement, not semantic
  hand/rig correctness or artist acceptance.
- The tail uses the same current key and manually observed hand with an authored
  virtual blade guide,230≤t<400ms; no recovery smear. Its leading edge reaches
  the hand and its outer endpoint follows the virtual tip. FX is a separate layer.
- Actual browser captures use33exposures,20/30ms. Every sparse pose boundary is
  retained exactly, avoiding10ms GIF holds. These are effect presentation samples,
  not33character poses. GIF uses one shared palette; APNG preserves RGBA.
- [Independent saved-source audit](evidence/reopened-source-revised.json):137
  actual evaluated times. Modeled sole drift below3e−7world units and palm/hilt
  center error below9e−7. Fingers/acting/balance forces/painted contacts remain
  unverified. The source is authored, not a retarget of an external video.
-16 actual Chromium checks,10 tail tests,8 gesture regression tests. They verify
  technical behavior and catch failed controls, not production art acceptance.

## Outstanding failures

[Image audit](evidence/slash-gesture-report.json) remains
`REJECTED_OR_INCOMPLETE`, `production_pass=false`: held-out bootX16.32px andY2.97px
variation exceed provisional4px/2px diagnostics. Lowest-alpha boot contours are
screen-side observations, not stable world-contact vertices. The grip/guard and
edge alignment are still ambiguous after generation; a round golden cap cannot
be relabeled a verified crossguard. Finger wrap, hidden joint ownership, precise
weight transfer, source-pose matching, animation appeal and user acceptance are
unresolved. The actor is one flat layer; full painted replacement parts are absent.

Only existingWwalking has user acceptance. [Protected pixels](evidence/protected-W.json)
are byte-identical to the previous commit. No other walk/attack or factory release
is approved by these checks. Failed attempts, the first source version, original
prompts, an initially misplaced transparent-pixel knuckle annotation and all
source/packing receipts are retained. Never promote a failed bank by relabeling it.

## Reproduce

Run from the repository root on the sole research branch. Author into a fresh
directory; the author refuses to overwrite a source. Installed tools: Blender4.3.2,
Python/Pillow/NumPy, Node and Playwright/Chromium.

```bash
blender -b -t 4 --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/check-cross-body-slash-v25.py -- --index research/sprite-animation/cross-body-slash-v25/rig-source/source-index.json --out /tmp/v25-reopened-source.json
python skills/modular-eight-direction-sprites/scripts/slash-gesture.py --case research/sprite-animation/cross-body-slash-v25/evidence/slash-gesture-case.json --root . --out /tmp/v25-gesture.json
python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p test_slash_gesture.py -v
node research/sprite-animation/cross-body-slash-v25/hand-tail.test.mjs
node skills/modular-eight-direction-sprites/studies/walk-test/check-cross-body-slash-review-v25.cjs
python skills/modular-eight-direction-sprites/studies/walk-test/package-cross-body-slash-v25.py
```

The browser requires this environment's supported execution grant; it loads
self-contained HTML via setContent and blocks outgoing HTTP requests. Image
redraw is performed with imagegen using recorded prompts/conditioning references;
packing only applies one shared scale and whole-frame registration. It does not
repaint, warp limbs or reconstruct hidden joints. See the durable
[slash guide](../../../skills/modular-eight-direction-sprites/references/cross-body-slash-gesture.md).
