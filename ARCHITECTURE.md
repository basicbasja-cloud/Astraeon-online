# Runtime architecture

The default Wayfarer runtime renders the Blender-authored spatial environment
with vendored Three.js and painterly directional 2D actors in the same WebGL depth
buffer. DOM/CSS owns menus and responsive controls. Canvas assembles actor textures,
renders UI/effects and retains legacy zones. This is a local action RPG slice.

The [master plan](MASTER_PLAN.md) incorporates the user's spatial architecture
amendment. `authoring/wayfarer-spatial.blend` exports meshes, UVs, materials,
walkable surfaces, solids, parented services, patrols, lights and portals through
`tools/export-world-v3.py`. Default boot imports `world/v3/wayfarer-spatial.json`
before gameplay modules capture content; `world/v3/town-import.js` adapts the
same records to existing simulation consumers. `world/v3/spatial.js` compiles
lightweight navigation and elevation. Runtime rendering does not draw building
cards in the native town or maintain a separate collision coordinate list.

`world/v3/renderer.js` batches static meshes by material, uses authored UVs and
original material atlases, and draws alpha-tested upright illustrated actor quads with
depth tests and depth writes. The default classic Ragnarok camera uses a 15-degree
perspective lens, 50-degree downward pitch, yaw zero, zoom 125 and centered smooth
follow. Mouse orbit/tilt/zoom controls update the basis shared with gameplay.
Ground clicks raycast authored navigation surfaces; actor/service
picks use the visible depth solution and actor alpha. The quad's vertical axis
is world Z, so a character standing before a doorway does not lean into its wall.
Hidden contact rectangles follow the actual civic and shrine tread tops; the
earlier continuous ramps remain inactive source references. This avoids expensive
mesh physics while keeping feet above the visible steps. Baked cast shadows and
world-space contact shadows replace real-time shadow maps.

The Golden Warrior uses `world/v3/locomotion.js` for simulation and the new
`warrior-painted-locomotion.json` for eight-direction/eight-frame full-body
walk/run/sprint playback. Artwork uses shared scale and foot baselines; no
procedural limbs are overlaid on the new locomotion frames. Older contact/rig
paths remain for comparison and other states. Combat, skills, inventory, quests and saves
retain their existing responsibilities. Golden animation and art approval remain
open; implementation and test passes are not visual acceptance.

