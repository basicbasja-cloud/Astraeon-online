# RO / other-game paintover experiments — v19

ลองวาดตัวละครของเราทับลำดับ RO จริงที่เก็บไว้ และ ValyriaTear จาก native atlas/โค้ดจริงแล้วครับ รอบนี้มี4 imagegen calls: RO8key2attempts,8midpointdrawings,Valyria6drawings รวม30newdrawings. ชุด16ประกอบจาก8keyเดิม +8ภาพแทรก ไม่ใช่16ภาพใหม่ทั้งหมด **ยังไม่ผ่าน motion/art/production** และไม่แทนที่ upright source v17 ที่ผู้ใช้อนุมัติ

## ดูผลจริง

- [เทียบทีละเฟรม6banks /57exposures](frame-review.html): RO source8,our keys8,interleaved16,Valyria source6,our6,KingLucas13. เล่น clockเดิมหรือ equal800ms พร้อมปุ่มstep/scrub; cross-gamefractionalphase ไม่ใช่ recoveredbonealignment.
- [RO8keyGIF —600ms](ro-keys/walk-ro-cadence.gif) · [RO8keyAPNG —75ms/exposure](ro-keys/walk-ro-cadence.png)
- [16framesGIF —FAILED experiment,600ms](ro-sixteen/walk-native-cycle-600ms.gif) · [APNG exact37.5ms](ro-sixteen/walk-native-cycle-600ms.png)
- [16framesuniformGIF800ms](ro-sixteen/walk-uniform-control-800ms.gif) · [same8keycontrol800ms](ro-keys/walk-uniform-control-800ms.gif)
- [Valyria-style6exposures780ms —UNAPPROVED](valyria-keys/walk-native-cycle-780ms.gif)
- [RO source/ourdrawings](evidence/RO-source-paintover-board.png) · [Valyria source/ourdrawings](evidence/Valyria-source-paintover-board.png) · [midpoint4 actualcoordinate review](evidence/midpoint4-coordinate-review.png)

The browser viewer uses plainHTML/raster images, not SVG. Its standalone inline content/controls/57image decoding were tested in Chromium; file-URL navigation was unavailable (`ERR_BLOCKED_BY_ADMINISTRATOR`), so the authorized local authored HTML was supplied with Playwright `setContent`, without file navigation, policy changes or external requests. No game-engine integration tested. [Browser report](evidence/browser-report.json) · [desktop](evidence/viewer-desktop.png) · [mobile](evidence/viewer-mobile.png)

## สิ่งที่ตรวจพบ

RO source is **community-rendered original-game imagery**, not an official-client recording or recovered skeleton. Preserve its original8×75ms conversion; primary client studies now report24ms tick versus historical25ms, but this character's nativeACT/ticks weren't obtained. [Source audit](evidence/source-audit.json) and [pinned decoder receipts](evidence/pinned-source-receipts.json) record what was read, reused or unexecuted.

First RO attempt crosses two column gutters with cape pixels, so equal-grid packing rejects it; it is retained without deletion/individual fit. Second attempt fits but enlarges the character relative to conditioning and shifts the lower row. Pixel-bound joints under garments remain unknown. Paintover is not mathematically exact pose tracing.

Inserted midpoint4 widens the stance again between a bent trailing-leg key and a passing key. Midpoint boots/body grow and floor placement changes. Actual cyclic silver-hair occupancy detects:

| Bank | Largest step | Last→first | Status |
|---|---:|---:|---|
| RO8newkeys |18.95px|13.77px|No20pxwarning; anatomy/contact still unresolved |
| Samekeys +8midpoints |22.32px|22.32px|Loop warning, midpoint pose/scale failed |
| Valyria6drafts |27.93px|27.93px|Four temporal warnings; phase/pose unresolved |

These are calibrated surface-region measurements, **not anatomy accuracy or an animation quality percentage**. Initial y70ROI cropped some hair; invalid initial metrics retained in `evidence/*initial-roi-failed.json`, explicitly withdrawn. The checker now marks a region touching a crop boundary inconclusive, and measurements were rerun with one full-clip ROI. [Actual-image findings](evidence/actual-image-review.json)

Valyria sequenceIDs13/14/15/13/16/17 are6exposures,5unique native cells. Generated1/4 resemble the same neutral pose but are pixel-different;2/5 widen more than source intermediates. We preserve that drift as evidence. KingLucas13developerGIF was inspected/comparison-added; no new KingLucaspaintover was generated. RO/Valyria trials keep our silver-haired/gold-scarf quality, not their character identity.

## Source-of-truth tooling and reuse

[Reusable guide](../../../skills/modular-eight-direction-sprites/references/reverse-paintover-source-truth.md) distinguishes capturedpixels, native descriptor data, actual original source bones, visible observation, inferred reconstruction, new authored frames and user approval.

`reference-truth.py` verifies immutable captured order/canvas/timing/hashes and exact original authored key copies at sixteen-slot indices0,2,...14. Inserted slots name sourcepairs, including7→0, and remain authored. It rejects changing source75ms to purported native72ms, substituting a midpoint into a protected key, marking hidden joints as observed, missing times and forged source-known bones. **It verifies a research contract, not artistic correctness.** Current `--require-production` returns2.

```bash
PYTHONPATH=/tmp/astraeon-vision-deps python \
 skills/modular-eight-direction-sprites/studies/walk-test/build-reverse-study.py

python skills/modular-eight-direction-sprites/scripts/reference-truth.py \
 --contract research/sprite-animation/reverse-paintover-v19/evidence/ro-sixteen-truth-contract.json \
 --out /tmp/rechecked-reference-truth.json --require-production
```

[154Python regressions](evidence/regression-check.txt) include10new truth-contract and2actual-imageROI tests. [Decoded formats](evidence/decoded-format-clocks.json) retainAPNG37.5ms andGIF30/40ms600ms versus theexplicitlychanged800ms50ms clock;8-keycontrols use100ms. No individually aligned/rescaled frames, mirrored images, silhouette-fitting or inferred worldroot correction were used. A common initial sheet-to512canvas transform is preserved from pack manifests.

The reference pixels/declaredtime and accepted original v17 source are usable scoped authorities; the foreign source's hidden anatomical rig is not recovered. Next work remains original source-owner/contact-guided authoring and complete painted replacement parts. This experiment does not establish a reliable mass-production generator or approved new animation.

Only `research/modular-sprites-full-body-2026-10-11`.
