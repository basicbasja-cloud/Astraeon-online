# Production recipes

These are documented workflow proposals. No authoring command, model inference, or engine integration was executed during the research pass. Verify installed tool versions before adopting commands.

## Aligned pixel-art layers in Aseprite

Create one editable master pose sequence per compatible rig/action family. Use layers or groups for production pieces and separate reference layers for the approved body, sockets, and root markers. Name tags with action and facing, such as `walk_S`, `walk_SE`, and `attack_onehand_NE`. Give every production piece the exact same pose timeline even when some cels are invisible.

Author equipment while the base is visible, but export equipment without flattening the base into it. Export from a production copy that excludes guide layers. Aseprite's documented CLI can split visible layers or select a named layer. Example invocation patterns:

```bash
aseprite -b --split-layers source/character.aseprite \
  --save-as 'export/{layer}-{frame}.png'

aseprite -b --layer 'torso/linen' source/character.aseprite \
  --sheet export/torso-linen.png \
  --format json-array --data export/torso-linen.json
```

Create output directories as needed. The layer and file names are examples. Inspect whether group paths, hidden layers, frame tags, and export ordering match the installed Aseprite version. `--split-layers` must precede the input document. `--all-layers` can include hidden layers when deliberately exporting them. Do not enable `--ignore-empty` and then assume an image count still describes the full timeline. Avoid trim/packing initially; a shipping exporter must retain coordinate metadata and explicit blank bindings.

