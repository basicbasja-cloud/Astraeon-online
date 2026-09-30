# Asset provenance

No Ragnarok intellectual property is included. All assets below are original generated art for ASTRAEON. No third-party texture/model/audio pack is presently used. Generated-art provenance is tracked here; this is not a claim that third-party game art is licensed.

| Asset | Origin | Use / status |
|---|---|---|
| astral-outpost.webp | Original project image generation, pre-audit repository asset | Character creation key art |
| hero-atlas.webp | Original project image generation, pre-audit repository asset | Legacy hero/NPC atlas; replacement in progress |
| astral-wolf.webp | Original project image generation, pre-audit repository asset | Legacy wolf atlas |
| grassland-ground.webp | Original project image generation, pre-audit repository asset | Ground base; authored roads and decals layer over it |
| town-atlas-v1.webp | Built-in ImageGen, 2026-09-30, original Shenzhou 8-object atlas | City benchmark; alpha preserved; cell crops rendered in scene.js |
| icon.svg | Original project vector asset | App icon |

Town prompt: transparent eight-object atlas, jade-roof timber/plaster guildhall, merchant shop, shrine, city gate, broadleaf tree, striped market stall, astral fountain and merchant cart; raised restrained-yaw three-quarter camera, storybook fantasy, warm upper-left light, no game IP or text. Final prompts for subsequent animation atlases will be recorded with their integration.

## Original production-pass atlases — 2026-09-30
Generated with the built-in ImageGen for this project from original textual briefs (and edits of those same original generated images). No external character/map/art reference was provided to the generator.

| Files | Content / provenance |
|---|---|
| warrior-atlas-v1.webp | Original silver-haired navy/cream warrior; final source exec-4b0c9504-8f9d-4bf2-b5b9-481456d14805.png |
| mage-atlas-v1.webp | Original teal/cream staff mage; final source exec-543439ea-f7bb-4e46-919e-8f465765c101.png |
| ranger-atlas-v1.webp | Original sage-cloaked archer; final source exec-eb893943-c508-4db1-9bfa-8317171fa1a0.png |
| meadow-monsters-atlas-v1.webp | Leafmane fox, mossback boar, amber beetle, caravan outlaw; exec-a9705229-0c54-4cd5-973a-82466dde02b5.png |
| forest-monsters-atlas-v1.webp | Sporeling, lanternwood spirit, moonstone sentinel, veil serpent; exec-598028fc-68db-4693-8511-f6e06eb90d54.png |
| moonveil-boss-atlas-v1.webp | Original armored stag guardian and glaive poses; exec-97a0dd6c-4dc8-4ec2-9774-73bf0a7dc8e4.png |
| secondary-atlas-v1.webp | Planter, bench, crates, notice board, bamboo, ruin arch, terrace, pillar; exec-949dfe95-0c9d-4ad1-8de3-19fe4c75610e.png |

PNG→WebP preserves alpha; source extraction/ground anchors are in atlas-metadata.js/world-content.js. Audio in world-systems.js is original synthesized oscillator/noise material and an original pentatonic sequence, with no samples from another game.

## Directional artwork — 2026-09-30

Built-in ImageGen edits of the project’s original atlases, preserving the previous painted character design. Lossless WebP copies retain transparency; `directional-metadata.js` declares source rectangles. No external model or third-party character artwork is used.

| Asset | Generated source |
|---|---|
| warrior-directional-v1.webp | exec-b6c73faa-7798-4fbc-b959-7a3d2ecf0fc5.png |
| mage-directional-v1.webp | exec-764d1e2c-6de8-42a5-a3cf-27362b252108.png |
| ranger-directional-v1.webp | exec-466bf877-e6a7-4134-a358-b55e5144aa24.png |
| boss-directional-v1.webp | exec-62e132f9-111d-4182-b99a-a114962a96e4.png |
| meadow-directional-v1.webp | exec-a84bd012-eebf-4869-9961-de856e2f5321.png |
| forest-directional-v1.webp | exec-2ab2efd2-9183-44dc-8e5b-6fab6fa03fa4.png |

## Shenzhou environment and walking sheets — 2026-09-30

Original built-in ImageGen art and edits of this project's own sheets. Format conversion preserves transparency; environment and directional metadata record source rectangles. Runtime source-silhouette clipping separates neighboring sprites; original image files are preserved. Walk copies use quality-90 alpha WebP; terrain uses quality-88 WebP. Original PNGs remain in the task's generated_images directory. No third-party art/audio references were used.

| Runtime asset | Generated source |
|---|---|
| outdoor-atlas-v1.webp | exec-d3c03079-501e-4a1d-b457-764955845578.png |
| ruin-atlas-v1.webp | exec-2449ee31-8a48-4902-a010-1b4879a006c1.png |
| meadow-ground-v1.webp | exec-11740bcd-3357-42e5-b02b-938f9b2c05c6.png |
| forest-ground-v1.webp | exec-527ba276-6264-4f7f-8f3c-3e4cd7e2ad66.png |
| ruin-ground-v1.webp | exec-c4e70d3b-6b68-4eb7-95b4-0314316c2d6f.png |
| path-ground-v1.webp | exec-e5c318c5-cf5f-4049-9bdc-345c082e99bf.png |
| warrior-walk-v1.webp | exec-9c15937d-6c73-437a-92da-9b22601c9388.png |
| mage-walk-v1.webp | exec-b5d936ee-91fa-41b6-8408-8a200783daf4.png |
| ranger-walk-v1.webp | exec-158f16d9-e3e5-4d4a-9733-2a84de6c28f1.png |

Environment brief: original Shenzhou mill, farmhouse, caravan camp, willow/bamboo, broken stone and lantern shrine; quiet hand-painted meadow, woodland, dirt path and stone materials; camera and light matched to the existing game. Ruin props include two wall orientations, rubble, braziers, moonseal, altar, pillar and chest. Walking briefs preserve the existing detailed warrior/mage/ranger identity with eight stride phases in eight authored directions. Runtime deliberately uses the accepted base atlas for two rear directions where the extended sheets did not retain the required facing. UI vectors in icons.js and water/noise audio are original code-created material.

## Golden Town Scene paving — 2026-09-30

`assets/town-limestone-v1.webp` replaces town paving with original built-in ImageGen art, source `exec-62028e7a-c750-49b6-b7c6-c07773324e19.png`. No third-party reference pixels were supplied. PNG-to-WebP conversion changes format/compression only. The original remains outside the checkout under `/workspace/generated_images`. This refines an existing material; it does not add a building or decorative asset family. The material must pass actual runtime style, lighting, projection and scale review.
