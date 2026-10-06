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
portals, lighting and animation. Full production of a second major town stays
frozen until Wayfarer passes Golden acceptance and the required productionization
pass below is complete.

## Current capital authority — 6 October 2026

The latest user direction supersedes the fixed concept layout below. Expand and reorganize Wayfarer as one regional capital with geometric streets, a royal ceremonial axis, greater housing density and substantial civic landmarks. Prontera supplies scale, block placement and street-hierarchy reference; Wayfarer retains its own geometric blueprint. The original concept supplies the theme, and all ten RO3 reference images remain the hard visual target. The current implementation keeps generous public streets beside close frontages, adds two inward-facing owned courts and orients ten nearby buildings toward the fountain square. The active reviewed plan is `docs/review/wayfarer-capital-v75/plan.json`; the native Blender scene remains the geometry authority. This expands the existing city and does not authorize a separate second-city production pass.

## Historical concept layout authority

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
surfaces from the same source. Hidden contact rectangles follow the civic and
shrine tread tops, retaining the old ramps as inactive source references;
this is visual/navigation separation, not expensive mesh physics. Bridges and
raised surfaces are included in ground picking and contact elevation.

`world/v3/locomotion.js` supplies distinct walk/run/sprint contact strategies,
start/stop/turn settling and absolute planted-foot elevations. Action sprites and
animation registration remain 2D and manifest driven. The existing action and
reaction states require full visual review. Actor quads remain upright in world
space, and action offsets follow their full projected facing direction. Sixteen original hit/death poses now
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
8. After Golden visual, gameplay, animation and performance acceptance, complete
   the required productionization pass below before full production of City 2.

Legacy Canvas review reports remain historical evidence. They are not approval
of the spatial migration. Public Pages inspection currently encounters the
managed network's HTTP 403; do not claim the public build was reviewed locally.

For normal source edits, save the Blender scene and run its exporter. Initial
migration scripts are historical one-time steps. Refinement scripts operate on
the saved source; never recreate the town merely to export it.

## Production scalability requirement — mandatory Golden Foundation deliverable

This amendment extends the existing execution plan; it does not restart the
project or interrupt the current Golden Wayfarer implementation. Visual quality
remains higher priority than framework elegance. All earlier Golden completion
criteria remain active.

**Order of work:** complete and visually approve the Golden Wayfarer playable
slice → extract its proven production workflow → verify the reusable city
pipeline → begin full production of the second major town.

**Current status:** Golden acceptance remains open. The Wayfarer visual and
playable implementation loop remains the active phase. Productionization is a
required, pending phase, not permission to build a generic framework now. A
passing test count, technical proof, preview or repository push cannot open it.

### Entry gate and anti-premature-abstraction rule

Begin the dedicated productionization pass only after Wayfarer passes its
visual, gameplay, animation and performance acceptance criteria in actual play.
Record the accepted source/build revision and its visual, traversal, animation
and representative performance evidence so extraction has a stable baseline.

Only extract systems proven by that completed Golden Wayfarer. Do not generalize
a system solely because it might be useful later. Keep Wayfarer-specific
solutions local while their design is still undergoing visual iteration. Reuse
and preserve the accepted game, saved Blender scene, native contracts, exporter,
2D animation manifests and gameplay systems rather than rebuilding them.

### Required separation

| Responsibility | Productionization deliverable |
|---|---|
| Generic engine / world systems | Blender → runtime exporter; world/spatial contract; navigation; portals; collision; elevation; NPC/service markers; lighting metadata; Three.js world renderer; shared-depth 2D actor integration; minimap/world markers; town-field transitions |
| Reusable environment kits | Terrain and road modules; wall/gate/bridge modules; civic, residential, market, workshop and shrine architecture modules; vegetation modules; prop libraries; material/palette definitions |
| City-specific content | Wayfarer layout, landmarks, Consortium Hall, district composition, local palette, local props, local NPCs, lore and quests |

City-specific content must not be hardcoded into reusable engine modules.
Shared systems consume authored world data and metadata; city definitions select
kits and supply their own content. Unique landmarks belong to city content.
Generic material libraries and palette mechanisms stay separate from a city's
chosen palette. Visual geometry and gameplay metadata must continue to originate
from the same authored IDs and transforms.

