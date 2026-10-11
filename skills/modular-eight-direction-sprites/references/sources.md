# Annotated source catalog

Reviewed on 2026-10-11. This base catalog contains 55 source entries. Iteration 4 adds the [deep rig study](sprite-rig-production.md), [pinned GitHub skill comparison/audit](github-skill-study.md) and [fresh RO hard-reference audit](ragnarok-hard-reference.md); their review scopes are recorded separately. Entries are evidence for their stated scope only. Code was inspected statically; no upstream engine, model, or asset generator was executed. The original package motion study was executed separately. Publication years refer to identified artifacts rather than search-engine age labels.

Review levels: **code** = selected implementation inspected from a pinned commit; **page** = source page or retrieved document inspected; **metadata** = repository/index/abstract inspected; **limited** = indexed excerpts available but full-page retrieval failed or embedded material was not inspected. Live documentation and default-branch URLs can change.

## Game implementations and modular libraries

| ID | Source | Review and useful evidence | Limits |
| --- | --- | --- | --- |
| S01 | [Flare Entity.cpp](https://github.com/flareteam/flare-engine/blob/1969baeb89ebf94cf22e2bc2ed4e3d8413714d4f/src/Entity.cpp) | **code**. Emits layered renderables using the current direction's order; applies shared actor position. | One engine implementation, not a universal schema. |
| S02 | [Flare hero_layers.txt](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/mods/fantasycore/engine/hero_layers.txt) | **code**. Eight facing-specific equipment orders. | Legacy file naming should not dictate a new project API. |
| S03 | [Flare Animation Definitions](https://github.com/flareteam/flare-engine/wiki/Animation-Definitions) | **page**. Direction/frame grids, ground offsets, packed frame rectangles. | Wiki contains historical examples; verify current parser. |
| S04 | [Flare render8dirs.py](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/art_src/characters/render8dirs.py) | **code**. Rotates a render platform through eight captures. | Legacy Blender syntax; not a complete modular exporter. |
| S05 | [Modular isometric SciFi character for Flare](https://opengameart.org/content/modular-isometric-scifi-character-spritesheets-with-weapons-cyborg-or-android-avatar-for) | **page**. Creator describes modular sheets, eight directions, and layer configuration. | Assets were not downloaded or visually qualified. |
| S06 | [Universal LPC README](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/58ce1aa479e4df32845a73a5d0afc221c3a893c2/README.md) | **code**. Layer library, generator, authorship, and license/credits requirements. | Code and art have distinct licensing considerations. |
| S07 | [LPC constants.ts](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/58ce1aa479e4df32845a73a5d0afc221c3a893c2/sources/state/constants.ts) | **code**. Standard four-direction row order and clip mappings. | Do not label standard LPC sheets eight-direction. |
| S08 | [LPC renderer.ts](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/58ce1aa479e4df32845a73a5d0afc221c3a893c2/sources/canvas/renderer.ts) | **code**. Filters animation support and sorts rendering by z-position. | Generator composition is not an in-game wardrobe runtime. |
| S09 | [LPC contributing guide](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/58ce1aa479e4df32845a73a5d0afc221c3a893c2/CONTRIBUTING.md) | **code**. Asset definitions, layer metadata, contribution and credit conventions. | Repository-specific conventions. |
| S10 | [Mana Source Sprite System](https://doc.manasource.org/sprite_system/) | **limited**. Indexed author documentation describes sprite definitions and animation frames. | Full-page fetch failed; background lead, not a basis for exact API claims. |
| S11 | [The Mana World Playersets](https://wiki.themanaworld.org/wiki/Dev%3APlayersets) | **page**, fetched directly. Project documentation identifies four directions, frame specification, and equipment layering. | Page itself is flagged for updating; useful historical comparison, not eight-direction proof. |
| S12 | [Mana Seed Character Base](https://seliel-the-shaper.itch.io/character-base) | **page**. Creator describes a four-direction paper-doll base with matching separate sheets and dynamic layering. | Page fetched directly; advertised assets were not downloaded or tested. |
| S13 | [OpenDiablo2 composite.go](https://github.com/OpenDiablo2/OpenDiablo2/blob/7f92c571bf04057a7fbdfb5d25a486f7d775e3c3/d2core/d2asset/composite.go) | **code**. Equipment layers rendered by current direction/frame priority; common mode/frame APIs. | Archived reimplementation, not original proprietary source. Equip rebuilds mode; do not infer guaranteed phase-preserving swaps. |
| S14 | [OpenDiablo2 COF decoder](https://github.com/OpenDiablo2/OpenDiablo2/blob/7f92c571bf04057a7fbdfb5d25a486f7d775e3c3/d2common/d2fileformats/d2cof/cof.go) | **code**. Parses direction × frame × layer priorities and frame events. | Format-specific and variable direction counts. |
| S15 | [Ragnarok Research Lab ACT format](https://ragnarokresearchlab.github.io/file-formats/act/) | **page**. First-hand format documentation for anchors, layers, animation timing, and events. | Reverse-engineered documentation; version-dependent details. |
| S16 | [roBrowser EntityRender.js](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Entity/EntityRender.js) | **code**. Eight-way camera/entity facing, separate body/head/equipment drawing, direction-sensitive shield placement. | Archived client; observe architecture without assuming current compatibility. |

## Official authoring and runtime documentation

| ID | Source | Review and useful evidence | Limits |
| --- | --- | --- | --- |
| S17 | [Spine skins](https://esotericsoftware.com/spine-skins) | **page**. Grouping attachments and combining item/body skins. | Skeletal system, not automatic directional image synthesis. |
| S18 | [Spine slots](https://esotericsoftware.com/spine-slots) | **page**. Slots decouple attachment selection and drawing order; order can be keyed. | Whole-slot ordering still needs splits for within-frame crossings. |
| S19 | [Spine mix-and-match](https://esotericsoftware.com/spine-examples-mix-and-match) | **metadata/indexed author example**. Official multi-item skin workflow. | Example was not run. |
| S20 | [Unity 2D Animation Sprite Swap](https://docs.unity3d.com/Packages/com.unity.2d.animation@10.2/manual/ex-sprite-swap.html) | **page**. Part categories/labels, Sprite Library, Resolver selection. | Package 10.2 docs; verify installed package. |
| S21 | [Godot AnimatedSprite2D](https://docs.godotengine.org/en/stable/classes/class_animatedsprite2d.html) | **page**. Frame/progress state and animation-change reset behavior. | Stable URL can advance; pin project engine version. |
| S22 | [Godot CanvasItem](https://docs.godotengine.org/en/stable/classes/class_canvasitem.html) | **page**. z-index, relative z, sorting and sampling controls. | Node grouping must be designed for the project's world sorting. |
| S23 | [Phaser Container](https://docs.phaser.io/phaser/concepts/gameobjects/container) | **page**. Grouping, display-list ordering, and depth limitations for children. | Container overhead and ordering need actual runtime checks. |
| S24 | [Phaser Game Object Components](https://docs.phaser.io/phaser/concepts/gameobjects/components) | **metadata/indexed docs**. Depth and frame-related component behavior. | General depth documentation does not supersede Container child-list semantics. |
| S25 | [Aseprite CLI](https://www.aseprite.org/docs/cli/) | **page**. Layer export, tags, trims, empty-frame handling, padding. | Export recipes have not been run in this workspace. |
| S26 | [Aseprite slices](https://www.aseprite.org/docs/slices/) | **page**. Named regions and pivot information. | Define a conversion to runtime socket/anchor coordinates. |
| S27 | [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings) | **page**. Trim, packing, extrusion, and texture options. | Loader support determines usable metadata. |
| S28 | [TexturePacker CLI parameters](https://www.codeandweb.com/texturepacker/documentation/commandline/parameters) | **metadata/indexed docs**. Pivot and padding/extrusion parameters. | No local TexturePacker export was executed. |
| S29 | [Blender 4.2 Holdout shader](https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/holdout.html) | **page**, fetched directly after browser-tool retrieval failed. Transparent holdout behavior in rendering. | Holdout masks are combination-dependent; select the installed Blender manual. |
| S30 | [Blender 4.2 Cryptomatte node](https://docs.blender.org/manual/en/4.2/compositing/types/mask/cryptomatte.html) | **page**, fetched directly after browser-tool retrieval failed. Compositing selection masks and render passes. | Does not recover hidden geometry; select the installed Blender manual. |

## Developer-authored production references

| ID | Source | Review and useful evidence | Limits |
| --- | --- | --- | --- |
| S31 | [Dead Cells art pipeline deep dive](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-) | **page**. Developer explains a model-to-pixel-animation workflow and practical artifacts. | Side-view production account; no eight-direction modular-equipment claim. |
| S32 | [Broxxar animation capture](https://github.com/Broxxar/PixelArtPipeline/blob/5969589448e87cc12cd7fb0d81926c9f218a089c/Assets/Scripts/AnimationCaptureHelper.cs) | **code**. Samples clips and captures color and normal-map atlases. | Example, not a maintained complete wardrobe tool. |
| S33 | [Clint Bellanger: Isometric Tiles in Blender](https://clintbellanger.net/articles/isometric_tiles/) | **page**. Orthographic setup and eight-view rotation-script concept. | Written for Blender 2.6; tile projection is not a universal character camera. |
| S34 | [Pedro Medeiros / Saint11 tutorials](https://saint11.art/blog/pixel-art-tutorials/) | **page and visual panels**. [Walk](https://saint11.art/img/pixel-tutorials/Walk.gif) and [top-down walk](https://saint11.art/img/pixel-tutorials/TopDownWalkCycle.gif) downloaded and visually inspected during iteration 2. Coordinated contact/down/passing/up, torso/head and arm motion. | Artist examples; neither specifies a full eight-direction modular weapon pipeline. Other panels remain unreviewed. |

## Research papers, projects, and dataset code

| ID | Source | Review and useful evidence | Limits |
| --- | --- | --- | --- |
| S35 | [Sprite Sheet Diffusion v1](https://arxiv.org/html/2412.03685v1) | **page/document**. Pose/reference/temporal method, dataset and reported limitations. | 2024 preprint v1; narrow evaluation does not validate equipment interchangeability. |
| S36 | [Sprite Sheet Diffusion repository](https://github.com/chenganhsieh/Sprite-Sheet-Diffusion) | **metadata/README**. Author implementation and stated licensing. | No training, inference, or model-weight audit performed. |
| S37 | [Animate Anyone](https://arxiv.org/abs/2311.17117) | **abstract/metadata**. Character consistency and pose-controlled animation research. | No inference run; video metrics do not establish sprite registration. |
| S38 | [Transparent Image Layer Diffusion](https://lllyasviel.github.io/pages/layerdiffuse/) | **project page and abstract**. Transparency/layer-generation research, SIGGRAPH 2024. | Does not establish semantic eight-direction wardrobe compatibility. |
| S39 | [See-through paper](https://arxiv.org/abs/2602.03749) | **abstract/metadata**. Inpainted semantic anime layers with ordering, 2026. | Single-image 2.5D decomposition, not a complete multi-view sprite wardrobe. |
| S40 | [See-through author repository](https://github.com/shitagaki-lab/see-through/blob/df019de5129d6c4b406587a14c3501669441a783/README.md) | **code/README**. Author-advertised pipeline and layered PSD output; repo labels SIGGRAPH 2026 Conference Paper. | Installation, memory claims, and output quality not benchmarked. |
| S41 | [Sprite-from-Sprite](https://lllyasviel.github.io/GitPageToonDecompose/) | **project page**. Author's SIGGRAPH Asia 2022 animation-decomposition project. | No eight-view equipment contract established. |
| S42 | [Disentangled Sequential Autoencoder](https://proceedings.mlr.press/v80/yingzhen18a.html) | **publication abstract/metadata**. ICML 2018 appearance/motion factorization. | Representation learning, not an equipment authoring specification. |
| S43 | [YingzhenLi/Sprites](https://github.com/YingzhenLi/Sprites) | **metadata/README**. Authors' sprite-video dataset-generation repository. | Research dataset source; inspect upstream asset rights before reuse. |
| S44 | [CharacterShot](https://arxiv.org/abs/2508.07409) | **abstract/metadata**. Multi-view and temporal character-animation consistency. | 2025 preprint; no demonstrated replaceable 2D parts guarantee. |
| S45 | [Wong and Volino: Sprite Sheet Generation using a Diffusion Model](https://marcovolino.github.io/docs/papers/2025-wong-cvmp.pdf) | **one-page document**. Portrait-guided motion and stylization experiment. | Retrieved PDF is one page; evidence depth is limited. |

## Fresh animation study — iteration 2

| ID | Source | Review and useful evidence | Limits |
| --- | --- | --- | --- |
| S47 | [Ragnarok Research Lab animation systems](https://ragnarokresearchlab.github.io/rendering/animation-systems/) | **page**. First-hand timing experiment reports 24 ms versus legacy 25 ms intervals. | Measurements not reproduced here; internal-clock explanation is speculative. |
| S48 | [Ragnarok Research Lab camera controls](https://ragnarokresearchlab.github.io/rendering/camera-controls/) | **page**. Orbit and narrow perspective context. | Distinguish reverse-engineered settings from Astraeon's own camera choices. |
| S49 | [Ragnarok Research Lab SPR format](https://ragnarokresearchlab.github.io/file-formats/spr/) | **page**. Indexed and truecolor image segments; palette-index-zero transparency and raw alpha conventions. | Version-specific decoder behavior, not an asset license or animation timeline. |
| S50 | [Ryan Juckett: Analytic Two-Bone IK in 2D](https://www.ryanjuckett.com/analytic-two-bone-ik-in-2d/) | **page/full derivation**. Reach bounds, bend choice, invalid-target handling, planar use in 3D. | Study uses independently written geometry; no source code imported. IK alone does not establish convincing movement. |
| S51 | [Kovar, Gleicher, Schreiner: Footskate Cleanup](https://research.cs.wisc.edu/graphics/Gallery/kovar.vol/Cleanup/cleanup.pdf) | **full paper, algorithm/results read**. SCA 2002. Contact constraints, smoothing and root/knee popping; deliberately permits small length changes. | Paper implementation not reproduced. Mocap cleanup is not a sprite exporter. |
| S52 | [Current roBrowserLegacy EntityRender.js](https://github.com/MrAntares/roBrowserLegacy/blob/1370afa878ba296a6ea35f5b76eb904a2611537b/src/Renderer/Entity/EntityRender.js) | **code**. Camera-relative facing, anchor composition, body-authoritative shared walk phase. | Executable constant uses 25 while nearby comment says 24; phase caching is not proof of every layer's correct poses. |
| S53 | [Current roBrowserLegacy Action.js](https://github.com/MrAntares/roBrowserLegacy/blob/1370afa878ba296a6ea35f5b76eb904a2611537b/src/Loaders/Action.js) | **code**. ACT layers, anchors, version gates, stored-delay conversion by 25. | Reimplementation compatibility choice, not independently verified original behavior. |
| S54 | [Jonathan Cooper: animation principles in games](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games) | **limited**. Author/book excerpt identified as a relevant artistic study lead. | Current full-page retrieval returned 403; no claim of full chapter study or game-specific technique validation. |
| S55 | [GDC: Responsive movement in Just Cause 3](https://www.gdcvault.com/play/1021981/contactUs) | **metadata**. GDC 2015 session by Jeet Shroff and Alex Crowhurst identifies responsiveness/fidelity tradeoffs. | Talk/video not watched; no implementation claims derived from the listing. |

## Current vendor workflow

| ID | Source | Review and useful evidence | Limits |
| --- | --- | --- | --- |
| S46 | [Ludo eight-direction guide](https://ludo.ai/docs/sprite-generator/8-direction-sprites) | **page**. Vendor-documented matching settings and animation direction transfer. | Product workflow claim, not independent benchmark or proof of separate-part consistency. |

## Reproducibility and rights

[Source audit](source-audit.json) records 24 selected downloaded repository files, immutable commit URLs, content hashes, and retrieval date. [Repository snapshots](repository-snapshots.json) records ten repository commit snapshots; fields that were not rechecked are explicitly unset. Additional selected files support the inspection without each receiving a separate catalog entry.

Use architectural ideas and original project-owned art by default. Before admitting external art or code, check that specific material's license and attribution, including per-item credits in mixed catalogs. A repository's code license does not automatically license linked commercial game assets. Model code, weights, training data, and generated-output terms may differ. This research did not import third-party art into the game.

Search results that led to mirrors, marketing pages, or unverified agent skills were discovery leads. They are not treated as production evidence in this catalog. Claims about quality or maintenance are bounded by the actual review level above.

The follow-up [RO action-direction audit](ro-action-direction-audit.json) contains 64 actual requests across eight Swordman action blocks, including eight distinct sitting views and a preserved head-region attack discrepancy. See the [interpretation and scope](ragnarok-hard-reference.md#eight-selectable-directions-versus-four-drawings).

Iteration 5 adds [original RO-inspired art-direction practice](original-ro-art-direction.md) and its [source/read-scope audit](art-direction-source-audit.json): first-person Dead Cells production, primary Saint11 instruction, complete NotSlot text series, a pinned toon-capture example and selected silhouette-coherence paper passages. Original visual practice and a tested held-pose FX-expiry repair are linked separately from external source study.


## Iteration 6 additions

Read [pose/reference practice](pose-guide-practice.md) and its [primary-source audit](pipeline-source-audit.json). The executable CLI applies export integrity and registration findings; [external capture evidence](../../../research/sprite-animation/motion-reference-v6/README.md) distinguishes 213 actually decoded/visually reviewed samples from candidate references not studied. Mixamo documentation was read, but no account/action download or retargeting was executed.

## Iteration 7 additions

Read [conditioning/redraw practice](conditioning-and-redraw.md), [natural-motion practice](natural-motion-practice.md), and the [source/code read-scope audit](conditioning-source-audit.json). Evidence includes205actually inspected ToS video/GIF samples, a new capture-window/crop implementation,64richer original guide-map sets, and88actual fresh external Quaternius source poses sampled through Blender. The original guide board was explicitly rejected by the user as unnatural; the external rig is studied, not retargeted. No model training/ControlNet/hand-refinement execution, naturalness acceptance or final character release is claimed.
