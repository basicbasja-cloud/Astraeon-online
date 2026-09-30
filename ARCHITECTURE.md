# Runtime architecture

Static, dependency-free browser client. Canvas2D paints an affine high-angle world with original illustrated assets; DOM/CSS owns menus and responsive controls. It is a local action RPG slice, not a networked MMORPG.

| Module | Actual responsibility |
|---|---|
| world-view.js | Shared projection/inverse, responsive zoom/framing, human-relative actor dimensions and zone bounds |
| skill-nodes.js | Authored compatibility, single-node application/normalization and pure contact status model |
| world-content.js | Authored Shenzhou props, roads, atlas regions, walker routes, five-region identity plan |
| input.js | Keyboard device bindings → action names and movement axes |
| combat.js | Pure ability definitions/compiler, cast/active/recovery timeline, cooldowns, world-space hit shapes, swept projectile collisions |
| character-motion.js | Continuous position, yaw, facing modes, analog velocity, bounded turning, gait and stance contacts |
| animation.js + directional-art.js + directional-metadata.js | Eight authored views, pose selection, explicit source bounds and ground anchoring |
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
Three original archetypes each have eight authored directions and six poses: idle, two locomotion strides, anticipation, contact and crouched reaction. The guardian has eight poses per direction; regular enemies have idle and attack views. Runtime yaw is continuous and smoothly follows movement, target or aim; presentation chooses the closest 45° view without horizontal mirroring. Gait phase follows traveled distance. Three additional walk sheets provide eight stride phases for six directions; north and northwest keep the accepted two-pose rear cycle because the extended sheets drifted toward side/front views. One warrior stride repeats an accepted neighboring pose to exclude a connected sword fragment. Cached source-silhouette paths clip neighboring cell pieces without repainting the original artwork. Source bounds exclude neighboring atlas fragments and align visible feet.

These are painted 2.5D assets, not skinned 3D characters. The movement layer tracks stance contacts, but sprites do not articulate limbs to those contacts. Hand/back/hip coordinates are approximate world-space attachment positions, not imported rig sockets. Attack impacts wait for actual aim convergence; projectiles and slash effects use the same continuous world direction. Directional pose consistency, limited enemy locomotion and richer transitions remain art polish work.

## Loading and persistence
Current zone spawns active enemies; old enemies are discarded on transition. Boot waits for town and character art. Zone transitions pause behind a loading overlay and await that zone’s ground/enemy atlases; failed loads preserve zone and travel gold and can be retried. Shared image atlases load once. This is zone activation, not chunk streaming. LocalStorage retains the existing save key and progression, normalized to saveVersion 3; failed writes notify the player. Active dungeon runs reset on reload. SW serves navigations network-first and versioned static assets cache-first (v26). Core town/hero art is precached; field/forest/guardian art is cached when visited. Unvisited zones require a connection. Real multiplayer, account persistence and a shared economy are future work.

## Base Skills and single-layer Nodes

Twelve starting-class skills are deliberately authored in `combat.js`; six attack skills accept explicit compatible nodes from `skill-nodes.js`. A save stores one string per Base Skill ID in `skillNodes`. The compiler retains base targeting, cost, cooldown, shape and class identity. Invalid, nested or incompatible choices are discarded during normalization. Old `techniques`, `active`, `path` and unknown progress fields survive save migration, but the old free-form compiler and Advanced Path controls are inactive. Existing bonuses are not stripped from returning saves.

Tempest and Arrow Rain each lock an authored area and pulse three times. Published fields survive ordinary cast recovery/cancel and clear on zone/class changes. Fire burns and ignites; Ice builds frost and freezes ordinary foes; Lightning chains through clear sight lines and briefly shocks; Gravity pulls with collision checks; Qi restores Resolve on contact; Spirit heals inside the area; Void delays ordinary enemy attacks; Wind backsteps after projectile release; Plasma follows a marked foe before its delayed burst. Bosses resist freeze/shock/disruption and have reduced pull.

Warrior combos earn Resolve on contact; Mage Mana recovers faster between casts; Ranger Focus recovers faster while stationary. Selected targets preserve facing while moving, including reverse gait when backing away. This does not add dedicated strafe animation art. Tuning is available in town or at an actual nearby camp after clearing nearby foes. Menus pause simulation. No skill trees, advanced evolutions or online authority are implemented.

## Mainline sprite presentation

The client loads the existing painted Warrior, Mage and Ranger atlases through the Canvas renderer. There is no opt-in WebGL character renderer or model download. Movement and aim remain separate, with continuous world-space direction selecting eight authored views. Distance-based gait and normalized action impact timing keep presentation coupled to actual movement and combat; damage remains controlled by the simulation. Existing skills and Nodes express their variations through behavior and VFX.

## Golden court presentation

`AstraeonContent.goldenScene` records the authored court polygon, controlled palette, focal order and pending art status. Roads have avenue/street/service/field roles: paved main routes frame the court, narrow dirt routes serve shops/courtyards, and the eastern stone approach gives way to dirt beyond the existing Caravan Gate. `scene.js` maps shared limestone through the affine ground projection and caches material/edge/wear composition. The fountain footprint is in `townBlocks`, so movement, pathfinding and projectiles agree with its occupancy. Existing NPC approaches and the connected region loop remain functional. This is one candidate block under a visual approval gate.
