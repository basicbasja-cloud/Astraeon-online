# ASTRAEON visual standard

## Scope
The first benchmark is Wayfarer Court and its guild/market approaches in Shenzhou. This establishes the visual standard for one region before other civilizations expand.

## Active architectural reference — source68

The user's instruction “Hard ref to ro3” makes `RO3 Ref/` the hard reference for
house/building exterior forms, facade construction, detail, texture readability,
lighting/shading and scale relative to the visible character. The approved
ASTRAEON concept continues to own identity and district hierarchy. House envelopes/infill and the planted fountain court may change to meet the reference while retaining useful streets and service routes.
Earlier Canvas2D/v26–v28 camera and scale prescriptions are superseded here.

Compare the same building family, character size and viewing angle. The images
are perspective views; their pixel ratios are observations, not proprietary
world dimensions. `04_08_00` controls long timber rows with two roof dormers;
`04_08_34` controls steep front gables, attic glazing and opened shutters;
`04_08_45` and `04_08_39` control stout framing, small window lights, tall wood
entrances and functional awnings. `04_08_30` supplies civic portal detail but
crops the full civic building, so it cannot establish the Hall's overall height.

## Camera and scale

The active scene is native 3D with world bounds 112 × 128. Ground and navigation
are Cartesian, terrain has authored elevations, and the camera uses ordinary
orbit/zoom controls. Gameplay pitch is 46 degrees; distance 65 is close and 325
is far. Sprite feet are the anchor. Camera controls and actor artwork must not
be resized to disguise architectural proportion errors.

| Relationship | Source68 working proportions, subject to visual approval |
| --- | --- |
| Humanoid H | Registered moving body ≈2.42 world units (70 × 92/76 ÷ 35); idle artwork bounds differ slightly; visible screenshot size depends on camera/pose |
| Ordinary building envelopes | 37 including one infill; primary lots6–7 wide, constrained traced fronts fit their actual edge |
| Ground floor top | Home 3.65, merchant 3.8, workshop 3.55 units; foundations remain at .44 |
| Door wood leaf | Home 2.8, merchant 3.0, workshop 2.75 world units; compare full entrance including frame/steps to the unchanged visible actor |
| Upper window | 1.08 × 1.52 units; three-by-three lights and three/four bays on primary frontage |
| Roof | Clay, 42° long rows with paired dormers / 48° front gables; dormer peaks below main ridge |
| Upper jetty | .42 units beyond wall, replacing .76–.89-unit projections |
| Civic Hall | Original monumental concept hierarchy retained; full silhouette cannot be measured from the cropped RO3 portal image |
| Ground trim | At most .16-unit outward projection inside existing .18-unit actor clearance |

Software rendering must remain at 1× CSS resolution; hardware follows display
density from at least 1× up to 1.5×. A higher explicit still-capture ratio is
review evidence only. Art and locomotion acceptance remain pending; technical
checks do not establish a hard-reference match.

## Characters
Anime/storybook proportions, readable head and weapon silhouette, navy/cream traveler outfit with restrained gold trim. Warrior, Mage and Ranger use distinct kits. No universal color-swapped character as a final class treatment. Movement uses distance-driven animation; attacks use anticipation, impact and recovery.

## Architecture
For the active Wayfarer RO3 pass, use warm limewash, stout dark timber and steep clay house roofs. Blue/slate roofs belong to civic and shrine landmarks. Shenzhou retains original spiritual devices and regional identity. Shop fronts face shared streets. Tiled roof ridges, carved wood brackets, cloth awnings and hanging signs. Architecture follows a district plan; it is not random scatter.

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

## Historical RO1-inspired production direction (pre-native-3D)

Use [RAGNAROK_REFERENCE.md](./RAGNAROK_REFERENCE.md) for the inspected sources and production techniques. Classic RO combines directional sprites with textured 3D terrain/models, navigation data and shared camera/lighting. ASTRAEON adapts those spatial relationships to its fixed-camera painted Canvas2D presentation. Our soft painted artwork and manual action feedback are ASTRAEON decisions; they are not claims about RO's original pixel-art workflow.

