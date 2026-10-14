# Replaceable head and two hair styles, v33

2026-10-14. User says **“สมูทขึ้นเยอะ ต่อเลย”**. That positive smoothness feedback is [bound to the exact v32 frames/GIFs](user-v32-smoothness-feedback.json). The original motion, source clocks and previous artwork are preserved. This iteration makes a complete base head and two genuinely separate hair styles work on the same motion.

- [Silver / auburn synchronized GIF](hair-swap-compare.gif).
- [Interactive hair switch](hair-preview.html): original comparison, silver/auburn/bald, frame slider, both clocks, rig overlay. Appearance can change while the action is running.
- [Appearance comparison](swap-comparison.png), [all poses and hidden base head](hair-and-hidden-head-review.png).
- [Replacement pixel/bind checks](swap-review.json), [new-image source motion checks](source-motion-review.json), [browser checks](browser-qa.json), [visual review](visual-review.json), [evidence audit](audit-report.json).
- [Detailed reusable know-how](KNOW-HOW.md), [generation ledger](generation-ledger.json), [opacity failure/control](opacity-control-review.json).

Three actual native imagegen jobs created a complete bald head, a four-piece silver/auburn front/rear atlas and a packing repair. The first atlas joins two silver pieces; its raw pixels remain as a failure case. The corrected atlas has four separate complete components. No whole-character frames were independently regenerated. The runtime keeps the original 15 body parts and replaces the combined head/hair with rear hair → base head → front hair: **18 active parts** for a styled character,16 for bald/original.

| Check | Actual result |
| --- | --- |
| Original v32 restored | All8 entire PNGs byte-identical |
| Source-driven pose file | Byte-identical to v32 |
| Body pixels outside declared head render union | **0 changed pixels**, every variant/pose |
| Purple-eye pixels between new appearances | Identical rest patch and all8 projected eye interiors |
| Toe X/Y drift in each new appearance | **0px**, independent texture observations |
| Cuff source-relative phase error | **0.005313**, all3 new appearances |
| Support/phase criteria | Original6px / .25, unchanged |
| Distinct hairstyle silhouettes | **6,673 differing pixels**, not only recoloring |
| Regression/browser checks | **12 / 14 passed** |

The new head's generated interior alpha was252–253 rather than fully opaque. Without correction, rear hair tints538pixels in the protected eye patch by up to3channel levels. The explicit head-only opaque material promotes decoded alpha≥240 to255 before posing, retains soft outer edges/decodedRGB, and leaves the original raw files unchanged. The counterfactual replay retains the defect; the corrected appearances have identical eye pixels. This material rule is for intended opaque head skin, not translucent effects.

Fixed asset registration transforms are authored once into the original head coordinate system, then composed with the exact v32 head mount in every pose. They are not per-frame fitting. Actual exported matrices, depth order, source texture hashes and full RGBA renders are verified. Head passes are counterfactual renderer evidence, not a learned segmentation/anatomy detector; the projected eye ROI is an authoring comparison region, not blind eye detection.

The result passes **agent one-view hair-swap review**. Prior user feedback approves improved v32 smoothness; it does not approve these new hairstyles, a new face, all eight facings, object contact or the whole factory. The original v32 character remains selectable for exact comparison. All published v30/v31/v32 evidence and the13protected W files are unchanged. Work/push remains on `research/modular-sprites-full-body-2026-10-11`.
