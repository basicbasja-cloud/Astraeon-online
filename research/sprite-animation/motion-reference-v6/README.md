# External motion studies — frame by frame

These are **third-party reference studies**, separately kept outside the original character package. Their source character art is not our game's sprite material. All existing game-branch characters remain excluded. Frames keep each source sequence's fixed canvas; no per-frame recentering removes the motion being studied.

## Ragnarok community-rendered Swordman

Freshly retrieved 16 sequences: walk requests 8–15 and weapon-attack requests 80–87. Full timing, exact URLs, source SHA-256 and decoded-frame hashes are in [ro-capture-audit.json](ro-capture-audit.json).

- [All 64 walking samples](walk-all-frames-review.png): eight views × eight frames, 75 ms per sample, 600 ms per reference loop.
- [All 72 attack samples](attack-all-frames-review.png): eight requests × nine frames, 100 ms per sample, 900 ms total. Adjacent requests reuse diagonal pictures; duplicates are deliberately retained.
- Detailed SE [walk](ro/walk-SE/frames-review.png) / [attack](ro/attack-SE/frames-review.png). All source-canvas PNGs live in their action/direction folders.

These are **community renderer display timings**, not official client captures, gameplay attack-speed rules or source skeletons. Their per-direction canvas sizes vary, and they do not supply a common world-root transform. Hidden joints and grip surfaces cannot be recovered exactly from the pixels. All eight complete walk/attack sequences were inspected in the combined boards; exact-image direction reuse is independently documented by the earlier RO audits.

The walk illustrates alternating feet, bent swing knees and modest body changes. Side views clarify foot paths; front views clarify lane width. The attack separates held preparation from the brief stroke and follow-through. Its broad drawn effect hides several anatomical regions, so blindly tracing it would supply uncertain grip/arm data. These observations inform posing; they do not validate our original walk or attack.

## Other games and developer process

**King Lucas**, primary article by Art Director Antonio Pastor: [How to animate a king](https://www.devilishgames.com/en/2016/12/14/how-to-animate-a-king-who-has-lost-his-daugthers/).

- [Walk comparison 1, all 13 samples](other-games/king-lucas-walk-1/frames-review.png).
- [Walk comparison 2, all 16 samples](other-games/king-lucas-walk-2/frames-review.png).
- [Shading comparison, all 26 samples](other-games/king-lucas-texture-comparison/frames-review.png).

The GIFs are labeled by their source filenames; the page discusses a before/after change without explicit per-image labels. The author describes a more purposeful walk, fewer attack frames for stronger impact, segmented sprites and direction-specific work to avoid mirrored weapon/one-eyed-character errors. We downloaded/decoded/visually inspected these three GIFs, not the whole game or the embedded video. The hero's stronger alternating leg movement and upper-body acting are useful here; its short-legged side-view proportions are not an eight-direction skeleton template. The container's 30 ms exposures are not our target body cadence.

**Fyna**, primary [developer improvement article](https://www.indiedb.com/games/fyna/news/devblog-20-animation-improvements-2).

- [Rough rig/reference, all 11 samples](other-games/fyna-rough-guide/frames-review.png).
- [Drawn refinement, all 11 samples](other-games/fyna-finished-guide/frames-review.png).

The developer explains rough rig motion as a starting guide for frame drawing and cloth/hair detail. Some GIF samples declare **zero delay**. We preserved their samples but left overall display time unknown, rather than inventing an FPS. The actual original decoded canvas is 1712×2169. Git keeps reduced study derivatives with a separate [sampling/hash record](other-games/fyna-rough-guide/published-sampling.json); the full decoded captures remain in the local study. `capture.json` hashes full original decoded images, so use `published-sampling.json` for the reduced PNGs. These are original-to-refinement studies, not imported source armatures or new modular game assets.

In total this archive studies **213 decoded samples**: 136 RO, 55 King Lucas and 22 Fyna. Sample count is research coverage, not proof of skill mastery. Tree of Savior's primary hair/FX articles were additionally read; the Wakfu lead animator portfolio was located. Wakfu trailers, Final Fantasy Tactics, Disgaea and Mixamo action files have **not** been frame-studied or retargeted in this iteration.

## Reuse the extraction method

Use the [capture command](../../../skills/modular-eight-direction-sprites/scripts/README.md) with a local GIF/APNG or video and its exact source URL. It retains every sample, canvas and available presentation time. It emits an **empty** anatomical-landmark template for explicit observations; it does not claim to recover a hidden skeleton from a chibi sprite.

For the authoritative **original** skeleton, see [the 64 source-rig guide poses](../pipeline-v6/pose-guide-review.png). [Pose-guide practice](../../../skills/modular-eight-direction-sprites/references/pose-guide-practice.md) explains when to use external visual observations, when to use source-known joints, and why a palm/finger inspection and art review are still required.