During this pass, audit the existing boot/world binding, renderer activation,
camera/zone framing, content import and local authoring scripts for Wayfarer
assumptions. Move stabilized city assumptions into city definitions or authoring
presets where practical. Keep unique landmark rules local. This is extraction
from accepted implementation, not a combat, quest, inventory, save or skill rewrite.

### Building kit requirement

Do not scale future towns by cloning complete buildings. Reuse primarily at
component level: wall sections, foundations, roofs, dormers, windows, doors,
columns, arches, balconies, chimneys, awnings, fences, signs, garden pieces and
structural details. Use those components to author multiple distinct variants,
with entrances and roof orientation responding to the actual street/courtyard
plan. Retain the building-variety and district-identity requirements.

Provide data-driven building definitions or equivalent reusable authoring
presets. A residential variant must support at least:

```yaml
ResidentialVariant:
  footprint: authored footprint
  floors: floor count
  wallMaterial: selected material
  roofType: roof form
  roofOrientation: authored orientation
  entrancePosition: authored entry
  windowPattern: selected arrangement
  balcony: optional configuration
  chimney: optional configuration
  garden: lot and frontage treatment
  decorativeSet: selected details and props
```

Avoid object-ID-specific generation logic where a reusable parameterized rule
is practical. Component reuse must preserve authored silhouette, lot, frontage,
material and district variation; a collection of cloned complete houses does
not satisfy this requirement.

### ASTRAEON city-authoring template

Before starting the second major town, deliver a city-authoring template for:

concept / world-building → district plan → Blender blockout → select
architecture/material/vegetation kits → author unique landmarks → place
NPC/services/portals → export → playable runtime → visual QA.

The template must document the editable source structure, kit/preset selection,
city data boundaries, source IDs/transforms, export commands and visual QA gates.
A new town must not require rebuilding the renderer, actor integration,
navigation system, exporter, collision pipeline, NPC interaction framework,
portal framework or material loading system.

### Dedicated productionization execution pass

1. Identify proven generic systems and stable components in the accepted
   Wayfarer revision; keep unresolved or city-specific work local.
2. Extract engine/world responsibilities while preserving gameplay behavior,
   shared depth, authoring fidelity, navigation and metadata alignment.
3. Package component-level environment kits and parameterized building presets,
   including materials, vegetation and props with distinct family variants.
4. Keep Wayfarer's accepted layout, unique landmarks, palette, NPCs, lore and
   quests in city-specific source/content definitions.
5. Produce the city-authoring template and documented concept-to-playable
   workflow, including visual and performance QA.
6. Recheck the accepted Wayfarer after extraction. Rehearse the template with a
   minimal authoring fixture to demonstrate a new world can export and run
   through the existing systems without duplicating Wayfarer implementation
   files. This validates the template; it does not start full City 2 production.
7. Record evidence for the exit gate before releasing the City 2 production
   freeze. Do not substitute framework documents alone for usable tools/kits.

### Scalability definition of done and City 2 gate

The Golden Foundation is fully complete only when all of the following hold:

- Wayfarer itself passes Golden visual, gameplay, animation and performance
  acceptance.
- Its proven production workflow is extracted into usable reusable tools/kits,
  with generic systems, environment kits and city-specific content separated.
- The city template and component-level building presets are delivered and
  demonstrated through export, playable runtime and visual QA.
- Starting a second town requires neither duplication nor rewriting of
  Wayfarer-specific implementation files or the shared systems listed above.
- The accepted Wayfarer retains its visual quality, gameplay, animation,
  performance and authoring/metadata fidelity after extraction.

**Do not start full production of City 2 before this productionization pass is
complete.** Passing Wayfarer alone completes the playable Golden slice; it does
not by itself complete the Golden Foundation.

## Research responsibilities

[Architecture](ARCHITECTURE.md), [reference study](RAGNAROK_REFERENCE.md) and
[research catalog](RESEARCH-SOURCES.md) retain their source caveats. NostalRO and
roBrowser inform browser responsibilities; Ragnarok Research Lab informs native
terrain/navigation/world/animation separation; BrowEdit informs level-authoring
workflow; rAthena informs NPC and portal responsibilities. Integrating the catalog
does not claim a fresh external source audit or adoption of RO file formats.
