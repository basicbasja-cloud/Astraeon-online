# Wayfarer Court — visual consolidation candidate

Content expansion is paused. **Golden Town Scene approval: pending. Golden Sprite Character approval: pending.** Ragnarok Online 1 guides current presentation and town planning; painted sprites are the mainline character direction. Do not add maps, classes, skill sets, NPC families, buildings or districts until both gates pass in the deployed game.

## Town concept

A Shenzhou frontier town whose Consortium court gathers adventurers and trade onto the eastern road to Goldenfield. The Consortium Hall is the primary civic landmark. Its entrance opens onto Wayfarer Court; the fountain is the smaller meeting point. Warrior is the first Golden Sprite Character. The other two existing archetypes remain available without expanding their asset scope.

## Composition

The benchmark is the central fountain court, its Consortium entrance, one shop frontage, one market counter, two seating edges and a west courtyard tree cluster. The broad Consortium facade and open entrance establish the primary landmark; the fountain is the smaller court focal point. The adventurer sits in the open foreground. The market supports the right edge rather than filling the centre. Trees frame edges and entrances rather than filling every gap.

Removed two excess central planters, the duplicate centre-market canopy and the loose guild cart. Benches now occupy the court's edges. Crates, merchant, counter and cart form one market service cluster. The Registrar and Quest Board share the hall forecourt. The Artisan works beside the existing workshop, the Housing Keeper at the residential approach and the Gatekeeper beside the Caravan Gate. Two existing guards now patrol the gate checkpoint; one customer circulates at the market. There are three ambient routes; the court centre remains quieter.

The existing shrine moves into the western garden/courtyard connected by the service path. Existing surrounding trees supply its Spirit/Qi context. This relocates existing content; it does not generate a new district or asset family. The shrine remains part of Shenzhou's culture and stops competing with the central fountain.

## Architecture and material language

Shenzhou's dominant family is pale warm plaster, exposed ochre timber, weathered limestone bases, layered upturned eaves, jade slate civic roofs, muted clay domestic roofs, brass/gold trim and warm lanterns. Teal-and-ivory shop cloth echoes Consortium banners. Jade magic is a small accent. The civic roof colour distinguishes function rather than introducing a separate asset style. Imported technology stays an accent; it does not define this block.

The retained nearby assets come from the same original town atlas. Their upper-left highlights and warm/cool shadow grouping supply the common light direction. Ground and contact shadows use this same convention. An attractive asset with a conflicting projection or light direction still needs re-authoring; colour grading cannot correct its structure.

The limestone paint replaces flat screen-aligned checker paving. A shared affine material transform maps its staggered courses into X/Z world coordinates. Avenue, connecting street and court share this stone family; narrow service routes use worn warm soil. Dust aprons, edge grit, small grass intrusions, joints, subtle traffic wear and contact gradients integrate the surfaces. The repeating material is quiet enough to leave character and fountain readable. Terrain remains continuous beyond the viewport, not a diamond board.

## Circulation and scale

Use one visible painted humanoid as the relative 1.0 baseline. Calibrate player and NPC artwork by visible feet-to-head size, not atlas cell width: 70 pixels for the Golden Warrior before responsive zoom, registered to visible boot contacts across idle and locomotion sheets. The atlas presentation scalar 76 is **not** a promise of a 76-pixel visible height.

| Relationship | Current candidate |
|---|---|
| Main avenue | 3.8 ground units, limestone; Consortium forecourt → court → market frontage → eastern Caravan Gate |
| Secondary street | 2.6 units, shared stone; north/south court mouths and the western approach |
| Gate-to-field continuation | Main eastern stone street ends at the Caravan Gate; 1.9-unit dirt route continues beyond it |
| Service path | 1.1 units, warm worn soil; serves the market/back courtyard |
| Plaza | Authored six-sided court about 9.6 × 8.2 units; perimeter circulation around the basin |
| Fountain | 2.2 × 1.3-unit collision core, with 0.2 navigation clearance; visual basin extends slightly beyond |
| Humanoid scale | One visible-height baseline for player/major NPCs; independent readable UI |
| Camera | Shared forward/inverse affine projection; responsive zoom and foot anchors are preserved |

The fountain now blocks movement. Players and pathfinding must route around its basin instead of standing inside the artwork. Building entrances and market interactions remain accessible through actual input. Roof fade keeps the player readable when passing behind architecture. Broad contact gradients replace hard elliptical stamps under town props.

The hall artwork has been refined with a taller open double doorway, shallow steps and a clearer ground-floor facade, preserving the existing jade-roof/timber/plaster vocabulary. It is registered to the front steps and connected to an authored limestone forecourt. The door opening is roughly 1.3 Warrior heights in the candidate; visual clearance and perspective still require public review. This is a replacement for the existing hall, not a new building. Responsive camera zoom, city bounds and the main hall size retain their contracts; v28 aligns the projection and revises existing route/footprint placement together.

## Golden Sprite Character integration and review

Warrior, Mage and Ranger use the existing richly painted directional atlases. Eight authored front/side/rear/diagonal views preserve hair, cape, costume and weapon identity without image mirroring. Continuous movement/aim controls facing; presentation chooses the nearest authored angle. Distance-based gait and actual impact timing support manual combat. The Golden Warrior now has separate painted hit and fallen poses in four reviewed cardinal views; diagonals select the nearest view without mirroring. Idle, movement, attacks and dodge retain eight views, including the existing two-pose rear walking fallback. Boot-contact registration and per-direction body calibration prevent sheet changes from altering apparent stature. Reusable slash ribbons, a bright contact edge and ground-projected dodge dust modernize feedback; existing cast effects, telegraphs and single-layer Node behaviors retain their scope. The live game includes no low-poly character path.