The [production scalability phase](MASTER_PLAN.md#production-scalability-requirement--mandatory-golden-foundation-deliverable)
is a required Golden Foundation deliverable after Wayfarer acceptance and before
full production of City 2. Extract proven engine/world systems and component-level
environment kits while keeping layout, unique landmarks, palette, NPCs, lore and
quests in city content. Keep solutions local during the current visual iteration;
this requirement does not authorize premature framework abstraction. New cities
must use the same exporter, renderer, shared-depth 2D actors, navigation,
collision, NPC/portal framework and material loader through a city template.

`?renderer=canvas` and `?world=court-legacy` retain migration/comparison paths.
`proof.html` and the older review reports remain historical structural evidence.
The following baseline notes describe earlier versions where explicitly dated;
they do not supersede the current spatial architecture.

| Module | Actual responsibility |
|---|---|
| world-view.js | Shared projection/inverse, responsive zoom/framing, human-relative actor dimensions and zone bounds |
| skill-nodes.js | Authored compatibility, single-node application/normalization and pure contact status model |
| world-content.js | Authored Shenzhou props, identified collision footprints, entrance forecourts, roads, atlas regions and walker routes |
| input.js | Keyboard device bindings → action names and movement axes |
| combat.js | Pure ability definitions/compiler, cast/active/recovery timeline, cooldowns, world-space hit shapes, swept projectile collisions |
| character-motion.js | Continuous position, yaw, facing modes, analog velocity, bounded turning, gait and stance contacts |
| animation.js + directional-art.js + directional-metadata.js | Eight authored views, pose selection, explicit source bounds and ground anchoring |
| sprite-motion.js | Pure foot-pivot presentation offsets and anticipation/contact/recovery pose timing |
| hero-registration.js | Golden Warrior boot contacts, per-direction body calibration and reaction source rectangles |
| combat-vfx.js | Reusable world-space slash ribbons and dodge dust; shares Node colors |
| character-renderer.js | Painted actor adapters and grounded shadows |
| dungeon.js | Four authored rooms, connecting passages, wall collision and gated progression |
| environment.js + environment-metadata.js | Authored field/forest paths, painted props, ground patterns and segmented ruin walls |
| navigation.js | Bounded half-unit A* grid, wall-safe path simplification; never rendered as terrain |
| enemy-combat.js | Pure species/boss attack plans, telegraph geometry and swept charge contact |
| exploration.js + save-state.js | Persistent supply/herb claims and backwards-compatible save normalization |
| icons.js | Original SVG control/navigation symbols |
| scene.js | Cached authored paving, original environment sprites, depth fade and animated fountain/lamps |
| world-systems.js | Ambient walkers, gradual atmosphere parameters, quality presets and original WebAudio synthesis |
| game.js | Existing local state/progression/menu integration, movement, enemy AI, reactions, save, camera and presentation orchestration |
| qa.html | Same live iframe in four actual CSS viewport sizes; frame timing and state samples through validated postMessage |

## Coordinate contract
Ground uses ordinary Cartesian x/y with separate z elevation. The authored town includes stairs and terraces. Its shared camera profile governs perspective projection, floor rays, actor directions and camera-relative input; world-space scenery and upright actors share one depth buffer. Other zones retain the paired affine projection and projected-depth sorting. The camera starts at the player and follows with exponential time-based smoothing.

## Simulation boundary
`combat.js` has no renderer, DOM, audio, storage or clock dependency. Caller supplies simulation time, action origin, aim and entities, then consumes contact/release events. Paused menus and hidden tabs freeze simulation time. Dodge can cancel an action; cooldowns remain spent. Impact presentation does not determine damage timing. Enemy attack geometry, navigation, save defaults and world claims now have independent pure modules. Movement/AI/progression orchestration still lives inside `game.js`; moving them into an `IGameSimulation` adapter is outstanding. No server-authority or prediction claim.

## Historical archetype animation contract (current Warrior below)
Three original archetypes each have eight authored directions and six poses: idle, two locomotion strides, anticipation, contact and crouched reaction. The guardian has eight poses per direction; regular enemies have idle and attack views. Runtime yaw is continuous and smoothly follows movement, target or aim; presentation projects facing through the ground camera and chooses the closest screen-space 45° view without horizontal mirroring. Gait phase follows traveled distance. Three additional walk sheets provide eight stride phases for six directions; north and northwest keep the accepted two-pose rear cycle because the extended sheets drifted toward side/front views. Warrior omits the corrupted stride and distributes seven accepted keys evenly across a cycle, avoiding a repeated hold. Cached source-silhouette paths clip neighboring cell pieces without repainting the original artwork. Source bounds exclude neighboring atlas fragments and align visible feet. Golden Warrior registration now uses source-space boot contacts and stable 70-pixel visible body scale. Sixteen original hit/death frames cover all eight directions without cardinal fallback. The manifest drives a per-direction 2D fall transform on the hit pose, crossfades to the original collapsed artwork, then holds it before its final fade.

These are painted 2.5D assets, not skinned 3D characters. The movement layer tracks stance contacts, but sprites do not articulate limbs to those contacts. Hand/back/hip coordinates are approximate world-space attachment positions, not imported rig sockets. Attack impacts wait for actual aim convergence; projectiles and slash effects use the same continuous world direction. Directional pose consistency, limited enemy locomotion and richer transitions remain art polish work.

## Loading and persistence
Current zone spawns active enemies; old enemies are discarded on transition. Boot waits for town and character art. Zone transitions pause behind a loading overlay and await that zone’s ground/enemy atlases; failed loads preserve zone and travel gold and can be retried. Shared image atlases load once. This is zone activation, not chunk streaming. LocalStorage retains the existing save key and progression, normalized to saveVersion 3; failed writes notify the player. Active dungeon runs reset on reload. SW serves navigations network-first and versioned static assets cache-first (v68, aligned with boot/page). Core town/hero art is precached; field/forest/guardian art is cached when visited. Unvisited zones require a connection. Real multiplayer, account persistence and a shared economy are future work.

## Base Skills and single-layer Nodes

Twelve starting-class skills are deliberately authored in `combat.js`; six attack skills accept explicit compatible nodes from `skill-nodes.js`. A save stores one string per Base Skill ID in `skillNodes`. The compiler retains base targeting, cost, cooldown, shape and class identity. Invalid, nested or incompatible choices are discarded during normalization. Old `techniques`, `active`, `path` and unknown progress fields survive save migration, but the old free-form compiler and Advanced Path controls are inactive. Existing bonuses are not stripped from returning saves.

Tempest and Arrow Rain each lock an authored area and pulse three times. Published fields survive ordinary cast recovery/cancel and clear on zone/class changes. Fire burns and ignites; Ice builds frost and freezes ordinary foes; Lightning chains through clear sight lines and briefly shocks; Gravity pulls with collision checks; Qi restores Resolve on contact; Spirit heals inside the area; Void delays ordinary enemy attacks; Wind backsteps after projectile release; Plasma follows a marked foe before its delayed burst. Bosses resist freeze/shock/disruption and have reduced pull.

Warrior combos earn Resolve on contact; Mage Mana recovers faster between casts; Ranger Focus recovers faster while stationary. Selected targets preserve facing while moving, including reverse gait when backing away. This does not add dedicated strafe animation art. Tuning is available in town or at an actual nearby camp after clearing nearby foes. Menus pause simulation. No skill trees, advanced evolutions or online authority are implemented.

## Historical Canvas sprite presentation (other zones)

The client loads the existing painted Warrior, Mage and Ranger atlases through the Canvas renderer. There is no opt-in WebGL character renderer or model download. Movement and aim remain separate, with continuous world-space direction selecting eight authored views. Distance-based gait and normalized action impact timing keep presentation coupled to actual movement and combat; damage remains controlled by the simulation. Existing skills and Nodes express their variations through behavior and VFX.

## Historical Canvas Golden court presentation

`AstraeonContent.goldenScene` records the town concept, selected Warrior, Consortium landmark, court polygon, controlled palette, eastbound axis, focal order and pending art status. Roads have avenue/street/service/field roles: paved main routes frame the court, narrow dirt routes serve shops/courtyards, and the eastern stone approach gives way to dirt beyond the existing Caravan Gate. `scene.js` maps shared limestone through the affine ground projection and caches material/edge/wear composition. The fountain footprint is in `townBlocks`, so movement, pathfinding and projectiles agree with its occupancy. Existing NPC approaches and the connected region loop remain functional. This is one candidate block under a visual approval gate.

The v27 hall image replaces only `guild-hall`; the original town atlas remains in use for all other assets. Its front steps define the anchor. Town verge material is downsampled, toned and mapped through the shared world projection once. Paving/soil/edge/drainage composition retains a single terrain cache and visible-region blits. The Registrar/Quest Board, Artisan, Housing Keeper and Gatekeeper keep their original interactions at revised facility approaches.

## Shared projection and registration — v28

The affine ground basis is world X `(48,14)`, world Y `(-32,22)`. `world-view.js` owns projection, inverse and material matrices. Town and outdoor caches, terrain patterns, depth sorting, sprite facing, pointer targets and VFX consume that contract. Painted facades retain their authored view and dimensions; camera zoom and 44 × 40 town bounds are unchanged.

Town cache is 4000 × 2100, offset (1450,100); outdoor road cache is 3000 × 1800, offset (1150,160). Visible-region blits avoid scaling the whole cache per frame. Temporary construction masks can increase boot memory. Forecourts are shared source data rather than renderer literals. Building shadows use matching identified occupied footprints; NPC labels are drawn after actors with nearby-service filtering and collision separation. NPCs turn toward nearby players.

`sprite-motion.js` adds bounded foot-pivot rise/lean and action offsets. It does not move collision, extend weapon range or set damage timing. Combat remains world-space; visual direction selection accounts for the camera.

## Expanded town and movement correction — cache v47

Wayfarer land and district spacing expand by two on each ground axis, giving four times the land area (112 x 128 world bounds). Building proportions remain local to their district placement. Old overlapping road patches are replaced by an authored civic spine and connected district loops. Exact collision/elevation queries use 8-unit spatial buckets. Large town navigation uses 1-unit A* search spacing and a bounds-derived unique-node budget; smaller zones retain half-unit searches. Physical polygon clearance still decides traversability.

Normal complete-body frames sample shared GPU atlases directly; action transforms/fall blends still compose into actor Canvas textures. Shared sprite alpha masks preserve visible picking. Painted stride travel and duty override the old procedural clips. Measured brown boot soles, explicit contact/flight phases and a latched world contact translate the whole illustrated body. Contact shadows follow its rendered ground position. Teleports and idle/action transitions clear stale contacts. Movement views use actual travel direction immediately while simulation aiming retains smoothed rotation.

AudioContext preparation occurs during setup and resumes on the creation gesture, avoiding device initialization on the first footstep. QA exposes compact whole-frame costs for performance measurements without cloning the entire world. Source/export parity, live routes and actual captures remain necessary; model-foot tests alone do not validate painted contact or art quality.

## Painterly town finish — v47

The default Three town uses a 15-degree lens, 46-degree downward pitch and centered follow. Camera rays, input, actor directions and visible sole registration share the current camera orientation. Full-frame sprite textures retain linear filtering without mipmaps; shared preuploaded atlases avoid frame-by-frame texture creation. Canvas remains in use for reactions/actions and other zones.

Twelve separately owned frontage lots have projecting upper storeys, window bays, balconies, dormers, arched entrances and varied shallow curved roof profiles. The Hall has a broad faceted dome, asymmetric towers and a deeper civic entrance; arched loggias frame its public approach. Gentle street bends and an irregular court replace the strongest geometric outlines. The saved Blender source contains the geometry, ownership, contacts, services and patrol paths. Scripts numbered v44–v47 are a chronological edit record, mostly one-time migrations, not a rebuild recipe.

Material batches include the material name as well as its texture specification, preserving distinct architectural colors that share a tile. Source67 exterior textures store meanLinearRGB and paletteDetail in their native material metadata. The shader normalizes texture variation against that linear mean and applies it to the authored palette, retaining seams and grain without recoloring whole buildings. Older atlases keep their existing mix. Roof UVs follow the ridge and slope distance rather than placing tile rows along the slope. Clockwise walkable faces shade upward. Native lighting optionally exports ambientColor and sun.color; worlds without these fields retain their prior tones. Source67 uses warm sun (.68) and cool ambient (.40), 16-ray corner contact AO (.42 strength / 1.6-unit radius), and an alpha-aware 1536-pixel native floor cast/contact bake. The runtime uses the bake’s actual resolution and projects it onto the highest authored floor in each half-unit cell; the 2048-pixel geometric atlas remains the fallback. These are static bakes, without per-frame shadow rays or physically based GI.

Paving feathers derive only from exposed low-floor union boundaries; internal segment/junction seams remain opaque. The shallow shoreline ribbon and calmer water palette soften the rock/water contact. These visual meshes do not affect navigation or interaction picking. Buildings intersecting the actual player sightline fade to smooth 16% transparency, while collision and cast shadows stay intact; up to four owners can fade simultaneously. Vegetation alpha cutouts retain their existing depth/picking policy.

Contact registration uses the lowest substantial brown-boot band and reviewed directional support/flight exceptions, excluding sword/cape tips. A landing after flight starts a new contact generation; the old point is never resumed across an airborne interval. Flight offsets decay once over the first airborne frame interval and stay released, avoiding repeated root pops at each new flight frame.


### Strict RO3 exterior, density and fountain source68

The saved native town has37 ordinary house envelopes: twelve primary frontages,
24 other existing house/inn/workshop lots and one added approach house. Shared
`ro3-facade-kit-v68.py` defines pierced timber facades, nine-light windows and
steep clay roof variants. Ground details fit actual traced front edges; awnings
clear raised approach terrain. `plan-ro3-density-v68.py` produces a source plan
that preserves roads, service access and patrol legs. Occupied house ground
increases13.1%; five rooted tree groups move as complete units.

The fountain is native physical geometry with tiered pools, a scalloped rim,
planted corners, green seating and two walkable terrain steps. Optional native
`texture.ripple` metadata drives a quiet shared shader clock and authored local
water UVs. No object-specific replacement collider or dynamic shadow/PBR pass
is introduced. Original material tile mips, actor registration and native
software resolution remain. Corner/floor bakes must follow geometry edits
sequentially. Ground bake invalidation and saved source/export parity stay active.

The review records intentional collision/floor changes, low-detail contacts,
pane clearance, actual service/field/save flow, offline cache and isolated timing.
Scoped exterior visual review is separate from user Golden acceptance and
physical-device performance. Boot/page/cache versions are68; original diffuse
artwork retains its67 filename. See `docs/review/wayfarer-v68/`.

### Regional capital source75

The current native layout `wayfarer-regional-capital-v75` has 256 × 288 world bounds, 54,848 square world units of contiguous city land, 172 houses, 78 trees and three new civic landmarks. All 37 original house assemblies retain their indexed geometry and UVs after rigid relocation. Existing services and both field destinations retain their identities. Native public/private paving is clipped against actual streets, gardens and retained raised contacts; public irregular stone uses continuous world UVs. Original gates are preserved as authoring references and replaced by wider native passages in the same service collections.

Decorative components in newly built houses are joined by material, role and shadow policy while original component vertex groups remain available for editing. Collision cores stay separate. Runtime opaque batches use 32-world-unit spatial cells; half-unit floor-shadow contacts share a material in 16-unit receiver chunks. The 4096² native floor atlas supports the larger extent, with original eight sun/four contact samples and cutout canopy alpha. These mechanisms bound submission work without changing actor art, gameplay speed or native drawing resolution.

The neighborhood refinement organizes 172 homes into continuous street-facing rows and shared back courts. Whole native roof/awning envelopes constrain placement, with small side passages instead of large isolated plot gaps. Owned paving fills inhabited street-defined blocks; continuous closed curb boundaries mark street/sidewalk edges, including garden/court holes. Explicit outward curb winding avoids closed-mesh normal inference on open faces. Existing civic/service precincts and their raised contacts remain authoritative. Eighteen additional native residents use local street circuits; runtime per-frame actor budgets are unchanged.

The final street hierarchy uses 8-unit cross streets, 9-unit district spines,
a 10-unit circuit and 14/12-unit ceremonial avenues. Five redundant through
lanes are removed so close frontage rows enclose larger inhabited blocks. Ten
whole models face the fountain square. Seven whole models face two owned courts
with native shared wells, seating, planting and craft features. Court and square
resident loops reuse existing actors. Derived floor contacts and complete rigid
assembly transforms remain authoritative; world units are not claimed as
recovered RO3 metre measurements.

Retained models can have a geometric front that differs from their root heading.
The square’s legacy infill records `frontageOffset` independently from its
assembly rotation. The source checker measures the actual thin axis and outward
side of every plaza door leaf, rather than treating placement metadata as proof
of a facing entrance. Original parts, UVs and indexed faces remain rigidly moved.
