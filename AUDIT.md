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
Preserve the working gameplay loop and saves. Establish one city benchmark with properly anchored original painted assets, authored roads, layered depth sorting and occlusion, and camera correction before content expansion. Canvas2D can validate this art/scale/combat slice without destroying current systems. A WebGL migration is not yet justified by a measured renderer bottleneck; record this limitation and reassess after the benchmark. The current RO1-inspired production direction uses painted sprites and authored 2.5D spaces; a renderer migration is not a prerequisite for this benchmark.

## Original visual gate
FAILED at the audit baseline: primitive town architecture/trees, transparent roof half, sparse composition, repeating terrain, four-frame locomotion and static NPC crowd. No production-ready claim.

## Directional pass status — 2026-09-30

Continuous world-space transforms, smooth heading changes, analog speed, aim-aligned impacts/projectiles and eight-direction painted archetype/enemy/guardian artwork are implemented. Moonveil now has three connected rooms and a boss court, with collidable walls and gated progression. Existing local progression and save format are preserved.

The original audit table above records the starting state. This pass does not close the full production gate: animation transitions and atlas consistency need further polish; regular enemy locomotion has two poses; terrain elevation, a complete online adapter, streaming and real phone performance remain outstanding. The renderer remains painted Canvas2D 2.5D.

## Connected Shenzhou pass — 2026-09-30

Field and forest now use distinct painted materials, authored roads, layered trees/camps/mill/shrine props, useful exploration markers and a collidable four-room painted ruin. Replaced primitive active dungeon walls/floor and default-field block geometry. Main controls use original SVG icons, the phone quest strip is collapsible, and the dungeon minimap matches its authored rooms.

A fresh Ranger completed the field contract, one-time supply claim, natural forest/shrine route, all four rooms, guardian phases and three attacks, reward return, armor crafting/equipment and persistent reload through real UI input. Resolved unreachable gates, arrival-target cancellation, obstacle pursuit and wall-crossing projectiles. Save normalization and failed zone-load retry preserve progress.

Full production gate remains open: two rear walking directions retain the shorter accepted cycle, dedicated action/reaction/death transitions and atlas consistency need art work, terrain elevation/interiors and real mobile measurements are absent, and social/economy features remain local. No five-region expansion or live MMO completion is claimed.

## Scale and canonical skill audit — 2026-09-30

The master production brief supersedes historical scale and progression assumptions. Local runtime comparison found humanoids too large beside doors, civic buildings too small, roads compressed, and the original composer/Advanced Path controls inconsistent with current scope.

Corrected the related system: 44 × 40 town footprint, neighborhood anchors, wider avenue/branches, enlarged service architecture and dominant civic terrace, smaller human-relative actors, scaled terrain/props, paired inverse input and responsive camera framing. Plaza, market, Consortium approach and caravan gate were inspected in local browser screenshots; the city benchmark remains provisional until public inspection. Painted directional characters are retained, without blocky replacements or a false claim of skinned 3D.

Three starting classes retain twelve Base Skills. Six attack skills accept authored compatibility from nine Nodes with real burn/frost/chain/pull/resource/heal/disruption/backstep/heat mechanics. Tempest and Arrow Rain pulse in locked areas. Removed active free-form composition and Advanced Path evolution. Save v3 retains old progression and archived legacy fields. Phone menu review found and fixed action controls covering the skill cards; menus now hide combat overlays and portrait cards use one column.

Evidence: 42 pure checks; 44 Chromium smoke checks under `/Astraeon-online/`; 10 actual UI/Node gameplay checks; six fresh-Ranger journey checks passed, including actual cleared-camp rest/Node tuning and a physical return to town before crafting/reload. No runtime or failed-resource errors. Additional town service/gate and live QA iframe checks confirmed all four viewport sizes, v25 cache and repository-subpath SW scope. See PERFORMANCE.md for measured limits. Raw screenshots/reports are external task artifacts under `/workspace/setup-checks/public-production/`.

### Deployment / public acceptance

The earlier connected pass was committed/pushed as `c7e4a73313f8b4d0291682a6a1333051f51b5ad7`; [Pages run 24](https://github.com/basicbasja-cloud/Astraeon-online/actions/runs/36707426745) completed successfully for that exact commit. Significant changes in this pass must likewise be pushed and matched to a successful Pages run.

The current environment can read GitHub HTML and push using injected HTTPS Git proxy authentication. The public Pages host and API host are denied by the environment proxy (HTTPS CONNECT HTTP 403; Chromium `ERR_TUNNEL_CONNECTION_FAILED`). This is a network prerequisite, not evidence of a broken deployment or missing token. Required domain additions are saved in the cloud environment draft; saving the draft does not apply runtime access.

**Public browser gameplay, public screenshots and public visual comparison are blocked, not passed.** Once the network settings are applied, open the public URL in a fresh browser context, confirm the current cache version, play movement/combat/services/camp/dungeon, review plaza/market/gate/field/ruin and both phone orientations, inspect console/resources and compare screenshots. Local evidence and successful Pages workflows do not close this gate. Full production animation, architectural details, elevation, real-device performance and online simulation also remain open.

## RO1-inspired Golden Town / Sprite consolidation — 2026-09-30

The latest character direction supersedes the rigged migration: existing painted Warrior/Mage/Ranger remain the mainline presentation. Removed all optional 3D boot/render hooks and kept the unapproved experiment outside the checkout. No new class, sprite family, skill, map or district was added. Both Golden Sprite Character and Golden Town Scene approvals are pending.

Rebuilt only the existing central court and approaches: removed competing central props/canopy, clustered market goods, moved benches to edges, reduced overlapping ambient routes, relocated the existing shrine into its connected western Spirit courtyard and cleared service approaches. Avenue, secondary street, service path and six-sided plaza have explicit hierarchy. The eastern stone approach ends at the Caravan Gate and becomes a narrower dirt continuation toward the field. Shared painted limestone follows world projection; dust, edge intrusion, wear and softer contact gradients replace screen-axis paving and hard shadow stamps. Fountain collision prevents walking inside its basin.

Local regression passed 42 pure checks, 44 regular-client repository-subpath browser checks and all six connected expedition checks, with no reported runtime/resource errors. Actual input also verified basin collision, Consortium access market access and walking through the city gate into the field, and captured desktop/tablet/both phone orientations. Movement test fixtures now start on the open southern avenue instead of requiring movement through the newly collidable basin; speed/facing assertions remain.

Door clearance, architectural perspective and final sprite/scene cohesion still need visual acceptance. The original guild doorway is near humanoid height. Public browser inspection remains blocked by the environment proxy; successful local tests and deployment do not approve either visual gate. See GOLDEN_SCENE.md.
