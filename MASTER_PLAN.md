# ASTRAEON master execution plan

The user's architecture and concept-layout amendments supersede the earlier
Canvas-only environment decision. Continue the existing repository and playable
slice. Golden acceptance remains open; functional checks are supporting evidence.

## Governing architecture

Blender is the authoritative environment authoring space. The default Wayfarer
uses lightweight spatial meshes and original painterly materials in Three.js,
with high-resolution directional 2D actors rendered as alpha-tested world-space
quads in the same depth buffer. Canvas still assembles painted actor frames and
renders UI/effects and legacy zones. Whole-building cards are migration assets.
Characters remain illustrated sprites; combat, quests, inventory, skills, saves
and progression keep their existing simulation responsibilities.

No Ragnarok artwork, maps, textures, proprietary content or exact layouts may be
copied. The research informs separation of terrain, navigation, world objects,
portals, lighting and animation. Content expansion stays frozen until all three
Golden pillars pass in actual play.

## Concept layout authority

The latest supplied Wayfarer concept image governs district relationships. Adapt
its geometry to the fixed gameplay camera while retaining these relationships:

| Concept role | Authored playable role |
|---|---|
| West Gate and arrival bridge | Open fortified passage and bridge at the western town edge; field threshold outside it |
| Gate approach | Primary avenue into the public center, with readable destination sightlines |
| Central plaza | Fountain and circulation ring; clear movement and browsing space |
| Consortium Hall above plaza | Raised civic terrace, processional stairs, blue roofs, stone and gold landmark |
| Seafarer's Rest upper-left | Western social courtyard, porch, balcony, traveler service |
| Bronze Anvil lower-left | Western working frontage, chimney, covered yard, hearth and craft service |
| Market right of plaza | Merchant fronts, distinct awnings, goods and public browsing space |
| Luna Shrine upper-right | Quiet sacred approach and blue spire, separate from market density |
| Residential edges | Different domestic heights, roof forms, entry positions and garden treatments |
| Water, walls and edges | Raised defended bank, perimeter walls, open gate bridge and outward road |

The implementation must visibly read as this concept town. Generic ingredients,
repeated building silhouettes and labels alone do not satisfy the layout gate.

## Current implementation

`authoring/wayfarer-spatial.blend` is the saved environment source.
`tools/export-world-v3.py` exports its actual geometry, UVs, material catalog,
walkable surfaces, object IDs, transforms, blockers, parented services, patrols,
lights and portals into `world/v3/wayfarer-spatial.json`. The runtime consumes that
export directly. Do not maintain replacement runtime town coordinates.

`world/v3/renderer.js` batches static geometry by material and integrates painted
actors into shared depth. Navigation derives lightweight footprints and walkable
surfaces from the same source. A hidden navigation ramp follows the civic stairs;
this is visual/navigation separation, not expensive mesh physics. Bridges and
raised surfaces are included in ground picking and contact elevation.

`world/v3/locomotion.js` supplies distinct walk/run/sprint contact strategies,
start/stop/turn settling and absolute planted-foot elevations. Action sprites and
animation registration remain 2D and manifest driven. The existing action and
reaction states require full visual review. Sixteen original hit/death poses now
cover all eight directions, with source bounds, silhouette outlines and anchors
in the same animation manifest; nearest-cardinal fallback has been removed.

The material atlas is original ASTRAEON artwork. Three.js is vendored with its MIT
license; no runtime CDN or heavy PBR dependency is introduced.

## Renderer decision and limits

The bounded comparison uses the same `golden-proof.blend` export for Canvas and
WebGL, including the gate passage, raised span, tree, building and Warrior. Canvas
can sort split cards at ground depth but lacks a general shared spatial depth
buffer. Three consumes the actual geometry and supports elevated floor picking
and sprite quads without reconstructing the town. It is the primary candidate
and current implementation. A separate independently layered character canvas
is not an acceptable hybrid.

Software Chromium measurements are not physical-device certification. Rendering
cost, shared-depth traversal and visual integration remain acceptance criteria;
proof screenshots and CPU submission timings alone do not close them.

## Execution loop and acceptance

Continue inspecting, implementing, running, visually reviewing and refining:

1. Complete district traversal, services, minimap and town/field/save regression.
2. Review native front/behind walls, arches, canopy, stairs, terrace and bridge.
3. Refine district silhouettes, street joins, thresholds, foliage, lighting and density.
4. Review idle, walk, run, sprint, start, stop, turn, attack, hit and death in every required direction, including real elevations and occlusion.
5. Record concept-to-playable layout comparison, district placement comparison,
   building family/variant sheet and gameplay camera evidence on desktop/mobile.
6. Measure representative performance and publish the authorized repository changes.
7. Repeat Golden review until all three pillars pass together: concept-true town,
   strong Blender-authored spatial composition with efficient MMO readability,
   and correct integrated 2D character animation.

Legacy Canvas review reports remain historical evidence. They are not approval
of the spatial migration. Public Pages inspection currently encounters the
managed network's HTTP 403; do not claim the public build was reviewed locally.

For normal source edits, save the Blender scene and run its exporter. Initial
migration scripts are historical one-time steps. Refinement scripts operate on
the saved source; never recreate the town merely to export it.

## Research responsibilities

[Architecture](ARCHITECTURE.md), [reference study](RAGNAROK_REFERENCE.md) and
[research catalog](RESEARCH-SOURCES.md) retain their source caveats. NostalRO and
roBrowser inform browser responsibilities; Ragnarok Research Lab informs native
terrain/navigation/world/animation separation; BrowEdit informs level-authoring
workflow; rAthena informs NPC and portal responsibilities. Integrating the catalog
does not claim a fresh external source audit or adoption of RO file formats.
