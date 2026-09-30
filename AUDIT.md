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

## Current visual gate
FAILED: primitive town architecture/trees, transparent roof half, sparse composition, repeating terrain, four-frame locomotion and static NPC crowd. No production-ready claim.
