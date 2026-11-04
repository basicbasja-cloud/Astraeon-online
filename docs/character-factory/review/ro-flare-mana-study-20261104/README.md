# RO, Flare and ManaPlus comparison using Craft Anything

## Scope and actual execution

This study combines manual source reading, pinned animation-data inspection, Craft Anything 0.3.0 source inventories, and real Chromium website/public-renderer captures. It does **not** claim that all three full game clients were installed, logged in or played. Source and asset licenses are distinct. No third-party game art or engine code is imported into Astraeon's character pipeline.

Craft Anything inventories four bounded source sets (RO client, Flare engine, Flare animation data, ManaPlus client). A fresh replay downloaded the same eighteen source/license files with identical SHA-256 values. [Source manifest](source-manifest.json) includes exact revisions, URLs, sizes and hashes. Its results verify file identity, not the correctness of our semantic interpretation.

## Findings relevant to the factory

| Reference | Verified behavior | Use for Astraeon |
|---|---|---|
| RO via Goro | Separate head, weapon and weaponLight views; action/direction/body-motion bindings; action/motion-dependent drawing order; head motion has its own selection policy | Keep same-pose equipment binding and explicit front/back FX. Review head policy rather than assuming all layers have identical frame indices in RO. |
| Flare | Each direction/frame stores atlas rectangle plus render offset; per-action duration and explicit `play_once`, `looped`, `back_forth`; animation state can be synchronized | Trimming must preserve origin/offset. A changing image rectangle is not itself size drift. Test one-shot recovery separately from looping movement. |
| ManaPlus/The Mana World client | Compound parts receive the same action, direction and update time; the renderer applies per-frame and imageset offsets | Switch all compatible parts together; draw from a common actor anchor; preserve authored offsets through extraction and atlas packing. |

### RO source and public visual sample

