# Pickup: source-driven modular rendering, v32

2026-10-13. User: **“ทำให้ผ่าน แล้วจดบันทึก”**. The current eight-key, one-view unarmed crouch/reach/return passes **agent motion review**. This is a bounded milestone, not user artwork approval, complete eight-direction coverage, actual object pickup, or a finished all-action factory.

- [Game-timing GIF](pickup-game-clock.gif): same eight keys, explicitly retimed to 700ms active + 600ms terminal hold.
- [Source-timing GIF](pickup-source-clock.gif): 1300ms active + 600ms terminal hold; GIF centisecond quantization disclosed.
- [Actual source versus character, interactive Canvas](rig-preview.html): select frame, play either clock once, toggle authored rig.
- [Eight-frame image review](eight-frame-review.png), [independent pixel tracks](pixel-tracks-review.png), [RGBA sheet](eight-frames.png).
- [Passing motion receipt](motion-review.json), [pixel validation](pixel-validation.json), [rig binds](rig-bind-review.json), [visual review](visual-review.json).
- [Reusable know-how](KNOW-HOW.md), [generation provenance](generation-ledger.json), [evidence audit](audit-report.json).

| Criterion | v31 whole-character redraw | v32 modular render |
| --- | --- | --- |
| Planted far/near shoe X range | 55 / 62px | **0 / 0px**, actual image matches |
| Planted far/near shoe Y range | 2 / 5px | **0 / 0px** |
| Existing support budget | 6px | 6px, unchanged |
| Held-out cuff/source recovery difference | ~0.376 | **0.005313**, maximum normalized phase error |
| Existing phase warning | 0.25 | 0.25, unchanged |
| Held-out cuff pixel match vs authored render point | Unknown | **0.782px max**; this texture family only |
| Frame count / independent poses | 8 / 8 | 8 / 8, unchanged |
| Modular painted appearance | Whole character frames | **16 actual part slots**, head+hair combined |

Three real imagegen jobs created a new part atlas, a torso repair and a closed-joint limb repair. The first atlas had embedded shoulder armor and hollow limb sockets: these are retained as authoring failures, repaired by actual imagegen. Detached alpha specks and neighboring panel fragments are removed once while extracting each shared asset; retained RGBA pixels are unchanged. No per-frame translation, scale fitting, recoloring or whole-frame warping repairs this motion.

The fresh external source remains KayKit Free1.1 **Rig_Medium_General.glb / PickUp**, 23 named bones, eight actual samples. The sprite has an explicitly authored 2D rig: source pelvis/spine/wrist curves drive moving body parts; two fixed shoe anchors and fixed-length two-bone IK keep the legs attached. Rest offsets and scale adaptations are declared in [rig-runtime.js](rig-runtime.js). These are not exact 3D-to-2D anatomical measurements. In particular source `head` drives an authored upper-body/head mount; the source has no separate neck bone.

The image observer locates toe texture and the bracer/glove junction from **only frame0** plus fixed search regions. No later rig coordinates/angles guide the search. All 24 surface observations survive uniqueness/visibility checks; the lowest NCC is 0.963 and positional margin is 0.250. Scores are texture similarities, not accuracy probabilities. Both fixed toe patches are byte-identical across all eight actual RGBA renders. Later authored wrist coordinates are used only after detection to validate this rigid-texture experiment. Hidden knee/hip coordinates remain unknown in the image; ownership is proven by bound part-parent transforms and visual attachment review separately.

Validation: **12 regression cases, 13 actual browser checks, 19 bounded motion checks**, plus the evidence audit. Negative cases reject translated shoes, missing/duplicate texture, stale images, switched leg parents, mirrored parts, wrong source times and visual acceptance transferred to different hashes. The old v31 foot/phase failures still fail the same criteria. The generic surface checker continues to report anatomy/contact/production false; the separate bounded motion review combines pixels, source/binds and an independently saved agent visual receipt. Rebuilding cannot create a fresh visual PASS for changed images.

Current scope: one left-facing three-quarter camera, one unarmed gesture. No prop/finger contact, world force/COM, separately replaceable hair, perspective bank, all-RPG motion set or game admission is approved. Exact approved W walking files and all published v30/v31 evidence remain unchanged. All work stays on `research/modular-sprites-full-body-2026-10-11`.
