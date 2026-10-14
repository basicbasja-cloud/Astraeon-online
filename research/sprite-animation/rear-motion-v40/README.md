# Rear-view proof and a caught false positive — v40

The user accepts the exact v39 crouch/reach/return and authorizes the next proof. That acceptance is hash-bound in [user-v39-acceptance.json](user-v39-acceptance.json). The new experiment uses the same external motion from a physical rear camera, with newly painted rear body/outfit and a separate rear head. **The source-camera proof passes; the new painted motion is rejected for guide fidelity.** Acceptance of v39 is preserved and does not transfer to this new artwork.

- [Front/rear comparison, same source clock](two-view-source.gif); [game-clock comparison](two-view-game.gif).
- [Rear draft GIF, explicitly rejected](review-game.gif); [source-clock draft](review-source.gif); [interactive review](motion-preview.html).
- [Actual eight-frame sheet](motion-contact-sheet.png), [diagnostics including failed absolute displacement](motion-diagnostics.png), [neck detail](motion-neck-detail.png).
- [Source/painting comparison](source-vs-art-source.gif), [before/after two existing-key repairs](before-after-source.gif).
- [Independent camera/source audit](source-view-qa.json), [strict painted-motion report](motion-qa.json), [decision](review-decision.json), [agent inspection](visual-review.json).
- [Detailed reproduction and lessons](KNOW-HOW.md), [seven actual still jobs and exact inputs](generation-ledger.json), [reference reproduction](reference-reproduction.json).

| Proof | Result | Scope |
| --- | --- | --- |
| Same GLB, PickUp world joints and eight timestamps | Pass, world difference0 | External source only |
| Independent orthographic reprojection | Maximum0.0000534px |136 named source observations, not painted joints |
| New complete rear head / body-owned collar | Maximum0.7831px endpoint residual; all bridges255alpha | Two logical equipment slots, three Canvas passes |
| Separated boot surface X/Y ranges | Screen-left5/2px; screen-right5/2px | Visible surfaces, unchanged6px budget; not zero drift or force contact |
| Fitted two-axis temporal phase | Held-out X0.1491/Y0.1070, below0.25 | Calibrated rest/peak, cannot prove shape |
| Fixed guide displacement, rest origin only | **26.02px error, above provisional8px** | **Rejected**; no independent per-axis amplitude fit |
| Strict reviewed native empty patches | A1 speck in native key3 | Raw alpha failure retained, not thresholded away |
| Software verification |8 source regressions +13 motion/component regressions;19 browser checks | Tests pass while the real painted candidate remains rejected |

The new source camera is `(6,9,5.5)`, looking at `(0,0,1.15)`, orthographic scale3.5. This is a physical rear three-quarter view, not a raster mirror or a calibrated game-direction label. The previous front view remains byte-identical. The independent camera audit checks unchanged actual world coordinates and newly projected coordinates rather than accepting view labels.

Seven native **still-image** jobs produced three body strips, one rear head, one neutral cleanup and two isolated existing-key repairs. Final review uses seven distinct clothed body drawings in eight exposures. The source samples remain0…1.3s, with the same source/game comparison clocks and600ms terminal hold as v39. No extra interpolated frames, video generation, MiniMax call or old own attack conditioning occurs.

The attempt3 native strip has a common lower-row packing offset. All four lower-row near-boot soles are463 versus486 for all four upper-row cells; one shared integer`+23Y` correction is disclosed in [packing-receipt.json](packing-receipt.json). It is not per-key fitting, a final body warp or shoe cloning. No visible foreground at alpha128 is cut; ten off-canvas alpha1 noise pixels are clipped by the row canvas, and the complete native atlas is retained. This does not rescue the separate raw-alpha failure. One shared final body matrix and a fixed`.13` rear-head scale apply to all frames. The locally packed verification atlases are explicitly not native strip outputs.

Two false-positive mechanisms are now retained as negative controls. The [superseded rectangular-ROI report](superseded-contaminated-roi-qa.json) measured part of the neighboring boot. The component-based observer now requires two separated boot components and abstains when they merge or are clipped. The [superseded phase-only report](superseded-phase-only-qa.json) passed after fitting each axis to rest/peak, despite the torso moving too far downward and too little leftward. The strict guide-fidelity check rejects the same unchanged pixels. A software pass is not an artwork pass.

Far-arm image joints, grasp/contact with a real object, per-pose head pitch, new-view proportions and all-eight-view compatibility remain unproved. The visible far hand is still too outboard to certify the intended reach; hidden wrists are not filled in from source bones. The next artwork correction must follow the fixed rear guide displacement and far-arm occlusion, rather than fitting the guide to this painting. The current view is a failed production candidate and a useful regression fixture.

All v30–v39 frozen manifests and thirteen protected W files are audited unchanged. Work and push stay on`research/modular-sprites-full-body-2026-10-11`.