Goro revision `33389d39e7a0e6ede2fd277b5b93afad02708b0e`:
[render.go](https://github.com/kivutar/goro/blob/33389d39e7a0e6ede2fd277b5b93afad02708b0e/game/sprites/render.go),
[attack.go](https://github.com/kivutar/goro/blob/33389d39e7a0e6ede2fd277b5b93afad02708b0e/game/sprites/attack.go),
[assets.go](https://github.com/kivutar/goro/blob/33389d39e7a0e6ede2fd277b5b93afad02708b0e/game/sprites/assets.go).
`AttackActionFamily` selects player attack variants based on weapon-related action metadata. `drawFallbackHumanoidLayers` composes separate body/head/equipment/light views and uses frame-dependent order. These functions are implementation evidence, not a first-party account of RO's original painting process.

Craft Anything opened the public ragassets renderer requesting `job=1&head=1&weapon=1&action=40`. [Screenshot](ro-attack.png), [browser evidence](ro-attack-evidence.json), [request parameters](ro-attack-params.json). The primary GIF request returned HTTP 200; the unrelated favicon returned 404. The downloaded GIF has five frames, a fixed 63×89 canvas and 100ms exported delays; [analysis and hash](ro-gif-analysis.json). The original GIF remains temporary, not a vendored character asset. A still capture and the requested weapon parameter do **not** prove the correct sword/trail was visible, and a looping exported GIF does not prove attacks loop in the game. No RO blade-sweep geometry is certified by this sample.

The [ragassets documentation](https://github.com/adsonpleal/ragassets#understanding-action-animations--directions) describes action-family × 8 + direction indexing. Eight index slots do not establish eight independently painted unique poses or a universal four-direction attack rule. Keep the owner's four authored attack/cast directions for Astraeon; do not change that decision based only on a file-format index.

### Flare: offset and timing evidence

Engine revision `f9a17a266293a897a1d7eae2d54408b0de39af27`:
[Animation.cpp](https://github.com/flareteam/flare-engine/blob/f9a17a266293a897a1d7eae2d54408b0de39af27/src/Animation.cpp),
[AnimationSet.cpp](https://github.com/flareteam/flare-engine/blob/f9a17a266293a897a1d7eae2d54408b0de39af27/src/AnimationSet.cpp).
`addFrame` records the frame rectangle and its offset; `getCurrentFrame` returns both; `advanceFrame` distinguishes one-shot, loop and back/forth behavior. The engine's duration distribution code even notes a limitation for non-even frame timing, so its implementation is not a blanket smoothness guarantee.

Game-data revision `af6eee6d339ac98011864bfe89da837fe7769c28`:
[male longsword](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/mods/fantasycore/animations/avatar/male/longsword.txt),
[female longsword](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/mods/fantasycore/animations/avatar/female/longsword.txt).
Both sampled files specify run = 8 frames / 533ms / looped, swing = 4 frames / 400ms / play_once, and cast = 4 frames / 400ms / play_once. Each swing has 32 frame/direction records (4×8) and 32 distinct offsets. Across those directions the male sword rectangles vary from 17–145px wide and 47–175px high; female 44–155px wide and 62–190px high. See [parsed data summary](flare-animation-summary.json). These are packed sword-layer rectangles, not whole-character heights or a recommendation to reduce Astraeon's frame count.

Craft Anything captured the [official Flare website](https://www.flarerpg.org/), including its published game screenshots: [capture](flare-site.png), [evidence](flare-site-evidence.json). This is website inspection, not a running Flare game session. No character-sheet playback was reconstructed here.

### ManaPlus: shared state, authored offsets

Revision `40ebe02e81b34f5b02ea682d2d470a20e7e63cfc`:
[CompoundSprite](https://github.com/ManaPlus/ManaPlus/blob/40ebe02e81b34f5b02ea682d2d470a20e7e63cfc/src/being/compoundsprite.cpp),
[AnimatedSprite](https://github.com/ManaPlus/ManaPlus/blob/40ebe02e81b34f5b02ea682d2d470a20e7e63cfc/src/resources/sprite/animatedsprite.cpp),
[SpriteDef](https://github.com/ManaPlus/ManaPlus/blob/40ebe02e81b34f5b02ea682d2d470a20e7e63cfc/src/resources/sprite/spritedef.cpp).
CompoundSprite distributes play/direction/update calls to its component sprites. SpriteDef loads delays and combines frame/imageset offsets; AnimatedSprite draws at actor position plus the stored offsets. This supports compatible authored layers, not arbitrary swapping between unrelated pose sequences.

Craft Anything loaded the [official client site](https://manaplus.org/): [capture](mana-site.png), [evidence](mana-site-evidence.json). The separate attempt to open its screenshots anchor failed during the walkthrough; see [failed attempt](mana-screenshots-evidence.json). Do not describe the homepage as gameplay or that failed attempt as a successful visual comparison.

## Decisions for our current work

1. Preserve the original tall Swordsman identity and the current four real attack views. None of the inspected code solves master-art anatomy drift.
2. Require a fixed character scale/actor anchor and carry extraction/packing offsets unchanged. Compare corresponding anatomical landmarks; do not normalize each frame by its bounding box or use a sampled mesh vertex as a certified sole.
3. Validate loop and one-shot transitions separately, including ready → attack → ready. A GIF loop and final-frame hold are review modes, not full gameplay-transition evidence.
4. Keep weapon/trail separate and require actual blade/grip trajectories plus depth review. This study did not establish a universally correct RO trail shape, length or emission frame.
5. Keep cosmetic compatibility tied to pose, camera, body fit and timing. Existing factory slot options should remain restricted to real compatible datasets.

These are research findings and implementation guidance. No new character, motion or cutout has passed as a result. Coverage remains **2/96 technical imports; 0/6 complete characters**.

## Reproduce

Use the earlier pinned Craft Anything installer, then run from repository root:

```sh
python tools/character_factory_v3/research_sprite_references.py \
  --output /tmp/astra-sprite-reference-study \
  --craft-cli /tmp/astra-craft-audit/craft-anything-0.3.0-linux-x86_64/bin/craft-anything-cli
```

The output must be fresh and outside the game repository. Sources/licenses remain there; manifests and Craft Anything inventories are retained here. To repeat a browser observation, pass its saved `*-params.json` to `web-walkthrough-record` with `--deep --allow-run --project <fresh temporary .cany path>`. Websites and public renderer responses may change. Browser JSON here keeps step/network/environment/error evidence and screenshot metadata; base64 images and full third-party page DOM are omitted. Semantic conclusions were reviewed manually, not generated by Craft Anything's inventory tool.
