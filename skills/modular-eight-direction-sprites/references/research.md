# Research dossier: eight-direction modular 2D characters

Reviewed: 2026-10-11. Scope: independently replaceable appearance and equipment, eight facings, coherent animation, and a repeatable authoring/export/runtime process. This is a bounded survey across primary repositories, author documentation, research publications, and developer-authored tutorials, not an exhaustive search of the internet.

The initial research was engine-neutral. Subsequent user instruction establishes a heavily Ragnarok-inspired game, acceptable broad art direction, and rejected character assets in every branch. Earlier asset observations are superseded. The new iteration studies permitted technical contracts at the newest branch and external primary sources, with fresh diagnostic geometry. The game was not modified. Read [binding constraints](user-constraints.md) and [motion findings](motion-study.md) before applying this dossier.

## What the evidence supports

The strongest match is a paper-doll system whose pieces share a pose contract. That contract includes more than image dimensions: direction, animation phase, root placement, compatibility, visibility, and draw order all have to agree. A sprite generator that makes attractive eight-view turnarounds does not by itself provide interchangeable equipment.

**Flare is a direct eight-direction reference.** Its animation documentation describes direction rows, frame columns, and ground offsets; its game data changes the order of equipment slots by facing; the engine reads directional layer definitions when emitting renderables. The creator of a modular Flare asset set explicitly supplies 32 animation frames across eight directions. These are concrete examples of the requested combination. [Flare animation format](https://github.com/flareteam/flare-engine/wiki/Animation-Definitions), [directional equipment order](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/mods/fantasycore/engine/hero_layers.txt), [modular asset example](https://opengameart.org/content/modular-isometric-scifi-character-spritesheets-with-weapons-cyborg-or-android-avatar-for).

**OpenDiablo2 demonstrates finer ordering.** Its COF decoder constructs a direction × frame × layer priority table, and its composite renderer uses that table to draw equipment layers. This is evidence for frame-specific occlusion rather than one fixed order for an entire character. It is an archived reimplementation, not Blizzard's original source and not a reusable license for Diablo art. [COF decoder](https://github.com/OpenDiablo2/OpenDiablo2/blob/7f92c571bf04057a7fbdfb5d25a486f7d775e3c3/d2common/d2fileformats/d2cof/cof.go), [composite renderer](https://github.com/OpenDiablo2/OpenDiablo2/blob/7f92c571bf04057a7fbdfb5d25a486f7d775e3c3/d2core/d2asset/composite.go).

**LPC demonstrates catalog-driven compositing.** Its current source declares the standard four-direction row order, filters items by supported animations, and sorts render calls by part z-position. This supports metadata-driven composition and coverage declarations. It does not establish a universal eight-direction format. Asset licenses and authorship are tracked individually. [Direction and animation constants](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/58ce1aa479e4df32845a73a5d0afc221c3a893c2/sources/state/constants.ts), [renderer](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/58ce1aa479e4df32845a73a5d0afc221c3a893c2/sources/canvas/renderer.ts), [project README](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/58ce1aa479e4df32845a73a5d0afc221c3a893c2/README.md).

**Mana Seed is a useful artist-authored production comparison.** Its creator describes four-direction paper-doll sheets with matching layouts, and notes that some bow equipment must change between front and back layering during animation. This reinforces the need to fit replacement art to a common sequence and review ordering through the action. It is a four-direction library, not ready-made diagonal art. [Creator's Character Base page](https://seliel-the-shaper.itch.io/character-base).

**Ragnarok-style anchors solve another part of the problem.** The ACT format documentation describes head, weapon, shield, and headgear positioning relative to the body. The archived roBrowser implementation provides a separate inspectable rendering reference. The practical inference is to preserve an explicit attachment coordinate system instead of aligning separate images by their visible centers. [ACT format](https://ragnarokresearchlab.github.io/file-formats/act/), [roBrowser entity rendering](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Entity/EntityRender.js).

## Four production approaches

| Approach | Works well when | Main cost or limitation | Recommended role |
| --- | --- | --- | --- |
| Aligned frame layers | Pixel clusters and pose silhouettes need direct artistic control | Each new shape must fit all supported poses | Default for strict pixel-art paper dolls |
| Directional cutout/skeletal rigs | Painted pieces, reusable motion, and smooth deformation fit the style | Rotation through depth still needs view-specific art and ordering | Strong option for high-resolution 2D |
| Modular 3D rig rendered to 2D | Many directions, actions, and variants make repeat rendering valuable | Rig/camera setup, mask strategy, and final pixel/paint cleanup | Strong option for larger equipment catalogs |
| AI-assisted images or sequences | Concepts, turnarounds, references, or draft animation need acceleration | Identity, temporal, geometric, and layer consistency remain review tasks | Assisted authoring with deterministic export and checks |

These approaches are compatible. A 3D rig can establish exact poses; an artist can draw frame layers over them; an AI-assisted pass can propose textures; the runtime can still use aligned 2D pieces. Choose based on acceptable style and total asset count rather than insisting on one tool.

Spine's slots, skins, and mix-and-match examples provide established skeletal mechanisms for replaceable attachments and keyed draw order. Unity's Sprite Swap samples use Sprite Libraries and Resolvers for changing character parts. Neither system automatically invents eight directional views of a flat image. [Spine skins](https://esotericsoftware.com/spine-skins), [slots](https://esotericsoftware.com/spine-slots), [mix-and-match](https://esotericsoftware.com/spine-examples-mix-and-match), [Unity samples](https://docs.unity3d.com/Packages/com.unity.2d.animation@10.2/manual/ex-sprite-swap.html).

Dead Cells' developer describes a 3D-to-pixel-sprite production pipeline. This is useful evidence for rendering animations from models, but the article is not evidence of an eight-direction replaceable-equipment system. Broxxar's example captures sampled animation into color and normal atlases. Flare's art-source script loops over eight render-platform rotations. Together they motivate a modular capture pipeline that needs its own equipment and occlusion extension. [Dead Cells developer account](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-), [capture example](https://github.com/Broxxar/PixelArtPipeline/blob/5969589448e87cc12cd7fb0d81926c9f218a089c/Assets/Scripts/AnimationCaptureHelper.cs), [Flare render script](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/art_src/characters/render8dirs.py).

## What research contributes—and what remains unproven

| Primary research | Relevant contribution | Boundary for this task |
| --- | --- | --- |
| [Sprite Sheet Diffusion](https://arxiv.org/html/2412.03685v1) (2024 preprint, inspected v1) | Appearance reference, pose guidance, and temporal modeling for sprite sequences | Small dataset; no demonstrated complete eight-direction interchangeable-part contract |
| [Animate Anyone](https://arxiv.org/abs/2311.17117) (2023 preprint; later CVPR 2024) | Reference-guided, pose-controlled character video | Temporal video quality does not establish discrete pixel or equipment correctness |
| [Transparent Image Layer Diffusion](https://lllyasviel.github.io/pages/layerdiffuse/) (SIGGRAPH 2024) | Generating transparency and image layers | Transparency alone does not enforce named equipment, shared rigs, or eight-view consistency |
| [See-through](https://arxiv.org/abs/2602.03749) (2026) | Semantic, inpainted anime layers with inferred ordering | A single-image 2.5D decomposition is not a verified eight-view animation wardrobe |
| [Sprite-from-Sprite](https://lllyasviel.github.io/GitPageToonDecompose/) (SIGGRAPH Asia 2022) | Decomposing cartoon animation into reusable sprite components | No established mapping to the required directional body/equipment matrix |
| [Disentangled Sequential Autoencoder](https://proceedings.mlr.press/v80/yingzhen18a.html) (ICML 2018) and [Sprites dataset](https://github.com/YingzhenLi/Sprites) | Separating persistent appearance from changing motion in sequential data | Learned appearance factors are not production-ready editable equipment layers |
| [CharacterShot](https://arxiv.org/abs/2508.07409) (2025 preprint) | Consistency across character motion and multiple views | No demonstrated replaceable 2D equipment interchangeability guarantee |
| [Wong and Volino, Sprite Sheet Generation using a Diffusion Model](https://marcovolino.github.io/docs/papers/2025-wong-cvmp.pdf) (2025) | Portrait-to-sprite sequence workflow and stylization comparison | Retrieved artifact is one page; do not describe it as a fully inspected long paper |

The inference from these sources is that **appearance, pose, time, view, and decomposition are distinct constraints**. Combining tools that address each constraint is promising, but their guarantees do not automatically compose. The skill should require a visual/runtime proof for the combined output.

The inspected Sprite Sheet Diffusion v1 describes 16 characters and 75 action sequences, acknowledges subject-consistency limitations, and includes future work. Its reported metrics are not a validation suite for seams, socket alignment, handedness, or equipment occlusion. Its repository was located; training or inference was not run. The See-through repository advertises semantic layer extraction and provides code, but this survey did not install or benchmark it. [SSD v1](https://arxiv.org/html/2412.03685v1), [SSD code](https://github.com/chenganhsieh/Sprite-Sheet-Diffusion), [See-through code](https://github.com/shitagaki-lab/see-through).

Ludo's own documentation describes matching settings and transferring an animation to other directions. This is a useful vendor-documented workflow, not independent evidence that exported layers are interchangeable. No paid generation service was used or benchmarked. [Eight-direction guide](https://ludo.ai/docs/sprite-generator/8-direction-sprites).

## The recommended system

The following is an engineering proposal synthesized from the sources, not a format copied from one engine.

1. Define a canonical body family and approved eight-view turnaround.
2. Author one pose timeline for every action/grip family, with exact phase landmarks.
3. Produce replacement parts against those poses in a shared source coordinate system.
4. Represent gameplay items as one or more render pieces with explicit coverage rules.
5. Store facing order plus frame overrides; split pieces when one ordering value cannot express a crossing.
6. Keep untrimmed authoring coordinates; carry trim offsets into shipping atlases.
7. Sample one animation clock, then resolve all equipped pieces atomically.
8. Review every supported pose and stress combination at actual game scale.

The first proof should be small enough to expose failures cheaply: one body, two torso items, two head items, a sword and shield, eight facings, idle/walk, and an attack if combat is required. Include an intentionally awkward combination such as long hair under a helmet or a sword crossing the torso. Expand only after registration and occlusion work.

## Hard production problems

**Hidden geometry.** A pixel mask from a flattened drawing contains visible pixels only. Removing a jacket can expose anatomy that was never drawn. A separated arm may also need pixels under the shoulder seam. Generate or author those pixels, or declare restricted combinations. Inpainting is a proposal that must be checked, not a factual recovery of hidden anatomy.

**Crossing surfaces.** A long weapon can be behind the torso at one end and in front of a hand at the other. Directional ordering helps, and frame-specific ordering helps further, but neither solves all within-frame crossings. Use multiple render pieces, coverage masks, or validated per-pixel depth composition.

**Mask validity.** Visibility extracted while wearing one large shoulder pad may fail with a small shoulder pad. Distinguish reusable full geometry from already-clipped visible content. A canonical visibility mask is only reusable within the combinations for which it was designed.

**Lighting consistency.** Isolated 3D renders can lose cast shadows and inter-part ambient occlusion. Conversely, a render captured with a particular shield can bake its shadow into the body. Decide which interactions are stylized away, authored as variants, or reconstructed, then compare assembled parts with a full reference render.

**Handedness and mirroring.** Anatomical left/right remain fixed even when screen position changes. Mirroring can change weapon hands, shield placement, text, asymmetric armor, or light direction. Approve mirroring per rig/item family and transform sockets/ordering accordingly; do not assume all eight views can be derived from five.

**Timing.** Equal average frame rates do not align contact phases. Different source-image counts can work with explicit pose maps and anchors sampled from one authoritative phase. A cosmetic swap must reuse the current pose rather than restart just one layer. Changing weapon grip can require a deliberate state transition.

**Coverage and body families.** Clothing that fits one torso shape does not necessarily fit another. A shared nominal resolution is insufficient. Support explicit rig families or supply adapter/variant art with actual validation.

## Scale and performance

Illustrative arithmetic, not a benchmark: with eight facings and idle=2, walk=8, attack=6 frames, one visual piece requires 128 logical poses. Twenty variants of that piece require 2,560 poses before deduplication. A gameplay item split into two render pieces adds two image sequences, although some images may be blank or shared.

If six slots have five choices each, complete pre-rendering would require 15,625 outfits. Independent parts require 30 item variants plus the base and any additional render-piece splits. Compatibility limits reduce valid combinations; new grip families and baked lighting interactions can increase production cost.

For an uncompressed RGBA8 illustration at 128 × 128 pixels, 128 full frames occupy 8 MiB before packing, mipmaps, extra maps, or engine overhead. Twenty such variants total 160 MiB. PNG file size is not decoded texture memory. For other dimensions/formats, recalculate rather than reusing this figure.

Start with direct layered rendering. Cache complete appearances only when measurements justify it; include rig version, equipment, palette, clip/pose or sequence identity, and render policy in cache keys. Use bounded eviction. Do not store every possible outfit by default. World sorting, atlas switches, masks, and blend modes determine actual draw cost; a texture atlas alone does not guarantee one draw call.

## Relation to Astraeon

Use the [newest-branch technical brief](astraeon-technical-brief.md). The obsolete local checkout and every branch's character assets are excluded as reference. The newest observed branch is pinned at `562dfe0e163e96c26189db165e6b2be28a10c5dc`; its technical contracts establish the camera and five combat slots. Preserve those contracts while separating appearance selection from gameplay equipment. No individual character seed or animation is approved.

## Evidence and outstanding decisions

The initial pass reviewed nine repository snapshots and 21 selected source files. Iteration 2 adds a current roBrowserLegacy snapshot and three pinned source files, first-hand Ragnarok timing/camera documentation, visually inspected animation tutorial panels, a full footskate paper, and an original motion/browser exercise. Source hashes and review levels distinguish inspected evidence from search leads. No upstream game or research model was built or executed. Search/open logs and source snapshots are retained under `/workspace/scratch/sprite-research/` for traceability.

Remaining production decisions include a fresh approved identity/turnaround, native size, body families, exact cosmetic coverage, action/grip scope, and capture/billboard policy. Broad direction and technical equipment slots are already known. Continue studies against measurable failures without requesting these decisions repeatedly. The full [source catalog](sources.md), [asset contract](asset-contract.md), and [recipes](production-recipes.md) accompany the skill.
