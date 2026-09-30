# ASTRAEON visual standard

## Scope
The first benchmark is Wayfarer Court and its guild/market approaches in Shenzhou. This establishes the visual standard for one region before other civilizations expand.

## Camera and scale
Normal Cartesian ground coordinates; elevation is separate. Raised orthographic-like three-quarter view. Terrain extends beyond the viewport. Forward/inverse projection and input share `world-view.js`; feet are the sprite anchor.

The earlier 90–105 pixel player / 180–280 pixel building guideline produced miniature architecture. Replace it with the following provisional human-relative system, inspected in local gameplay at desktop, tablet, phone portrait and landscape. **Public Pages has been inspected live at desktop, tablet and both phone orientations; art approval remains pending.** Revisit these relationships during further public comparisons rather than treating the numbers as permanent.

| Relationship | Benchmark convention |
|---|---|
| Humanoid baseline H | Visible player feet-to-head height, approximately 70 pixels before camera zoom; calibrate NPCs by visible bounds |
| Ordinary creature | Approximately 0.7–1.4 H; species silhouette determines the value |
| Guardian | Approximately 2.5 H |
| House | Approximately 3.85–4.25 H wide, 5.75–6.35 H tall |
| Service hall | Approximately 6 H wide, 6.9 H tall |
| Primary civic landmark | Approximately 7.1 H wide, 8.2 H tall; larger than service buildings |
| Gate | Approximately 5.2 H wide, 6.5 H tall |
| Tree | Mature border trees approximately 3.3 H tall; saplings may be smaller |
| Market stall / cart | Current market counter / cart approximately 2.1 / 1.6 H wide; leave approach space on road side |
| Door / counter | Judge visible human clearance around 1.1–1.4 H / waist height; source artwork remains the constraint |
| Main avenue / street / service | 3.8 / 2.6 / 1.1 world units across, versus humanoid body width approximately 0.5 world unit |

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

Reject new animation frames that point in the wrong direction even when their detail looks attractive. Retain accepted rear views until consistent replacements are available. Grounded frame crops and distance-based gait still require consistent authored foot poses.

## Current RO1-inspired production direction

Ragnarok Online 1 is the primary presentation and town-planning reference. ASTRAEON retains original lore, parallel power paradigms and manual action combat. Use painted directional sprites as the mainline character presentation. Preserve the rich Warrior, Mage and Ranger art; keep scope to 3–4 hero sets, with no fourth set before the existing style passes review. Exclude the low-poly prototype from the live client. Continuous simulated facing selects eight authored views; this is not continuously articulated 3D.

Modern combat comes from directional attacks, cast/hit effects, weapon trails, telegraphs, auras and restrained contact feedback. Single-layer Nodes vary gameplay and VFX, rather than requiring character sheets per Node. Do not mass-generate new sprite sets or multiply outfits to solve a visual-cohesion problem.

## Golden Town Scene gate

Content expansion is paused until Golden Sprite Character and Golden Town Scene are both approved in the deployed game. GOLDEN_SCENE.md defines Wayfarer Court: the fountain focal point, Consortium and market clusters, the gate route, shared architectural palette, world-aligned paving and one visible humanoid baseline. Roads, buildings and planting must define connected spaces. Door clearance, source perspective and final illustrated charm remain review items. The unavailable Photo 1 attachment was not inspected; repository artwork supplies the working reference.
