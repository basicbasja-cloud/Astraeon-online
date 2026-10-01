# ASTRAEON master world plan

Canonical integration: 2026-10-01. Scope: existing Wayfarer Court, Golden Warrior,
and the connected playable slice. The user's Canvas2D integration direction
supersedes the v3 package's preferred PixiJS proof. The package permits the
existing renderer when it meets the proof requirements with less risk.

## Governing decisions

- Keep Canvas2D, original painted directional actors, existing art, paired camera
  projection, controls, combat, skills/Nodes, quests, inventory and save compatibility.
- Concept art supplies visual grammar and spatial intent. Blender supplies authored
  placement, volumes, clearance and approach anchors. ASTRAEON-native JSON supplies
  the browser's spatial data. Research supplies responsibilities and workflows.
- No Ragnarok art, textures, sprite sheets, maps, exact layouts or proprietary
  content may enter the project. No RO-format compatibility layer is required.
- Content expansion stays paused until Golden Town and Golden Character review.
  Proofs and replacement work use existing town functions and the current slice;
  other towns, classes, districts and multiplayer are deferred.
- One object has one spatial record. Rendering parts, collision solids, passages,
  navigation, entrances, lighting and visibility derive from that record. Source
  image bounds do not define collision.
- Existing painted facades retain their authored perspective. Do not rotate or
  mirror paintings to simulate a new building orientation. Replace a bounded
  incompatible view only after reviewing the blockout.

## Evidence and research responsibilities

The attached [research catalog](RESEARCH-SOURCES.md), repository
[architecture](ARCHITECTURE.md) and [reference study](RAGNAROK_REFERENCE.md) are
inputs to this plan. They are not evidence that every proposed system exists.
The architecture/reference attachments describe an earlier v28 baseline; preserve
their source caveats and assess implementation against the current code.

| Reference | Apply to ASTRAEON | Evidence boundary |
|---|---|---|
| NostalRO | Simulation/rendering/resource separation, scene passes, focused viewers | Priority for further study; new catalog links are not a completed code audit |
| Ragnarok Research Lab | Terrain/navigation/world/animation responsibilities and coordinate contracts | Design ASTRAEON JSON; do not adopt GND/GAT/RSW/SPR/ACT parsers |
| BrowEdit3 | Placement, floor grounding, blockout review and export workflow | Blender replaces the editor role; its lightmapper does not establish Gravity's workflow |
| roBrowser | Camera-relative direction, anchors, browser loading and shared scene data | Historical pinned sources in the study are inspected; the catalog's newer client is a separate research target |
| rAthena | NPC/warp/map/gameplay responsibilities independent of images | Server reference, not a renderer; online authority remains future work |

For each research task record the pinned source, observed behavior, ASTRAEON
equivalent, preserved behavior, proposed change and verification. Separate an
observed source fact from an ASTRAEON recommendation. No fresh external inspection
is claimed by integrating these documents.

## Delivery sequence and gates

| Stage | Concrete deliverable | Exit evidence |
|---|---|---|
| 1. Native contracts | Terrain, Navigation, TownObject and ACT-like AnimationManifest schemas; initial existing-court placement/footprint manifest | Schema validation, stable IDs, shared coordinates and a legacy-compatible adapter |
| 2. Blender + Canvas proof | Limited terrain patch, layered building, tree, gate and Golden Warrior; same projection/pathfinding/rig as the game | Solid pillars, open passage, front/behind sorting, selective roof/canopy visibility, stable shadows, grounded feet |
| 3. Warrior contact review | Eight directions with separate walk/run/sprint contact, cycle distance and pose strategies; start/stop/turn | Gameplay-size playback video, alternating stance, no obvious skating, rear-view or scale pops |
| 4. Existing-court blockout | Import current placement/footprint/roads/forecourts into Blender; inspect top-down and gameplay camera before edits | Reachable existing services, clear fountain circulation, hall sightline, market frontage and gate mouth |
| 5. Bounded runtime import | Canvas consumes exported placements; collision/nav/entrances consume the same records; retain painted art and current services | Before/after placement parity, save/reload, combat, interactions and town → field regression |
| 6. Art/light refinement | Split existing art into foundations/walls/roof or trunk/canopy where proven necessary; coherent sun and visible-source emitters | Arrival/approach/behind/departure captures; no whole-object fade or roof-dependent shadow removal |
| 7. Golden acceptance | Repeatable desktop, portrait, landscape and tablet route; traversal/contact/combat video; frame/memory evidence | Explicit visual acceptance of both town and character; local tests alone do not close the gate |

