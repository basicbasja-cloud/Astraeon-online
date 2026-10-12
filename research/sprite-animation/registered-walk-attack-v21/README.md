# Eight-direction walk registration / rejected authored attack — v21

The user requests removing unintended frame bounce and making an attack, then rejects the authored attack poses and requests RO paintover. The active attack is [v22](../ro-attack-paintover-v22/README.md). These are research candidates, not approved production assets.

Review [walk GIF](walk-eight-directions.gif), [before/after GIF](walk-before-after.gif), or download [Canvas viewer](review.html). Default clock:8×100ms/800ms. Separate600ms APNG:8×75ms; GIF requires centisecond quantization.

## Walk changes

64masters remain512². Seven views preserve v20 anatomy/painting without resampling: SHA-bound integer XY translation follows the actual original Head trajectory, using first-exposure hair-region calibration. Explicit alpha≤1 provider noise is removed. No limb is warped, stretched or frozen. Original v19/v20 files remain unchanged.

S is repainted: contact phase7 visibly leads screen-left, opposite phase3. The first new S attempt misassigns an earlier contact and is retained. This scoped correction is not hidden hip recovery or whole-loop approval.

| View | v20 max vertical step px | Registered max step px |
|---|---:|---:|
| S | 2.87; repaint audited separately | 1.59 |
| SE | 32.08 | 1.39 |
| E | 6.15 | 2.01 |
| NE | 33.41 | 2.13 |
| N | 4.08 | 1.49 |
| NW | 4.87 | 1.60 |
| W | 16.21 | 1.86 |
| SW | 21.12 | 1.70 |

All views have zero warnings under declared3px axis-step/6px vertical-range budgets, including the loop edge. This is calibrated surface registration, **not** independent logical root, physical contact or naturalness acceptance. Source intentional small movement remains. Cross-facing size/root, proximal painted anatomy, contacts and complete painted replacement parts remain unresolved; all64frames are REVIEW_REQUIRED.

## Rejected attack retained

Two whole-sheet edits produce8painted SE slash poses from fresh authored source. The user rejects their staging. Fixed-length IK, grounded source soles and technical playback do not rescue that rejection. See [feedback](evidence/user-rejected-attack.json).

The first source also attaches the hilt to `hand_r.head`, the wrist. Corrected `attack/source-palm-fixed` resolves the actual complete glove-palm mesh center. Independent reopened-file checks evaluate161times×4views=644poses: palm/hilt center error≈1.04e-6world, sole-vertex drift≈3.25e-7world. The checker **fails the actual initial wrist-attached source**. These tests do not establish finger wrapping, acting or painted anatomy.

Original source, raw failures, generation conditioning, blade observations and separate FX remain archived. Body8exposures total800ms; trail300–430ms clears on cancel and is empty in terminal samples. This is a rejected motion study. Generation provenance refers to the initial source before palm correction; it is not relabeled retroactively.

## Reproduce

```bash
PYTHONPATH=/tmp/astraeon-vision-deps python3 skills/modular-eight-direction-sprites/studies/walk-test/build-registered-walk.py
python3 skills/modular-eight-direction-sprites/studies/walk-test/pack-sword-attack.py
python3 skills/modular-eight-direction-sprites/studies/walk-test/build-registration-review.py
node skills/modular-eight-direction-sprites/studies/walk-test/check-registration-review.cjs
python3 skills/modular-eight-direction-sprites/studies/walk-test/package-registration-review.py
```

Run source authoring into a fresh output path with Blender `--python-exit-code 1`, then independently reopen with `check-sword-source.py`. Original v17 blend stays unchanged. Verification includes183Python checks,8attack-FX checks,20actual browser checks,64walk registrations and source positive/negative cases. `sprite-motion-audit.py --require-production` still exits2. None of these counts is artistic acceptance.
