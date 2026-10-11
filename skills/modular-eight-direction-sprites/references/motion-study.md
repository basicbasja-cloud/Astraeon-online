# Fresh motion study and practical findings

Iteration 2, 2026-10-11. This study prioritizes animation because the user accepts the broad art direction and rejects all existing character assets. Research inputs are public primary sources, permitted newest-branch technical contracts, and newly authored diagnostic geometry.

## Ragnarok-specific findings

[ACT documentation](https://ragnarokresearchlab.github.io/file-formats/act/) separates sprite-image indices from pose layers, transforms, anchors, and clip timing. Treat image dimensions and logical registration as different concerns. A child part can attach through the difference between the body's anchor and its own anchor; do not center it by opaque bounds.

[SPR documentation](https://ragnarokresearchlab.github.io/file-formats/spr/) identifies indexed and truecolor image storage. Palette index zero supplies transparency for indexed sprites; palette alpha is ignored, while the truecolor segment contains raw alpha. Those legacy decode rules are distinct from a new PNG export's declared alpha convention. Palette swapping can vary color, but it cannot supply new costume geometry or missing poses.

[Ragnarok Research Lab's timing experiment](https://ragnarokresearchlab.github.io/rendering/animation-systems/) reports 24 ms per stored ACT interval and explains why the traditional 25 ms approximation is difficult to distinguish in short clips. Its internal-clock explanation is a hypothesis. This package did not reproduce the original-client measurements. ACT interval counts are neither FPS nor a rule that every drawn pose lasts 24 ms. For new assets, store explicit durations with units; preserve a declared compatibility convention when importing legacy files.

The archived roBrowser implementation uses common elapsed time but special frame selection for idle body poses and head look blocks. The current [roBrowserLegacy renderer](https://github.com/MrAntares/roBrowserLegacy/blob/1370afa878ba296a6ea35f5b76eb904a2611537b/src/Renderer/Entity/EntityRender.js) additionally caches distance-driven walking phase. Its [ACT loader](https://github.com/MrAntares/roBrowserLegacy/blob/1370afa878ba296a6ea35f5b76eb904a2611537b/src/Loaders/Action.js) multiplies intervals by 25; the renderer's executable walk constant also uses 25, although a nearby comment says 24. Record executable behavior separately from comments. Neither reimplementation establishes proprietary source behavior.

Inference for the new pipeline: one authoritative phase, explicit per-part pose mapping, camera-relative view selection, and authored anchors. Different source-image counts are allowed; independently advancing part clocks are unsafe. Static head art can move with an animated socket without needing a duplicate head bitmap for each pose.

## Grounding and coordinated movement

Pedro Medeiros' [walk panel](https://saint11.art/img/pixel-tutorials/Walk.gif) was visually inspected. It connects contact, down, passing, and up poses to body/head motion, opposing arm swing, and planted-leg travel. His [top-down panel](https://saint11.art/img/pixel-tutorials/TopDownWalkCycle.gif) shows depth stacking, arm/leg opposition, reduced rear-view bounce, and the importance of hand/foot key points. These are artist examples, not a universal frame count or an eight-direction weapon system. Mirroring an unarmed tutorial is not permission to reverse weapon handedness.

For a straight translating character, the stance relation is:

```text
world_foot(t) = world_root(t) + facing_rotation * local_foot(t)
d(world_foot)/dt = 0 during a declared plant
```

This is a contact constraint, not a requirement to freeze the whole body. The hips can lower after contact, rise through passing, shift weight, and counter-rotate the shoulders while the planted foot remains anchored. A comfortable restrained gait fits the stated game direction better than gratuitous whole-image wobble. Exact amplitudes, duty ratio, and cadence are art decisions; the study's values are arbitrary diagnostic choices.

[Ryan Juckett's analytic IK derivation](https://www.ryanjuckett.com/analytic-two-bone-ik-in-2d/) explains reach bounds, bend choice, clamping, and invalid-target reporting. The study implements its own plane-constrained triangle construction, with fixed bone lengths and no imported solver code. It does not model joint limits, heel/toe roll, balance, or cloth.

The full [Kovar, Gleicher, and Schreiner footskate paper](https://research.cs.wisc.edu/graphics/Gallery/kovar.vol/Cleanup/cleanup.pdf), SCA 2002, was downloaded and its algorithm/results sections read. It warns that independent contact correction can introduce root and knee popping. Its solution blends adjustments through neighboring frames and allows small leg-length changes. That deliberate tradeoff differs from this study's fixed-length solver. Transfer the need for accurate contact labels and smooth activation/release; do not claim its entire cleanup algorithm was implemented. Offline look-ahead smoothing is not a free responsiveness improvement for player controls.

## What the original exercise demonstrated

The [motion lab](../studies/motion-lab/README.md) constructs idle, walk, and one planted attack from a fresh segmented mannequin. It displays all eight views from one sampled pose, supports hats, coat color, weapon and shield swaps, and exposes continuous versus eight-held-pose playback. It never loads the game's character assets.

Twelve automated tests passed. They cover stance drift across four gait cycles/eight directions, toe-off/landing position and velocity continuity, fixed bone lengths/reachability, invalid IK targets, full-body participation, attack foot plants, loop closure, camera-relative projection, phase-preserving appearance changes, explicit part-image phase maps, higher-rate sampling, and exact attack landmark retention. Dense clip checks sampled 1,000 poses per action. A boundary test found that the usual positive-modulo expression perturbed an exact phase landmark; the implementation now avoids the unnecessary addition for positive remainders.

Chromium checks used real controls. The latest normal/quarter clock rates measured approximately 1.003 and 0.249, with no page errors. Paused mid-walk and mid-attack swaps retained exact elapsed time. Screenshots were inspected: all eight azimuths appear, left/right boot identities remain consistent, hats follow the head, and weapons/shields follow the hands. These observations do not establish a pleasing Ragnarok-like drawn animation, pixel-level occlusion correctness, or gameplay readiness.

## Export quantization is a separate problem

The continuous gait cancels root travel during stance. Holding its sampled pose while the game root continues moving breaks that cancellation. A simple diagnostic estimate is:

```text
maximum additional stance drift ≈ projected_root_speed * pose_hold_duration
```

For this study, stride is .68 units/cycle and duration .8 seconds. Eight equal holds last .1 seconds, producing up to .085 units of local forward drift before the next update. At 132 px/unit, that is 11.22 pixels for the side view; at the 46° front view it is about 8.07 pixels. This is an analytic bound for the study, not an in-game benchmark. Tests explicitly demonstrate the failure rather than approving the eight-pose export.

An initial constant-speed sampling estimate for pixel budget B is `N >= projected_cycle_travel / B`. With a one-pixel side-view budget at this study's display scale, that estimate gives 90 holds. Ninety frames is not a recommendation: it exposes a mismatch between large diagnostic scale, fast travel, and an overly strict held-pose budget. Evaluate at the real native scale/zoom; choose pose spacing, visible foot landmarks, cadence, velocity matching, and any reviewed contact correction together. Extra frames can still carry wrong contact anatomy.

For a frame sprite, record contact points per pose and measure in the actual runtime. For a skeletal renderer, smooth contact constraints and maintain reachable targets. For both, test corners and interruptions: constant-heading grounding is not proof that a rotating character retains its contact target.

## Higher FPS is the project direction

The user explicitly wants higher animation FPS than classic Ragnarok. Eight directions describe view coverage, not eight frames or an eight-FPS ceiling. Distinguish the game render/update rate, the source-pose sampling rate, and authored per-pose durations. The lab now compares a continuous rig, a deliberately sparse eight-pose diagnostic, and 30/60 FPS pose targets. Neither target is a verified game render rate.

For the .8-second study walk:

| Pose-rate policy | Poses per direction | Maximum additional hold drift at 64 px/unit | Raw RGBA8 memory per 128² part, eight directions |
| --- | --- | --- | --- |
| Eight-pose diagnostic | 8 | 5.44 px | 4 MiB |
| 30 FPS target | 24 | 1.81 px | 12 MiB |
| 60 FPS target | 48 | .91 px | 24 MiB |

These are bounded study calculations, excluding pixel rounding, trims, compression, mipmaps, masks, depth maps, and runtime overhead. At a larger display scale or faster actual travel, remeasure. The continuous pose is identical across policies; sampling density changes. More poses reduce hold error, while silhouette, weight and contact anatomy still need authored review.

Keep action duration and landmarks independent from pose density. The .72-second attack's 60 FPS target has 44 evenly spaced samples plus three exact authored landmarks, yielding 47 poses. Adding anticipation-end/contact/recovery times produces shorter local holds without changing total duration. Gameplay damage remains a simulation event, not a texture frame event. Idle may intentionally hold fewer distinct images; record that policy rather than claiming every action has 60 unique poses per second.

## Separate-part export and compositing exercise

The new offline exporter rasterizes the original geometry into aligned 128² RGBA PNGs, root `(64,104)`, at fixed 46° diagnostic elevation. Body, hat, weapon and shield each retain full independent visible geometry plus a compressed signed-integer per-pixel depth map. A depth compositor chooses the nearest opaque surface; it can handle regions where a weapon crosses both behind and in front of the body. Parts are not cut out of a flattened reference.

The canonical variant has a complete 48-pose walk and 47-pose attack across all eight directions, plus two deliberately sparse idle holds. Stress variants cover declared pose subsets; missing equipment is represented by explicit blank images. Encoded part images and depth maps are decoded before comparing their reconstruction with the full reference. Additional substitutions combine independently rendered equipment with another body's appearance, and combinations are checked at selected walk/attack phases.

A geometry-bounds check caught clipped toes in the first export layout. Every source piece now uses the corrected shared root, and the bounds test runs before export. Reconstructing the same clipped reference would otherwise have hidden that mistake. See [export report](../studies/motion-lab/evidence/export-report.json) for the completed counts and limits.

The corrected run passed 856 decoded reconstruction/substitution comparisons and 448 additional combination checks. It wrote 4,240 frame PNGs, retained 24 explicitly blank equipment frames, and verified that all sampled geometry fits the common canvas. The generated dataset remains separate from the game. Native previews were visually inspected after export.

This proves a bounded binary-alpha geometric composition method. It does not prove antialiased edges, translucent wings/hair, a production GPU compositor, arbitrary body proportions, final pixel art, or target-game integration. A production pipeline must choose and test splits/masks versus depth composition; it should not ship these diagnostic depth buffers by default. The 3D geometry itself supplies hidden surfaces here; AI decomposition of a painted image would require a separate hidden-content solution.

## Competency ladder

| Stage | Required proof | Current evidence |
| --- | --- | --- |
| Technical research | Primary sources, pinned code, qualified claims | Established for selected sources; many paper entries remain abstract-level |
| Continuous motion mechanics | Full-body gait, reachability, contact continuity, eight views | Original diagnostic study passes its bounded checks |
| Drawn pose design | Fresh identity, convincing silhouettes and weight at native size | Unproven; mannequin is not an approved character |
| Sprite export | Registered separate RGBA parts, correct timing, blanks and trims | Untrimmed original diagnostic exports verified; production art/packing untested |
| Modular compositing | Match reference across combinations, crossing surfaces and hidden coverage | Opaque geometric depth composition verified; translucent/painterly and GPU cases untested |
| Runtime behavior | Actual camera, starts/stops/turns, combat interruptions, live swaps | Study swaps tested; actual game integration/transitions untested |
| Production confidence | Repeated successful new items/actions with documented acceptance | Not yet established |

Continue with the first unproved stage, then repeat across another action/item family. Study a source to resolve a concrete failure, apply the lesson in an original exercise, preserve the evidence, and update the skill. Source counts and self-declared mastery are not acceptance criteria. New animation approval must come from its demonstrated behavior and the user's visual standard.