Scope is 3–4 hero sets; preserve and refine the three existing sets before considering another. The attachment could not be opened, so the repository's original painted art is the working benchmark. Richer transitions, consistent rear cycles and illustrated charm at gameplay distance remain art review criteria.

For each deployed comparison, use a fresh cache and capture the court, Consortium approach, market frontage, city gate, field transition and four viewport sizes. Move, turn, attack and dodge the actual sprite hero. Compare visible scales, material detail frequency, focal hierarchy, light/shadow direction, entrances and ground edges with the previous pass. Inspect each class inside the actual town, not only in an atlas gallery. Both gates require user visual approval and public in-game inspection. Local screenshots and functional passes are supporting evidence only.

### Previous v26 public evidence

Public access was restored during the previous pass. The deployed game was opened in fresh Chromium and inspected at desktop, tablet and both phone orientations; normal input verified fountain blocking, guild/market access, walking through the gate into the field, targeting, attack, skill and dodge. The deployed v26 scripts/cache were verified with no runtime/resource errors. A fresh Ranger also completed the whole live expedition through camp, dungeon and guardian, returned, crafted and reloaded successfully. A fresh Mage town inspection found no console/runtime/resource errors. This completes functional/public inspection for this candidate, not either art approval. Doorway clearance and architecture perspective remain open alongside final visual review.

## Recovery candidate — v27

The recovery began from clean commit `abd713e`, confirmed against remote `main`. The first incomplete milestone was the in-scene Golden Character/Golden Town review, not additional content. Replaced only the existing hall artwork and added eight Warrior reaction frames; the rejected 24-frame reaction candidate is excluded. No class, region, district, building, quest, NPC family or decorative pack was added.

Town grass now uses a quieter world-aligned version of the existing material. Soil aprons, softened paving edges, shallow side drainage, traffic wear and soil at tree roots integrate the street surfaces. Service NPCs were relocated to existing facilities; physical access and the connected expedition are regression targets.

Public Pages browsing currently fails with proxy HTTP 403 / `ERR_TUNNEL_CONNECTION_FAILED`; GitHub repository and Actions access remain available through the connector. Previous v26 public evidence does not approve v27. Local screenshots, successful deployment and functional tests are supporting evidence only. Both art gates remain pending until the deployed candidate is inspected and approved.

## Research application — 2026-09-30

[RAGNAROK_REFERENCE.md](./RAGNAROK_REFERENCE.md) records inspected RO terrain/world/navigation/sprite mechanisms, community editor workflows and Prontera/Geffen/Payon/Alberta service relationships. It converts those findings into original ASTRAEON placement, terrain and Warrior production techniques. The [current ground plan](./docs/reference/wayfarer-plan.svg) shows source-authored circulation, collision, art anchors and service positions.

The v27 research identified this repair order: confirm primary hall dominance against the reused northern civic facade; repair southeast ground/collision disagreements and register footprints/entrances against painted perspective; separate forecourt player/service/label space; repair Warrior rear/defective gait views; review court traffic and gate security use; then refine terrain repetition, contact and occlusion. At that revision the service path's `(31,26)` point and stone connector's `(30,29)` point lay inside the residence collision rectangle; normal route planning can avoid the obstacle while the painted road still fails spatial logic. Use existing content and replace only failed art. A top-down plan does not approve the scene's perspective or the character's motion.

Classic RO's 3D environment can rotate model instances; our single-view painted facades cannot. Preserve the fixed camera and choose compatible frontages before re-authoring an existing facade. Our current sprite lighting does not sample a spatial ground lightmap. These constraints remain explicit rather than being hidden under a claim of RO-equivalent rendering.

This pass adds source-based standards and a diagnostic diagram. It does not change runtime presentation or mark either Golden gate approved. Public official-reference browsing also returned HTTP 403; the research does not claim a fresh official screenshot survey.

## Applied reference candidate — v28 / 2026-10-01

Implemented the research in the playable client. Shared ground axes now match the painted front/side foundation planes; all terrain, street widths, inverse input, depth, sprite direction and effects follow the same projection. The existing northern civic copy now uses a smaller shop facade. Hall, market, workshop and residence entrances share source-authored limestone landings. Court value grouping, projected border/meeting rings and clipped wear unify the public paving; contact shadows follow occupied volumes. Existing trees were moved away from steps/streets rather than adding vegetation.

Revised the residence art/footprint/service together, routed its southern streets around occupancy, and moved the shrine path to the front approach. Every authored town road passes a full-width plus 0.2-unit human-clearance regression against every block. Registrar/Quest Board standing space and nearby-service labels are separated. Existing guards moved to the gate, and static service NPCs turn toward nearby players.

Warrior has even timing across seven accepted extended stride keys, screen-space direction selection and bounded foot-pivot motion. Attack/cast anticipation, contact and recovery use the actual timeline; movement, dodge and hit add restrained weight feedback. Damage and skill scope remain unchanged. Three generated rear-walk replacements failed review and were excluded; north/northwest still use the accepted shorter cycle. Four-cardinal reactions remain a compromise.

No class, map, district, building, quest or decorative asset family was added. Both Golden approvals remain pending. Local browser comparisons cover desktop, tablet, landscape and portrait, with normal-input service/court/gate/combat review. Public Pages inspection must still succeed before acceptance; a successful deployment is not visual approval.