Ragnarok Online 1 is the primary presentation and town-planning reference. ASTRAEON retains original lore, parallel power paradigms and manual action combat. Use painted directional sprites as the mainline character presentation. Preserve the rich Warrior, Mage and Ranger art; keep scope to 3–4 hero sets, with no fourth set before the existing style passes review. Exclude the low-poly prototype from the live client. Continuous simulated facing projected through the camera selects eight authored views; this is not continuously articulated 3D.

Modern combat comes from directional attacks, cast/hit effects, weapon trails, telegraphs, auras and restrained contact feedback. Single-layer Nodes vary gameplay and VFX, rather than requiring character sheets per Node. Do not mass-generate new sprite sets or multiply outfits to solve a visual-cohesion problem.

## Golden Town Scene gate

Content expansion is paused until Golden Sprite Character and Golden Town Scene are both approved in the deployed game. GOLDEN_SCENE.md defines Wayfarer Court: the primary Consortium landmark, smaller fountain focal point and market cluster, the gate route, shared architectural palette, world-aligned paving and one visible humanoid baseline. Roads, buildings and planting must define connected spaces. Door clearance, source perspective and final illustrated charm remain review items. The unavailable Photo 1 attachment was not inspected; repository artwork supplies the working reference.

Golden Warrior calibration uses reviewed boot contacts and one 70-pixel visible body height across directions and locomotion sheets, preserving overhead weapon reach. Separate hit/death poses use four cardinal views; diagonal reactions select the nearest view. Do not broaden this into outfit or Node sprite permutations. Other class refinements wait for the first in-scene art review.

## Reference-derived construction rules

- Place routes, plaza boundaries, footprints and door approaches before decorative detail. Buildings shape the edges of connected public space; every service needs a clear approach and departure.
- Keep one projected ground convention for materials, collision, props, actors and effects. The current basis is `(48,14)` / `(-32,22)`. Review each building's painted base against it; screen rotation or mirroring cannot create a new facade viewpoint.
- Separate art anchors, occupied ground, entrances and roof occlusion. The top of a sprite is not its depth origin. Current whole-sprite sorting/fading is an approximation that needs review around large footprints.
- Keep stone, soil, drainage, wear and planting tied to use. Review ground detail below actor contrast. Shared colour grading cannot repair inconsistent perspective or painted light.
- Preserve canonical face/hair, costume construction, sword handedness and cape fastening across views. Approve key poses before increasing frame counts; record per-frame boot contacts and standing body scale separately from weapon reach.
- Keep attack/cast effects aligned to actual contact timing. Repair the Warrior rear gait/defective stride before adding costumes or classes. Four-cardinal reactions remain a reviewed compromise, not eight unique reaction views.

Landmark hierarchy must pass from arrival, court, hall and phone views. The existing `north-house` now uses a smaller shop facade from the existing atlas, leaving the Consortium as the only large civic hall. Review all approaches rather than accepting nominal dimensions alone.

## Applied motion and town pass — v28

Ground axes now follow the painted foundation planes. Town, outdoor paths, dungeon stone, telegraphs, depth sorting and inverse input share the same basis; the camera remains fixed. Four existing entrance forecourts use the shared limestone. The court has a quieter value grouping, projected border and restrained fountain meeting rings. Full road width plus human clearance must remain outside occupied footprints.

Actor motion pivots around registered feet: restrained speed-dependent rise/lean while walking, anticipation before contact, a short contact lunge, return to idle during recovery and small cast/dodge/hit weight changes. These are presentation adjustments, not new limb frames. Warrior uses seven accepted extended stride keys at even cadence; north/northwest retain two authored poses. Three new rear-walk candidates failed identity/alternating-foot review and are excluded. Art acceptance stays pending.

Source68 street enclosure follows the supplied RO3 street views while keeping broad civic/gate courts. The fountain uses tiered pools, a scalloped rim, four raised flowerbeds and green benches against04_08_20. Density is assessed in gameplay views; local footprint growth is13.1%, without claiming a proprietary whole-map house count.
