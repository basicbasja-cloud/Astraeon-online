# Weighted diagonal slash v27 — source improved, art still incomplete

ทำใหม่โดยเทียบข้อมือ การง้าง/ตามแรง และการถ่ายสะโพกกับต้นแบบจริง
พร้อมวาดดาบแต่ละมุมใหม่ ไม่มีการหมุนภาพดาบใบเดียวขณะเล่น
**ผมยังไม่ให้ผ่าน production**: ภาพวาดยังมีความต่างของรองเท้าหลัง
และการจับด้าม/ลำดับบังของมือยังตรวจไม่ครบ ไม่มีท่าโจมตีที่ผู้ใช้อนุมัติ

- [GIF ภาพเรา + ดาบรายท่า ปิด FX](body-only-loop-demo.gif) — preferred acting comparison.
- [GIF ต้นแบบใหม่](source-loop-demo.gif) — actual reopened source; not painted-art approval.
- [เทียบช่วงท่า](phase-mechanics-comparison.png) · [เทียบข้อมือ](wrist-grip-comparison.png).
- [ดาบที่วาดแยกใหม่ตาม8คีย์](weapon/eight-weapon-review.png) — seven unique drawings + exact ready reuse.
- [Canvas review](review.html) — scrub, slow motion, source bones, observed hand points and optional tail; no SVG.
- [Self-review/rejections](evidence/selection-review.json) · [Reusable skill knowledge](../../../skills/modular-eight-direction-sprites/references/weighted-slash-and-weapon-poses.md).

## Findings and application

Actual source matrices expose a grip-basis mismatch: v26 assigned the sword to
hand+Y; native Flare blade is about59degrees off its hand-longitudinal axis.
The v27 experimental basis, elbow plane and forearm roll are authored together.
Total rest-relative source hand-frame angles improve from about98–179degrees
(v26) to8–28degrees. This includes roll and is NOT an anatomical wrist-flexion
score, universal safe joint range or proof of painted fingers closing correctly.

| Source-only proxy | v26 | v27 |
|---|---:|---:|
| Coil→follow hip forward travel, world units |0.043|0.125|
| Authored lean span |5°|19°|
| Mid-cut angular speed / preceding segment mean |0.267|1.013|

Hip/lean proxies are not COM, force, contact pressure or predicted damage.
v27 widens the base, bends reachable fixed-length knees, fixes the front sole,
allows rear heel roll while the rounded toe remains on the floor, and uses
monotonic cubic slopes through intermediate cut keys. Actual137saved-file times
verify mesh floor, front-sole stability, segment length, palm/hilt centers and
blade-basis replay. Rear heel rises about0.019world units; rear vertices move,
so this is not both-feet fixed-vertex locking. Finger wrap remains unverified.

One physical blade projects65.2–152.1px grip-to-tip across these eight poses.
`weapon-source/` evaluates actual mesh/camera per pose; `weapon/` contains new
painted drawings with different blade/guard perspectives. The runtime selects
body pose pixels directly; it has no rotating-master sword. Exact repeated ready
can reuse pixels. Pinned roBrowser ACT/layer rendering also supports authored
layer angles: do not claim that RO never transforms a sprite or freshly draws
all repeated holds. Our rule rejects arbitrary flat-master substitution across
changing views.

## Actual painted review and limits

Three whole-bank imagegen jobs plus a separate weapon job are retained with
exact prompts/raw PNGs. The first hilt-only body has reversed pommel direction.
The next full-sword raw has lower-row tips crossing ideal grid divisions but
intact before the next actors. Explicit empty gutters recover them without
inventing/cutting tips or warping anatomy; common scale and front-boot whole-frame
registration produce the preferred `full-sword-recovered` acting comparison.
The raw is not an equal-grid atlas. The latest `continuity-repair` fixes margins
but worsens independent rear warm-brown surfaceX variation to58.71px; not selected.

The preferred bank still has rear surfaceX25.85px/Y9.57px variation after front
boot calibration. Lowest warm pixels are surface proxies, not tracked anatomical
heel/toe vertices or recovered world contacts. Eight glove/forearm/tip observations
are bound to real new pixels, with explicit uncertainty; foreground support alone
cannot identify the correct hand or verify finger wrap. Source mechanics and
per-pose blade-direction/relative-foreshortening checks do not override these gaps.

The actor bank includes embedded sword pixels. The independent complete hilt/
blade drawings are not yet compatible replacement equipment: hidden grip/arm
layers and occlusion admission still need work. No accepted8-view attack, complete
painted modular bank, physics-validated strike or error-free factory is claimed.
Only exact Wwalking remains protected;13W files are byte-checked again.

## Clocks, checks and reproduction

Eight source/body exposures:100/80/50/50/80/100/100/120ms =680ms; seven unique
selected painted drawings because final ready copies the first. Loop demos add
800ms of ready, totaling1480ms. FX has33exposures on that same body clock, NOT
33new body drawings. FX is off by default in the review and is not visually
approved. APNG retainsRGBA; GIF uses a shared quantized palette.

15focused Python failure/unknown/binding tests,10direct Node tail tests,
16Chromium Canvas/clock/viewport checks,137actual source samples and decoded
animated-format clocks are bounded evidence. They do not approve art.

From repo root (Blender4.3.2, Python/Pillow/NumPy, Chromium/Playwright):

```sh
# Use a NEW empty output directory for each authoring run; never overwrite evidence.
blender --background --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/author-weighted-slash-v27.py -- --blend research/sprite-animation/ro-gait-v17/upright-source-rig/original-modular-walk.blend --out /tmp/weighted-slash-source
blender --background --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/check-weighted-slash-v27.py -- --index research/sprite-animation/weighted-slash-v27/rig-source/source-index.json --out /tmp/source-check.json
python skills/modular-eight-direction-sprites/scripts/attack-weight-review.py --case research/sprite-animation/weighted-slash-v27/evidence/painted-weight-case.json --root . --out /tmp/weight.json
python skills/modular-eight-direction-sprites/scripts/weapon-pose-review.py --case research/sprite-animation/weighted-slash-v27/evidence/weapon-pose-case.json --root . --out /tmp/weapons.json
```

The reusable author/check/pack/build/browser/package helpers live in
`skills/modular-eight-direction-sprites/studies/walk-test/*v27*`. Source revisions
and failed rounded-toe/wide-stance runs remain unselected. New tools always keep
`production_pass=false`; they are declared-family diagnostics, not universal
semantic detectors. Research source coverage is explicit in v26 receipts and the
linked skill guide: no claim to have examined every sword game or watched videos
that were only located/read.
