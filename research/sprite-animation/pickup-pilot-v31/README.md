# v31 — actual pickup paintover pilot and failure-aware image checks

2026-10-13. User authorizes proceeding from v30 tools/research into one real motion pilot. We selected an unarmed **PickUp,8source samples,one fixed three-quarter camera**. Actual external source is creator CC0KayKitFree1.1, not any rejected own slash rig. Five actual imagegen calls produced five original-character sheets; all raw outputs, exact prompts/input hashes and failures are retained.

**Current result: review candidate only, NOT production-approved.** Attempt5 fixes clipped capes and improves low→rise staging, but visible shoe surfaces still move laterally and recovery frame6 differs from source-relative timing. The image tracker returns0retained surface proposals under conservative bidirectional checks; joints under cloth/armor remain unknown. We do not turn source joints or drawn colors into painted-anatomy approval.

- [Pickup GIF](pickup-review.gif):8drawings, source-sampled active clock1300ms + authored600ms terminal review pause; repeat for inspection.
- [Source GIF](source-review.gif):same8sample times/pause, actual external mannequin poses.
- [Standalone source-versus-paint viewer](source-vs-paint.html):download/open HTML locally; embedded images, frame stepping, same clock, no SVG.
- [Coordinate board](coordinate-review.png), [reach/recovery detail](reach-coordinate-detail.png).
- [Image-surface annotation/tracking viewer](image-grid-review.html):editable visible-surface proxies, anatomical joints remain unknown.
- [Measured surface failures](surface-review.json), [sampled source stability](source-support-review.json).
- [Detailed findings and next factory recipe](KNOW-HOW.md), [generation ledger](generation-ledger.json), [test audit](audit-report.json).

| Actual evidence | Result |
| --- | --- |
| Fresh source | Rig_Medium_General.glb / PickUp,23bones,8real deformed-mesh renders; no separate neck bone inferred |
| Source clock | source duration1300ms, uniform8sampling endpoints, not full native30fps export |
| Sampled source toe movement | max axis range≈0.000341source world units; not proven meters/continuous contact |
| Painted revisions |5actual generations; attempts3/4cross cell edges, attempt5does not at alpha128 |
| Packing normalization | fixed384×512cells, shared scale1, one common lower-row origin translation32px |
| Shoe surface movement | far55pxX/2pxY; near62pxX/5pxY; provisional support budget6px |
| Source-relative cuff phase | frame6difference≈0.376normalized fraction after0/3calibration; provisional warning0.25 |
| Image point tracking |0retained proposals on15held-out surface-marker targets; no painted accuracy claim |
| Release | anatomy/contact/complete interchangeable parts unapproved; no game asset admission |

The row-origin repair removes a packing discrepancy equally for all4lower-row cells, calibrated from matching neutral endpoints0/7. It is not per-frame/limb fitting and does not rescue lateral shoe movement. Original pixels/raw sheets are retained. Full source/paint body proportions differ; normalized cuff motion compares phase, not anatomical joint error.

Appearance comes from exact accepted v21Wframe00 and fresh neutral v28identity artwork. W's exact13accepted files are unchanged. Neutral identity is not an accepted motion, and the new pickups have no user approval. No old own slash poses or original rejected production-branch assets are motion inputs. All work/push stays on the sole research branch.

GIF palette/compositing is a preview on a fixed dark background; original RGBA PNGs remain available. GIF PTS quantization is10ms, with measured190/180ms holds declared in packing.json. PNG alpha interiors and complete hidden replacement-part content are not approved for shipping.