Slices can hold named regions and pivots; convert those to the chosen manifest coordinate convention. Tags and exporter JSON are useful authoring metadata, but the runtime still needs an unambiguous action/direction/pose mapping. [CLI](https://www.aseprite.org/docs/cli/), [slices](https://www.aseprite.org/docs/slices/).

For recoloring, preserve semantic material ramps rather than applying one RGB multiplier across skin, metal, leather, and cloth. Where possible, keep palette changes independent of shape variants. Inspect alpha and outline behavior after recoloring.

## Painted or cutout characters with Spine / Unity

For each required view, establish appropriate bones and attachment artwork. Reuse motion where the projection allows it; supply directional art and drawing order changes where it does not. A flat arm deformation cannot automatically expose its opposite side.

In Spine, use slots for replacement categories, attachments for artwork, and skins to group item components. A combined runtime skin can assemble several item skins. Key attachment visibility and draw order where the action requires it. Keep source/editor/runtime versions compatible. [Skins](https://esotericsoftware.com/spine-skins), [slots](https://esotericsoftware.com/spine-slots), [mix-and-match example](https://esotericsoftware.com/spine-examples-mix-and-match).

In Unity, inspect the installed 2D Animation package's Sprite Swap samples. Use Sprite Library categories/labels and Sprite Resolvers for selection, while ensuring replacement images have suitable rigging, pivots, and mesh/bone associations. For a frame-based paper doll, a central frame resolver with several SpriteRenderers may be simpler than deforming a skeleton. Use an explicit character/world sorting strategy and frame overrides. [Sprite Swap samples, package 10.2](https://docs.unity3d.com/Packages/com.unity.2d.animation@10.2/manual/ex-sprite-swap.html).

## Modular 3D to eight-direction 2D

1. Build a shared rig and attach interchangeable meshes using actual anatomical sockets.
2. Lock projection, camera elevation, orthographic scale, frame bounds, lighting policy, color management, and transparent output.
3. Choose whether the character rotates under world-fixed lighting or a camera/light platform rotates around it. These produce different shading conventions.
4. Sample clips at declared times. For a loop with n samples, use phase `f/n` for `f=0..n-1`; normally exclude a duplicate endpoint. Nonlooping actions can include their final hold explicitly.
5. Capture the base and each item/piece at the same sample times and eight view azimuths.
6. Export full geometry, visibility masks, and/or depth according to a documented strategy. Split pieces for necessary crossings.
7. Compare reconstruction with selected complete-character reference renders and inspect game-size output.

Cryptomatte is useful for object/material selection in a rendered image. It is not a way to recover every pixel of a fully hidden object. Isolated renders supply hidden geometry, but then composition must restore occlusion. Holdouts can remove occluded regions from a pass, but a mask captured for one outfit can become invalid for another. [Blender 4.2 Cryptomatte](https://docs.blender.org/manual/en/4.2/compositing/types/mask/cryptomatte.html), [holdout](https://docs.blender.org/manual/en/4.2/render/shader_nodes/shader/holdout.html).

For strict pixel art, a low-resolution render is a starting point. Inspect edge flicker, changing thin features, silhouette clusters, and material noise. Use a locked raster grid and deterministic capture; perform artistic cleanup as required. For painted output, supersampling and filtered alpha can fit the style, but use one common scale for the entire rig.

Flare's eight-view script and Bellanger's article are legacy Blender references, useful for the rotation concept rather than current API syntax. Broxxar's Unity capture script demonstrates clip sampling and color/normal atlases; it needs additional work for eight views and equipment exports. [Flare script](https://github.com/flareteam/flare-game/blob/af6eee6d339ac98011864bfe89da837fe7769c28/art_src/characters/render8dirs.py), [Bellanger tutorial](https://clintbellanger.net/articles/isometric_tiles/), [Broxxar capture](https://github.com/Broxxar/PixelArtPipeline/blob/5969589448e87cc12cd7fb0d81926c9f218a089c/Assets/Scripts/AnimationCaptureHelper.cs).

## AI-assisted production

Establish a reference bundle: identity sheet, eight approved neutral views, palette/style guide, source dimensions, root marker, and pose reference timeline. Select a coherent clip or strip as a generation unit. A full strip still requires checking frame count, phase order, limb ownership, canvas alignment, and transparency.

Prompt ingredients for a part-generation edit are: the approved reference pose, the intended item/piece, exact facing, anatomy/handedness, unchanged registration, full supported pose sequence, visibility convention, and production style. If the tool cannot enforce a constraint, inspect and repair it downstream rather than reporting it as guaranteed.

```text
Use the supplied approved rig and pose sequence. Fit [item] to the same
anatomical body, camera, palette, source canvas, root, and frame phases.
Output only [render piece], with the declared transparency and hidden-region
policy. Preserve the supplied action, facing, pose count, and slot layout.
```

This is a prompting scaffold, not proof that one request can produce a correct wardrobe. Prefer producing and testing one difficult item before scaling the catalog. When starting from a flattened reference, distinguish visible segmentation from reconstructing hidden parts. Check reconstructed anatomy and seams, and test replacement items against that recovered base.

The reviewed generation/decomposition papers offer relevant components, but none of the inspected evidence validates this entire modular-eight-direction contract. Vendor guides can establish available workflows; only actual exported samples and integration checks establish fitness for a particular project. [Research comparison](research.md).

## Godot runtime

Use a root Node2D and Sprite2D/AnimatedSprite2D pieces. Keep the authoritative animation state in one controller. With AnimatedSprite2D followers, change the selected animation/resource as needed, then restore the sampled frame and progress; changing animation resets those properties. `set_frame_and_progress` exists for retaining progress. Alternatively use Sprite2D pieces and directly resolve atlas regions from a shared clock.

Set character-internal ordering explicitly. `z_index`, relative z, and y sorting interact, so keep all equipment on the same intended actor sort basis. Preserve anchors through texture swaps. Pixel art needs the chosen point sampling and coordinate snapping policy. [AnimatedSprite2D](https://docs.godotengine.org/en/stable/classes/class_animatedsprite2d.html), [CanvasItem](https://docs.godotengine.org/en/stable/classes/class_canvasitem.html).

## Phaser / Canvas runtime

For Phaser, a Container can group an appearance at one root. Within a Container, child display-list order controls layering; child depth settings do not independently change that order. Reorder pieces using the supported Container list methods when facing or action overrides change. Set the Container's world depth from the actor's world-sort key. A central controller should set all piece frames from one sampled pose. [Container](https://docs.phaser.io/phaser/concepts/gameobjects/container), [components](https://docs.phaser.io/phaser/concepts/gameobjects/components).

For a custom Canvas renderer, compute the root once, resolve pieces and trim placement, then issue draw operations in the resolved order. Set `imageSmoothingEnabled` according to style. Keep asynchronous image-loading work outside the visible commit and avoid resizing every part independently.

## Shipping atlases

For higher-FPS production, sample from the continuous/authoritative pose timeline and retain exact contact landmarks before packing. Use native-scale review to choose pose density. At 60 FPS, multiplying eight views by many separate pieces can dominate decoded memory even when PNG downloads are small. Alias unchanged source images while retaining their timing and socket entries. Benchmark compression/streaming and cache policy in the actual renderer rather than reducing motion quality without review.

The [original export study](../studies/motion-lab/README.md) demonstrates untrimmed independent PNG/depth passes and encoded/decoded reconstruction for opaque geometry. It is a diagnostic recipe, not an Aseprite/Blender production exporter or GPU implementation.

Choose atlas pages from measured texture/memory budgets. Preserve original logical canvas, trim placement, and pivots. Use padding/extrusion appropriate to sampling and mipmaps; nearest-neighbor assets can still be affected by renderer coordinate mistakes. Keep packing rotation off until supported, and preserve invisible/duplicate pose mappings.

TexturePacker documents trim, pivots, extrusion, and texture settings. Some export formats do not support importing pivots, so verify the loader rather than trusting the preview. After packing, reconstruct selected appearances and compare with untrimmed references. [Texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings), [command-line parameters](https://www.codeandweb.com/texturepacker/documentation/commandline/parameters).
