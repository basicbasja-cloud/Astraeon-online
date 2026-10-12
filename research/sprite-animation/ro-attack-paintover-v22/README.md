# Direct Ragnarok attack body paintover — v22

The user rejects v21 authored slash staging and requests direct RO paintover. This exercise uses actual captured RO body pixels, not that rejected skeleton. Our character keeps the original detailed silver hair, bronze armor, gold scarf and fixed left-hip teal cloth.

Review [attack GIF](RO-attack.gif), [synchronized RO/body/weapon comparison GIF](RO-frame-comparison.gif), or download [Canvas viewer](review.html). This is an **SE review draft**. Other attack views, complete painted replacement parts and production acceptance remain unestablished. Earlier8-view walk repair is in [v21](../registered-walk-attack-v21/README.md).

## Captured authority and actual holds

Successfully retrieved [job1/male/action87 body+head without weapon](https://assets.latam-tools.com.br/image?job=1&gender=male&head=1&weapon=0&action=87&enableShadow=false). Its saved APNG is65×95 with9×100ms/900ms. This is community-rendered container timing, **not original-client/ACT timing**. The prior full weapon/FX104×121 capture at9×100ms remains separately bound in `motion-reference-v6/ro/attack-SE`.

Exact hashes reveal6unique body images across9exposures:

```text
body key: 0,1,2,2,3,4,5,5,5
time ms:  0,100,200,300,400,500,600,700,800
```

Exposures3–4 and7–9 reuse exact authored body PNGs. Weapon/FX may still change. No invented sword-down ready, recovery or automatic last→first gameplay edge is added. `reference-holds.py` verifies source/body assignment and exact holds; `reference-truth.py` checks captured pixels/order/clock and protected authored keys. Neither certifies anatomy.

## Actual attempts / remaining gaps

Four whole-sheet body edits produce24drawings; another imagegen job produces one original isolated sword. Exact prompts/raw files remain archived. Attempt1 widens final stance. Attempt2 narrows it but loses foreground-foot depth. Attempt3 restores a clearer nearer left shin/boot and is selected. Attempt4 changes supporting-leg appearance and suggests a lifted boot; it is unselected.

The first other-boot report is invalid: a generic lifted-phase ROI includes the supporting toe. Retained `attempt1-unreviewed-ROI-registration-and-grip.json` contains the≈67px result, which is **not anatomical evidence**. Reviewed per-key windows replace it; clipped sole bottoms now fail.

One shared scale is calibrated at key1; rigid translations follow the observed source screen-left boot trajectory. That boot is calibration and excluded from independent validation. Heads are not pinned to one height. Screen-side surfaces do not establish anatomical hips/world contact.

Independent source comparisons still flag differences: selected hair-top phase error reaches**21px**, and key4's other boot differs**20px vertically**. Hair/proportion differences affect these measurements, but do not justify exact-pose PASS. Proximal anatomy, physical contacts, finger wrapping, full source correspondence and complete painted parts remain REVIEW_REQUIRED/unapproved.

## Separate weapon / FX

Our generated sword attaches to a manually observed right-palm point with4px uncertainty. Orientation, palm occlusion mask and ribbon are authored presentation approximations. Body-only captures can omit armed-hand content carried by weapon layers; full smears can obscure grip. These points are not recovered RO bones or verified finger wrapping.

Image review catches a shortest-path ribbon going below/left while its endpoint still matches. The corrected sweep goes clockwise overhead; a winding/upper-region check supplements endpoint tests. Own FX starts500ms and clears880ms,20ms before the body ends900ms, so a stopped GIF cannot freeze a residual tail. Cancellation clears immediately. A separate loop demo adds1200ms hold, totaling2100ms; it is a replay control, not source recovery motion.

## Reproduce / verify

```bash
python3 skills/modular-eight-direction-sprites/studies/walk-test/pack-ro-attack.py --attempt 3
python3 skills/modular-eight-direction-sprites/studies/walk-test/build-ro-attack-review.py
node skills/modular-eight-direction-sprites/studies/walk-test/check-ro-attack-review.cjs
python3 skills/modular-eight-direction-sprites/studies/walk-test/package-ro-attack.py
python3 skills/modular-eight-direction-sprites/scripts/reference-truth.py --contract research/sprite-animation/ro-attack-paintover-v22/evidence/attempt3-reference-truth-case.json --out /tmp/ro-review.json --require-production
```

Last command must exit2. Recorded checks include183Python regressions,17Chromium checks,45explicit20ms body/weapon/FX samples, decoded clocks and clear terminal FX. Passing hashes/browser checks does not override visible pose discrepancies.

Next: settle flagged body proportions/head/boot trajectories, inspect isolated armed-hand/native attachment evidence, author our own reviewed matching rig, then export complete replacement parts. Expand attack views after this template is accepted. Captures, inferred joints, actual original geometry, new drawings and user approval remain separate authorities.
