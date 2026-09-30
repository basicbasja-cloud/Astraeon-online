# ASTRAEON visual standard

## Scope
The first benchmark is Wayfarer Market in Shenzhou. This establishes the visual standard for one region before other civilizations expand.

## Camera and scale
Normal Cartesian ground coordinates; elevation is separate. Raised orthographic-like three-quarter view. Terrain extends beyond the viewport. Forward/inverse projection and input share `world-view.js`; feet are the sprite anchor.

The earlier 90–105 pixel player / 180–280 pixel building guideline produced miniature architecture. Replace it with the following provisional human-relative system, inspected in local gameplay at desktop, tablet, phone portrait and landscape. **Public Pages visual acceptance remains pending: the environment proxy currently blocks the public host.** Revisit these relationships after public inspection rather than treating the numbers as permanent.

| Relationship | Benchmark convention |
|---|---|
| Humanoid baseline H | 76 presentation units before camera zoom; NPCs 0.94 H |
| Ordinary creature | 0.68–1.25 H; species silhouette determines the value |
| Guardian | 2.32 H |
| House | Approximately 3.55–3.9 H wide, 5.3–5.8 H tall |
| Service hall | Approximately 5.5 H wide, 6.3 H tall |
| Primary civic landmark | Approximately 6.6 H wide, 7.5 H tall; larger than service buildings |
| Gate | Approximately 4.8 H wide, 6 H tall |
| Tree | Mature border trees approximately 2.7 H tall; saplings may be smaller |
| Market stall / cart | Approximately 2–2.3 H wide; leave approach space on road side |
| Door / counter | Judge visible human clearance around 1.1–1.4 H / waist height; source artwork remains the constraint |
| Main avenue / branch | 3.1–3.6 / 1.5–1.6 world units across, versus humanoid body width approximately 0.5 world unit |

Town bounds are 44 × 40 world units, versus the former 30 × 27. The central square, north civic terrace, market, east gate, west residential and southeast crafting neighborhoods form distinct anchors. Collision footprints expand with the architecture; paths and NPC approaches remain open. Do not assume sprite width equals traversable footprint.

Camera zoom is 0.92 on wide desktop, 0.96 on tablet/landscape, and 1.0 in tall portrait. The player ground anchor sits at 55% of viewport height (56% in portrait), exposing more forward space. UI controls scale independently. Benchmark screenshots show architecture extending outside the viewport and the player remaining identifiable beside doors and stalls. Door/window/stair details are still painted into source assets, so architectural acceptance requires visual review rather than a pixel formula alone.

## Characters
Anime/storybook proportions, readable head and weapon silhouette, navy/cream traveler outfit with restrained gold trim. Warrior, Mage and Ranger use distinct kits. No universal color-swapped character as a final class treatment. Movement uses distance-driven animation; attacks use anticipation, impact and recovery.

## Architecture
Shenzhou combines warm plaster, dark timber, jade ceramic roofs and small spiritual devices. Shop fronts face shared streets. Tiled roof ridges, carved wood brackets, cloth awnings and hanging signs. Architecture follows a district plan; it is not random scatter.

## Palette and materials
Sage/jade foliage; warm ochre roads; limestone plaza; terracotta and teal cloth; navy shadows; warm gold lamps. Clean illustrated material edges and low-frequency painted detail. Match sun from upper left and soft grounded shadows. Avoid a photorealistic ground with flat primitive props.

## Power systems
Magic, Qi, Spirit, gunpowder, advanced engineering and psionics coexist as parallel paradigms. Technology does not establish superior power. Visual motifs distinguish each system rather than relying on higher brightness.

## Vegetation and props
Rounded layered tree canopies with visible trunk/roots, flower beds, grass clumps, worn paving, barrels, carts, crates and market goods. Assets share camera, light and scale. Variation must change arrangement and silhouette, not only tint.

## UI
Translucent navy frames, cream text, gold emphasis and jade feedback. Minimize permanent controls. Portrait and landscape are separate layouts with reachable action clusters and a collapsible quest strip. No resize-by-scale-only layout.

## VFX and lighting
Short directional weapon trails, clear telegraphs conforming to ground projection, restrained contact sparks. Damage effects must not obscure hostile attacks. Day/night changes lamps and ambience as well as scene lighting. Weather changes fog, wind, wetness and audio.

## Asset acceptance
Original/legally usable art only. Transparent atlas sprites use declared cells and feet/base anchors. Check alpha, cell clipping, silhouettes, gameplay-distance readability and alignment in runtime. Never approve the final look solely from a generated image.

## Directional character style

Preserve the original richly painted, rounded character volumes, detailed armor, hair, robes and cloth. Front, back, left, right and diagonal views must depict the same identity. Avoid blocky low-poly substitutes. Runtime actors use eight authored views around the circle, without image mirroring. Review each archetype at gameplay scale as well as in the directional gallery.

## Shenzhou outdoor / ruin benchmark

Goldenfield: warm ochre paths, sage meadow flowers, willow silhouettes, jade/timber farm buildings and caravan services. Moonbamboo: cooler dense foliage, bamboo groves, old stone and a lantern-lit shrine. Moonveil: quieter stone ground, visible room thresholds, layered wall segments, braziers and a contrasting moonseal. Roads must connect landmarks and exits; decorations must respect collision footprints. Main action/navigation icons are original SVG outlines rather than platform emoji.

Reject new animation frames that point in the wrong direction even when their detail looks attractive. Retain accepted rear views until consistent replacements are available. Grounded frame crops and distance-based gait do not substitute for skeletal foot placement.
