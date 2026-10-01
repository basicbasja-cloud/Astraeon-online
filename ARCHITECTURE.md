# Runtime architecture

Static, dependency-free browser client. Canvas2D paints an affine high-angle world with original illustrated assets; DOM/CSS owns menus and responsive controls. It is a local action RPG slice, not a networked MMORPG.

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
Ground uses ordinary Cartesian x/y (future renderer may map these to X/Z). Motion elevation is a separate z coordinate, converted to pixel lift at projection; current terrain elevation is flat. Forward/inverse affine transforms are paired. The world never rotates into a diamond-shaped board. Ground and streets extend beyond the camera; props sort by projected ground depth. The camera starts at the player and follows with exponential time-based smoothing.

## Simulation boundary
`combat.js` has no renderer, DOM, audio, storage or clock dependency. Caller supplies simulation time, action origin, aim and entities, then consumes contact/release events. Paused menus and hidden tabs freeze simulation time. Dodge can cancel an action; cooldowns remain spent. Impact presentation does not determine damage timing. Enemy attack geometry, navigation, save defaults and world claims now have independent pure modules. Movement/AI/progression orchestration still lives inside `game.js`; moving them into an `IGameSimulation` adapter is outstanding. No server-authority or prediction claim.

## Animation contract
Three original archetypes each have eight authored directions and six poses: idle, two locomotion strides, anticipation, contact and crouched reaction. The guardian has eight poses per direction; regular enemies have idle and attack views. Runtime yaw is continuous and smoothly follows movement, target or aim; presentation projects facing through the ground camera and chooses the closest screen-space 45° view without horizontal mirroring. Gait phase follows traveled distance. Three additional walk sheets provide eight stride phases for six directions; north and northwest keep the accepted two-pose rear cycle because the extended sheets drifted toward side/front views. Warrior omits the corrupted stride and distributes seven accepted keys evenly across a cycle, avoiding a repeated hold. Cached source-silhouette paths clip neighboring cell pieces without repainting the original artwork. Source bounds exclude neighboring atlas fragments and align visible feet. Golden Warrior registration now uses source-space boot contacts and stable 70-pixel visible body scale. Eight separate hit/death frames provide four reviewed cardinal reaction views; diagonal facing selects the nearest cardinal without mirroring. Death holds its fallen pose before fading in the final portion of recovery.

These are painted 2.5D assets, not skinned 3D characters. The movement layer tracks stance contacts, but sprites do not articulate limbs to those contacts. Hand/back/hip coordinates are approximate world-space attachment positions, not imported rig sockets. Attack impacts wait for actual aim convergence; projectiles and slash effects use the same continuous world direction. Directional pose consistency, limited enemy locomotion and richer transitions remain art polish work.

## Loading and persistence
Current zone spawns active enemies; old enemies are discarded on transition. Boot waits for town and character art. Zone transitions pause behind a loading overlay and await that zone’s ground/enemy atlases; failed loads preserve zone and travel gold and can be retried. Shared image atlases load once. This is zone activation, not chunk streaming. LocalStorage retains the existing save key and progression, normalized to saveVersion 3; failed writes notify the player. Active dungeon runs reset on reload. SW serves navigations network-first and versioned static assets cache-first (v28). Core town/hero art is precached; field/forest/guardian art is cached when visited. Unvisited zones require a connection. Real multiplayer, account persistence and a shared economy are future work.

## Base Skills and single-layer Nodes

Twelve starting-class skills are deliberately authored in `combat.js`; six attack skills accept explicit compatible nodes from `skill-nodes.js`. A save stores one string per Base Skill ID in `skillNodes`. The compiler retains base targeting, cost, cooldown, shape and class identity. Invalid, nested or incompatible choices are discarded during normalization. Old `techniques`, `active`, `path` and unknown progress fields survive save migration, but the old free-form compiler and Advanced Path controls are inactive. Existing bonuses are not stripped from returning saves.

Tempest and Arrow Rain each lock an authored area and pulse three times. Published fields survive ordinary cast recovery/cancel and clear on zone/class changes. Fire burns and ignites; Ice builds frost and freezes ordinary foes; Lightning chains through clear sight lines and briefly shocks; Gravity pulls with collision checks; Qi restores Resolve on contact; Spirit heals inside the area; Void delays ordinary enemy attacks; Wind backsteps after projectile release; Plasma follows a marked foe before its delayed burst. Bosses resist freeze/shock/disruption and have reduced pull.

Warrior combos earn Resolve on contact; Mage Mana recovers faster between casts; Ranger Focus recovers faster while stationary. Selected targets preserve facing while moving, including reverse gait when backing away. This does not add dedicated strafe animation art. Tuning is available in town or at an actual nearby camp after clearing nearby foes. Menus pause simulation. No skill trees, advanced evolutions or online authority are implemented.

## Mainline sprite presentation

The client loads the existing painted Warrior, Mage and Ranger atlases through the Canvas renderer. There is no opt-in WebGL character renderer or model download. Movement and aim remain separate, with continuous world-space direction selecting eight authored views. Distance-based gait and normalized action impact timing keep presentation coupled to actual movement and combat; damage remains controlled by the simulation. Existing skills and Nodes express their variations through behavior and VFX.

## Golden court presentation

`AstraeonContent.goldenScene` records the town concept, selected Warrior, Consortium landmark, court polygon, controlled palette, eastbound axis, focal order and pending art status. Roads have avenue/street/service/field roles: paved main routes frame the court, narrow dirt routes serve shops/courtyards, and the eastern stone approach gives way to dirt beyond the existing Caravan Gate. `scene.js` maps shared limestone through the affine ground projection and caches material/edge/wear composition. The fountain footprint is in `townBlocks`, so movement, pathfinding and projectiles agree with its occupancy. Existing NPC approaches and the connected region loop remain functional. This is one candidate block under a visual approval gate.

The v27 hall image replaces only `guild-hall`; the original town atlas remains in use for all other assets. Its front steps define the anchor. Town verge material is downsampled, toned and mapped through the shared world projection once. Paving/soil/edge/drainage composition retains a single terrain cache and visible-region blits. The Registrar/Quest Board, Artisan, Housing Keeper and Gatekeeper keep their original interactions at revised facility approaches.

## Shared projection and registration — v28

The affine ground basis is world X `(48,14)`, world Y `(-32,22)`. `world-view.js` owns projection, inverse and material matrices. Town and outdoor caches, terrain patterns, depth sorting, sprite facing, pointer targets and VFX consume that contract. Painted facades retain their authored view and dimensions; camera zoom and 44 × 40 town bounds are unchanged.

Town cache is 4000 × 2100, offset (1450,100); outdoor road cache is 3000 × 1800, offset (1150,160). Visible-region blits avoid scaling the whole cache per frame. Temporary construction masks can increase boot memory. Forecourts are shared source data rather than renderer literals. Building shadows use matching identified occupied footprints; NPC labels are drawn after actors with nearby-service filtering and collision separation. NPCs turn toward nearby players.

`sprite-motion.js` adds bounded foot-pivot rise/lean and action offsets. It does not move collision, extend weapon range or set damage timing. Combat remains world-space; visual direction selection accounts for the camera.