The v3 concept's West Gate → Main Avenue → Plaza/Fountain → Consortium Hall
hierarchy is the target for a later approved Wayfarer rework. The current slice's
eastbound Caravan Gate → Goldenfield connection and save positions remain valid
during the initial import. Do not silently swap gate directions, rename services,
or relocate the full town in a data-format migration.

All open spaces in any approved layout edit must have a role: approach, forecourt,
plaza circulation, customer frontage, work yard, service access, residential garden
or public green. Reuse architecture within functional families; avoid one facade
serving unrelated inn, shrine, workshop and housing roles.

## Runtime boundaries

`world-view.js` owns Cartesian projection/inverse and scale. Blender world XY
exports unchanged; Z remains separate elevation. Terrain owns surfaces/materials;
navigation owns traversability derived from solids; TownObject owns geometry,
painted presentation registration, portals and emitters; actor metadata owns timing,
anchors, contacts and attachments. `navigation.js`, the existing Warrior rig and
simulation remain reusable consumers. DOM continues to own menus and controls.

Import the manifest before modules capture town content. Validate it before
activating the scene. Keep export and renderer caches separate from source data.
Blender is an authoring dependency, not a player download. The first adapter must
preserve placement/collision parity; subsequent polygon/elevation edits need their
own traversal review. Do not maintain a second hand-authored collision list.

## Current implementation and limits

The v3 branch provides four schemas, a reusable spatial compiler, an editable
Blender proof and exporter, a playable Canvas proof at `proof.html`, shared
collision/nav/visibility/shadow overlays and a contact scrubber. Distinct locomotion
atlases retain the original painted Warrior costume. The main game remains the
painted Canvas client; the preview does not alter saves or combat.

`authoring/wayfarer-court.blend` imports 45 current town objects and their existing
occupancy, roads, plaza and forecourts. `world/v3/wayfarer-court.json` exports their
native records; `world/v3/town-import.js` adapts them for existing `scene.js`,
`town-structure.js` and `game.js` consumers. Open
[the painted import preview](index.html?world=court-v3) to review it. Default play
retains the current data path until the import is accepted. Rectangular occupancy
and art positions have parity checks. No collisions are inferred for visual-only
objects. New rotated/polygon footprints are rejected by this initial adapter.
Existing-court mass heights are approximate authoring aids, not accepted roof or
lighting geometry; the painted presentation retains its current rendering.

The proof is a structural blockout, not a finished town or an accepted character.
The court import preserves the current layout; it is not the future concept town.
NPC interactions, walker routes and some art masks still use legacy data. Moving
services or enabling the import as the default requires those references to join
the shared contract and pass traversal/art review. Real
ramps, stairs, bridges, multi-level navigation and spatial ambient sampling remain
unimplemented. The proof's depth policy is a fixed-camera ground sort, not a 3D
depth buffer. Do not infer arbitrary height support from exported mesh vertices.

`tools/build-court-blender.py` is the initial legacy snapshot importer, not the
normal command for edited scenes. After changing Blender objects, use
`blender -b authoring/wayfarer-court.blend --python tools/export-world-v3.py`.
This preserves authored changes; rebuilding the initial snapshot would replace them.

## Renderer reconsideration

Canvas2D is the current decision. PixiJS or Three.js may be reconsidered only with
a measured failing case involving sustained real height, bridges, geometry
occlusion/lighting or unacceptable browser cost, plus a bounded comparison using
the same world contract. An engine switch is not an initial integration task.
Future 3D world sprites must participate in the environment depth solution.
