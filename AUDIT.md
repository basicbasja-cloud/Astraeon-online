# Repository audit — 2026-09-30

Baseline: GitHub `0657fa4a6efbdcf75ab042b23c36e45bec897966` (Pages run 19 succeeded). Inspected source, original atlases and the actual browser town.

| System | Evidence | Decision | Production gap |
|---|---|---|---|
| Runtime | Static HTML, CSS, single IIFE in game.js, Canvas2D | REFINE | Simulation/render/UI share globals; no module boundaries |
| Camera | Paired affine forward/inverse mapping, Cartesian ground coordinates | REFINE | Startup camera drifts in from origin; follow depends on rendered frame count |
| Terrain | One repeating illustrated ground texture per viewport plus zone tint | REPLACE | Ground ignores designed paths; repeated terrain and no elevation |
| Town | Four block collision rectangles, six service NPCs, tiny procedural props | REPLACE presentation / KEEP interactions | Placeholder buildings, sparse streets, no surrounding density; roof surface is transparent |
| Characters | Original alpha hero atlas, four rows × four frames; foot anchor inferred | REFINE / add art | Atlas has only idle/run/slash/roll; compressed frame geometry and silhouette; NPCs reuse hero |
| Combat | Immediate damage in action(), three damage multipliers, dodge immunity, enemy windups | KEEP rules / REPLACE timing | Hits precede contact, no hit stop/audio, telegraph size does not match world damage radius |
| Enemies | Wolf atlas plus procedural wisps/drones; ranged/melee, boss phase and adds | REFINE | Two basic AI behaviors, primitive boss silhouette, no real projectile travel |
| Progression | Inventory, crafting, class registry, skill composer, quests, chapters | KEEP | 22 class names largely share mechanics; composer options exceed real behavior |
| Dungeon | Three waves then boss, first-clear unlock and relic | KEEP / REFINE | No connected entrance journey, no authored dungeon space |
| Save | localStorage astraeon-iso-v1, migration defaults for newer fields | KEEP / REFINE | No validated schema/version, active run resets, storage errors unreported |
| Input | Keyboard, click-to-move, pointer joystick, buttons | KEEP / REFINE | Direct key coupling, asymmetric screen speed; aim/profile absent |
| UI | DOM menus, CSS media queries, mobile overlay controls | REFINE | Layered conflicting CSS, large quest box, emoji icons; tiny-screen scale override |
| Audio/weather/time | No audio subsystem; ambient dots only | ADD | World silent and static |
| Build/deploy | No dependencies/build; GitHub Pages static root, versioned SW | KEEP | Cache-first HTML risks stale deployment; no automated regression gates |
| Performance | DPR capped at 2; every entity and ground visible drawn each frame | REFINE after measurement | UI rebuilt 4×/sec, shadow/filter calls, frame-dependent camera/FX; no profiler |
| Online | No network simulation | PREPARE boundary only | Social/economy are local simulations; no live MMO claims |

## Priority and engine decision
Preserve the working gameplay loop and saves. Establish one city benchmark with properly anchored original painted assets, authored roads, layered depth sorting and occlusion, and camera correction before content expansion. Canvas2D can validate this art/scale/combat slice without destroying current systems. A WebGL migration is not yet justified by a measured renderer bottleneck; record this limitation and reassess after the benchmark. This does not claim the current renderer fulfills the eventual 3D environment requirement.

## Original visual gate
FAILED at the audit baseline: primitive town architecture/trees, transparent roof half, sparse composition, repeating terrain, four-frame locomotion and static NPC crowd. No production-ready claim.

## Directional pass status — 2026-09-30

Continuous world-space transforms, smooth heading changes, analog speed, aim-aligned impacts/projectiles and eight-direction painted archetype/enemy/guardian artwork are implemented. Moonveil now has three connected rooms and a boss court, with collidable walls and gated progression. Existing local progression and save format are preserved.

The original audit table above records the starting state. This pass does not close the full production gate: animation transitions and atlas consistency need further polish; regular enemy locomotion has two poses; terrain elevation, a complete online adapter, streaming and real phone performance remain outstanding. The renderer remains painted Canvas2D 2.5D.

## Connected Shenzhou pass — 2026-09-30

Field and forest now use distinct painted materials, authored roads, layered trees/camps/mill/shrine props, useful exploration markers and a collidable four-room painted ruin. Replaced primitive active dungeon walls/floor and default-field block geometry. Main controls use original SVG icons, the phone quest strip is collapsible, and the dungeon minimap matches its authored rooms.

A fresh Ranger completed the field contract, one-time supply claim, natural forest/shrine route, all four rooms, guardian phases and three attacks, reward return, armor crafting/equipment and persistent reload through real UI input. Resolved unreachable gates, arrival-target cancellation, obstacle pursuit and wall-crossing projectiles. Save normalization and failed zone-load retry preserve progress.

Full production gate remains open: painted 2.5D eight-view characters are not a skinned 3D pipeline, two rear walking directions retain the shorter accepted cycle, dedicated action/reaction/death transitions and atlas consistency need art work, terrain elevation/interiors and real mobile measurements are absent, and social/economy features remain local. No five-region expansion or live MMO completion is claimed.
