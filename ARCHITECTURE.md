# Runtime architecture

Static, dependency-free browser client. Canvas2D paints an affine high-angle world with original illustrated assets; DOM/CSS owns menus and responsive controls. It is a local action RPG slice, not a networked MMORPG.

| Module | Actual responsibility |
|---|---|
| world-content.js | Authored Shenzhou props, roads, atlas regions, walker routes, five-region identity plan |
| input.js | Keyboard device bindings → action names and movement axes |
| combat.js | Pure ability definitions/compiler, cast/active/recovery timeline, cooldowns, world-space hit shapes, swept projectile collisions |
| animation.js + atlas-metadata.js | Presentation clips, per-frame image extraction and foot anchoring; distance-driven run cycle |
| scene.js | Cached authored paving, original environment sprites, depth fade and animated fountain/lamps |
| world-systems.js | Ambient walkers, gradual atmosphere parameters, quality presets and original WebAudio synthesis |
| game.js | Existing local state/progression/menu integration, movement, enemy AI, reactions, save, camera and presentation orchestration |
| qa.html | Same live iframe in four actual CSS viewport sizes; frame timing and state samples through validated postMessage |

## Coordinate contract
Ground uses ordinary Cartesian x/y (future renderer may map these to X/Z). Elevation is a separate pixel lift. Forward/inverse affine transforms are paired. The world never rotates into a diamond-shaped board. Ground and streets extend beyond the camera; props sort by projected ground depth. The camera starts at the player and follows with exponential time-based smoothing.

## Simulation boundary
`combat.js` has no renderer, DOM, audio, storage or clock dependency. Caller supplies simulation time, action origin, aim and entities, then consumes contact/release events. Paused menus and hidden tabs freeze simulation time. Dodge can cancel an action; cooldowns remain spent. Impact presentation does not determine damage timing. Remaining movement/AI/progression still live inside `game.js`; moving them into an `IGameSimulation` adapter is outstanding. No server-authority or prediction claim.

## Animation contract
Three original 36-pose archetype atlases. Idle/run, attack, cast, dodge, hit, knockdown/get-up/death, interact and sit clips exist. Run phase follows traveled ground distance. Actions use the corresponding timeline duration. Per-frame ground anchors align the lowest opaque frame pixels. These are illustrated pose sequences, not a rig with full directional blends; weapon/foot consistency and all transitions still require visual review before the character polish gate passes.

## Loading and persistence
Current zone spawns active enemies; old enemies are discarded on transition. Shared image atlases load once. This is zone activation, not chunk streaming. LocalStorage retains the existing save key and progression; failed writes notify the player. Active dungeon runs reset on reload. SW serves navigations network-first and versioned static assets cache-first. Real multiplayer, account persistence and a shared economy are future work.
