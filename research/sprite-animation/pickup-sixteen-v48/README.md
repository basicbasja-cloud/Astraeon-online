# v48 — can pickup use more frames?

Yes: this study builds an actual16-exposure bank from8 unchanged v47 drawings plus8 new native drawings at additional actual source times. **The new painted bank is REJECTED for continuity, not selected as a smoother replacement.** Source replay supports more samples; generated painted inbetweens still need to agree with existing pixels.

[Offline synchronized viewer](review.html) · [source16 / painted8 / painted16 comparison GIF](previews/source-8-16-comparison.gif) · [actual image report](review.json) · [manual decisions](manual-review.json).

## Fair comparison

Both banks last1900ms. Every old drawing starts at exactly its original timestamp. Original8 exposures: `[190,180,190,180,190,180,190,600]`. New16: `[90,100,90,90,90,100,90,90,90,100,90,90,60,60,70,600]`. Final600ms hold stays600ms. First6 action intervals get a midpoint, final recovery interval gets one-third and two-thirds poses. This gives8 original +8 new images without fake final-hold splitting or changing speed.16unique PNG hashes do not prove16distinct meaningful acting poses.

`render-source.py` opens a byte-identical copy of v45 saved rig and evaluates actual bones/weighted foot vertices at8new times. It does not invoke any historical builder or interpolate two raster drawings. New projected source foot drift upper bound~0.010132px, independent projection residual~0.00006764px. Original8 source guide cells are inherited v45 captures; these are separate from the new8 evaluations. Source is still blockout art, not approved painting or engine proof.

## What happened in actual painting

Four real host-native still edits, exact prompts/reference orders/raws retained. No external paid API/MiniMax/Tripo/credits. Host billing unknown; no zero-cost claim.

The first3 full4x2 redraws repeatedly lift the lower row relative to its logical origin, even with an explicit floor guide. Attempt2 has upper boot bottoms487..488px and lower457px within cells. Source guides and prompt numbers did not enforce geometry. All failures remain unchanged.

Then a recovery quartet was generated with four poses repeated as context in both rows. The diagnostic16bank uses fixed TOP cells0..3 of attempt2 and fixed TOP cells0..3 of attempt4. Bottom rows are unselected, **never shifted into place**. This is an explicit new layout contract, not a native16frame strip claim or per-pose registration. All original8 key PNGs are exact RGBA copies at output indices `[0,2,4,6,8,10,12,15]`.

This reduces the row problem but still fails: observed distal boot bottom spans12/14px across the16bank, compared with2px for the parent8. Several inherited windows also abstain on changed silhouettes. The unchanged6px surface budget remains failed; cropped/unknown windows are not passed as anatomical soles. First recovery drawing also reads as a lifted right heel despite planted source. Cape, boots and head silhouettes change between neighbors. More exposures currently make the mismatches more frequent, not reliably smoother. No final shoe cloning, frame fit, row offset, opacity cleanup or warp was applied.

## Reproduce and check

Blender4.3.2, Python3/Pillow/NumPy/SciPy; Chromium/Playwright for controls. Commands write v48 derived files only:

```bash
blender -b -t 2 --python research/sprite-animation/pickup-sixteen-v48/render-source.py
blender -b -t 2 --python research/sprite-animation/pickup-sixteen-v48/render-owners.py
python research/sprite-animation/pickup-sixteen-v48/build-guides.py
python research/sprite-animation/pickup-sixteen-v48/build-study.py
python research/sprite-animation/pickup-sixteen-v48/check-study.py
python research/sprite-animation/pickup-sixteen-v48/browser-check.py
python research/sprite-animation/pickup-sixteen-v48/check-study.py --require-production
```

Last command intentionally exits1. Ordinary check success proves clocks/old bytes/source projections and retained negatives, not art acceptance. Decoded GIF exposure counts/clocks are independently checked. Browser uses local HTTP and blocks external network;1×/0.25× one-shot, loop, all16time seeks, next/previous and grid tested. GIF repeats are review only.

Do not rerender this evidence in place after publication. `verify.py` is a read-only hash check; new authoring goes freshv49 on the same sole research branch. Existing v47/art/skill evidence and protected W remain unchanged; only CURRENT_HANDOFF and newv48/newmethod files change.

## Next work

Use source-guided coherent whole-action geometry with painted materials or a constrained artist-edit workflow to hold existing key family and contacts; more unconstrained full-strip redraws did not solve this. Preserve exact old8comparison. Fix the actual insertion shoes/shape and original family/socket/contact gaps before accepting16frames or another motion. No user acceptance inferred from “โอเคต่อเลย”; no head/body separation, swaps or game integration claimed.
