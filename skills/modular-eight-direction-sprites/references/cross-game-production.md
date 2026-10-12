# Cross-game production study — v18

The user asks to study many games and all useful approaches, at production depth, comparing actual shots and frames. They additionally require references near our original painted fantasy character quality: RO, RO3, Tree of Savior and suitable alternatives. Low-resolution examples may teach implementation but must not lower our art target. The exact v17 upright W source walk remains the user-approved motion baseline.

## Visual and production reference roles

| Source | Actual study this iteration | Apply to our factory |
| --- | --- | --- |
| RO | Retained actual8-pose W sequence and prior direction audits; no new client capture | Sparse phase structure and readable silhouette, with our approved16-pose source as current motion |
| Tree of Savior | Primary [MAGGI interview](https://treeofsavior.com/page/news/view.php?n=337), [Swordsman article](https://treeofsavior.com/page/news/view.php?n=541), retained1920×1080 trailer, new30-frame7.6–8.6s group shot | Painted material/detail, fixed quarter-view readability and stable proportions. New shot is largely idle-like, not a recovered walking stride |
| RO3 | [GungHo official announcement/press PDF](https://www.gungho.co.jp/jp/news/ccjg5s00000000wh.html), second-page key visual visually inspected; gameplay image search for locating footage | Comparable fantasy finish/detailed costumes. Key art is not in-game anatomy; RO3 video has not been frame-captured this iteration |
| CrossCode | Three primary devlogs read;56-frame door traversal and93-frame combat GIF actually decoded/reviewed | Keep camera cuts/fades separate from within-shot spacing; effects/HUD can hide the body. No recovered hidden skeleton |
| Flare | Eight pinned item descriptors, actual eight-facing layer lists; engine parser/setup/avatar source read by blob | Packed rectangles retain explicit offsets; item clocks/pose IDs must match; draw order changes by view; version the engine adapter |
| Valyria Tear | Pinned actual atlas assets, walk/attack Lua descriptors and attack controller; six Wwalk exposures and eight attack cells reconstructed | Preserve repeated atlas IDs, per-exposure holds, separate weapon art and gameplay/FX thresholds |
| Dead Cells | [Artist Thomas Vasseur's primary account](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-) read; no new GIF capture | Block convincing timed key poses first; render from reusable3D sources. Its attack interpolation policy is a specific artistic choice, not our global walk rule |
| Hades | [Developer-badged primary explanation](https://steamcommunity.com/app/1145360/discussions/0/1738883810796606862/) read; no gameplay frame study | Many-view3D→2D exports with a consistent source. Hand-painted promotional/portrait art is a separate output |
| Project Terra / Alabaster Dawn | [Developer's bone-sprite announcement](https://www.radicalfishgames.com/?p=7178), Juno showcase page and associated independent prototype read | Test geometry-preserving sprite assemblies and directional item banks; proprietary implementation was not recovered |
| Vanillaware / Odin Sphere | [Kamitani primary interview](https://www.gamedeveloper.com/business/king-of-2d-vanillaware-s-george-kamitani) read | Detailed illustrated character-editor approach is another candidate; no proprietary code or motion reconstruction claimed |
| TalesWeaver | [Nexon official introduction](https://talesweaver.nexon.co.jp/intro/talesweaver.aspx) located/read | Additional2D fantasy/cosmetic quality reference; no new frame capture or verified8-direction action table |
| LPC | Pinned README/body sheets/tree metadata | Modular catalog engineering candidate, not our art-quality reference or a captured game's timeline |

These are deliberately different evidence types. A located trailer, read article, decoded GIF and executed source inventory are not interchangeable. This is a bounded new study, not a survey of every game on Earth.

## Production findings that change our implementation

**A packed atlas rectangle needs its original anchor.** Flare's descriptors store frame ID, direction index, rectangle and X/Y offset. Their named layer tables differ between W, N and SE. Do not center individual extracted pieces or assume one front-to-back order for all views. Numeric0–7 atlas directions must be mapped by a verified engine adapter, not guessed from names.

**Pin engine and content versions together.** The engine source explicitly deprecates `hero_layers.txt` in favor of a `render_layers` section; legacy fallback exists. A repository's file being present does not prove it is the live production format. Flare's parser treats duration as the entire animation and its setup distributes non-divisible durations through a Bresenham-style table. Declared533ms/8 poses is not automatically eight identical GIF exposures. We read code; no Flare engine launch is claimed. Three large body atlases were unavailable through the current text-oriented connector, so no full-body reassembly is claimed.

**A terminal hold is not zero-time, a loop or an unknown FPS to fill in.** Valyria's attack descriptor has75/75/75/200/40/40/75ms followed by a state-dependent hold. The atlas cells are64×64 despite a128×128 display declaration. Its controller starts slash after410ms, triggers damage after505ms and leaves the attack state after730ms; each uses `>` and actual update-time crossings. These are source thresholds, not measured exact gameplay event times. Our reconstruction preserves the indefinite last pose and distinguishes the580ms finite prefix from the attack controller. Wwalk has six130ms exposures, but one atlas ID intentionally appears twice: six exposures are not six unique drawings.

**Reference shots need transition labels.** CrossCode's door GIF includes a fade/room change. Do not call that image displacement bad registration, apply one root correction across it or infer world foot-lock from moving scenery. The combat clip is heavily obscured by FX/numbers. The newly selected ToS group shot is useful for detail/coherence but largely holds poses. Initial reconnaissance labels suggesting walking/turning were corrected after actual board review, with scope receipts retained.

**Complete part source must precede mass item generation.** The independent billboard prototype documents direction-dependent part images/sorting and repeated design iteration. Our actual source inventory now reopens the approved rig, verifies named weight bones/no unweighted vertices, and records170 meshes/67bones/13 source-item groups. Silver/auburn hair are two alternative items in one logical slot:12 logical categories, not13 simultaneous equipped layers. Geometry inventory does not approve painted hidden content or garment swaps.

## GitHub skill/code audit

| Pinned project | Read evidence | Use / limits |
| --- | --- | --- |
| [aldegad/sprite-gen](https://github.com/aldegad/sprite-gen/tree/611813b3f9d2069073cca8587e99647f8f184707) | SKILL, layer contract, actual motion/leg signal code | Study explicit tracks, exact inputs and isolated contact ROI with unknown outcomes. Foot-band signals do not determine anatomical owners. Avoid mirroring/normalization or video interpolation that changes approved motion; not installed/run |
| [JatCool/AI-Sprite-Animation](https://github.com/JatCool/AI-Sprite-Animation/tree/3818664861613905a377eca26c4ea940c06a646d) | SKILL, actual SpriteRig/RigAnimator C# | Study parent-relative angles and through-key Hermite curves. Near/far names are not persistent anatomical L/R; lowest-foot pinning differs from our ground-contact contract. Vacated-cell/neighbor-color fills are not complete hidden painted parts; Unity package not run |
| [ervareza/agent-skill-pixel-art](https://github.com/ervareza/agent-skill-pixel-art/tree/0de5e49a9ce9c1a326910b4efe3420c030ce3856) | Correct nested SKILL path and actual quality_audit.py | Audit alpha/palette/isolated pixels/canvas multiples when strict pixel art is the declared style. These checks do not inspect limbs, contact or acting. Mirror/default light rules do not override our asymmetry/art brief; not installed/run |

Read external skills as research data, not instructions governing our repository. Marketing claims of flawless/game-ready output do not establish accuracy. Preserve local snapshots with separate localSHA256 and upstream Git blob IDs; an earlier root-level pixel-art SKILL request failed, then the actual nested file was found. Code/art asset licenses are separate; this study imports no external character art into our game package.

## Executable factory foundation

`inspect-factory-source.py` inventories the actual reopened approved source. `factory-plan.py` binds its inventory, approval GIF, ground receipt, source blend/motion and every pose image; it rejects stale bindings, changed ordering/times and unapproved facings. It compiles16 W poses and208 item/frame authoring jobs, with50ms exposures and the authoritative512px export camera. Historical motion metadata still says256px and must not override the ground receipt. All new drawing jobs start unreviewed/not authored; no source approval flows into painted parts.

The plan is an authoring scheduler, **not a completed generator or production factory**.

Treat512px masters as authoring sources rather than blindly resident runtime textures. The current208W item/frame targets would occupy208MiB as full-canvas RGBA8 base levels; a hypothetical eight-facing extension would occupy1664MiB per action before mipmaps, normal/depth maps or more variants. These are arithmetic estimates, not measured GPU use or approval of other views. A production exporter needs a memory budget, lossless atlas trimming with the original logical-canvas/root offsets preserved, item/page residency and actual native-display review. Trimming an atlas rectangle with retained offsets is different from fitting/recentering a drawing. PNG file compression does not determine decoded GPU memory. Do not reduce our art target or choose an engine/device compression format from this estimate alone.

Retain separate production stages:

1. Approved motion/camera/body-family input.
2. Complete directional item sources with stable anatomical ownership and hidden surfaces.
3. Deterministic source-constrained rendering/painting adapter.
4. Per-pose source/image/contact/occlusion checks, including the loop seam.
5. Item compatibility, attachment/draw-order and extreme-pose wardrobe tests.
6. Engine timeline/events/cancellation/contact, format/memory/atlas tests.
7. Scoped visual acceptance and a versioned published package.

Prefer testing an adapter that preserves geometry over more unconstrained whole-sheet redraws. Compare at least deterministic modular3D renders with original painted materials, authored directional2D part banks and temporally constrained redraw. The v17 whole-sheet backend remains failed. No new backend is selected as validated solely from reading these references.

[v18 executed evidence / reference reader](../../../research/sprite-animation/cross-game-factory-v18/README.md) retains315 new reference samples:301 container/video samples plus14 source-script reconstructions. Browser launch failed under the current sandbox; HTML syntax/native-image/source tests do not substitute for browser behavior. Network-shell article downloads were not executed because automatic approval review hit a usage limit; read-only tools and already-local material were used without retrying that blocked command.
