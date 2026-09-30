# Wayfarer Court — visual consolidation candidate

Content expansion is paused. **Golden Town Scene approval: pending. Golden Sprite Character approval: pending.** Ragnarok Online 1 guides current presentation and town planning; painted sprites are the mainline character direction. Do not add maps, classes, skill sets, NPC families, buildings or districts until both gates pass in the deployed game.

## Composition

The benchmark is the central fountain court, its Consortium entrance, one shop frontage, one market counter, two seating edges and a west courtyard tree cluster. The fountain is the primary focal point; the Consortium threshold is secondary. The adventurer sits in the open foreground. The market supports the right edge rather than filling the centre. Trees frame edges and entrances rather than filling every gap.

Removed two excess central planters, the duplicate centre-market canopy and the loose guild cart. Benches now occupy the court's edges. Crates, merchant, counter and cart form one market service cluster. Housing staff move to their approach rather than standing in the court. Two guards follow its perimeter; one customer circulates at the market. There are three ambient routes, not five overlapping central circuits.

The existing shrine moves into the western garden/courtyard connected by the service path. Existing surrounding trees supply its Spirit/Qi context. This relocates existing content; it does not generate a new district or asset family. The shrine remains part of Shenzhou's culture and stops competing with the central fountain.

## Architecture and material language

Shenzhou's dominant family is pale warm plaster, exposed ochre timber, weathered limestone bases, layered upturned eaves, jade slate civic roofs, muted clay domestic roofs, brass/gold trim and warm lanterns. Teal-and-ivory shop cloth echoes Consortium banners. Jade magic is a small accent. The civic roof colour distinguishes function rather than introducing a separate asset style. Imported technology stays an accent; it does not define this block.

The retained nearby assets come from the same original town atlas. Their upper-left highlights and warm/cool shadow grouping supply the common light direction. Ground and contact shadows use this same convention. An attractive asset with a conflicting projection or light direction still needs re-authoring; colour grading cannot correct its structure.

The limestone paint replaces flat screen-aligned checker paving. A shared affine material transform maps its staggered courses into X/Z world coordinates. Avenue, connecting street and court share this stone family; narrow service routes use worn warm soil. Dust aprons, edge grit, small grass intrusions, joints, subtle traffic wear and contact gradients integrate the surfaces. The repeating material is quiet enough to leave character and fountain readable. Terrain remains continuous beyond the viewport, not a diamond board.

## Circulation and scale

Use one visible painted humanoid as the relative 1.0 baseline. Calibrate player and NPC artwork by visible feet-to-head size, not atlas cell width: approximately 70 pixels before responsive zoom. The atlas presentation scalar 76 is **not** a promise of a 76-pixel visible height.

| Relationship | Current candidate |
|---|---|
| Main avenue | 3.8 ground units, limestone; terminates at the court's north/south mouths |
| Secondary street | 2.6 units, shared stone; joins the open court east/west |
| Gate-to-field continuation | Main eastern stone street ends at the Caravan Gate; 1.9-unit dirt route continues beyond it |
| Service path | 1.1 units, warm worn soil; serves the market/back courtyard |
| Plaza | Authored six-sided court about 9.6 × 8.2 units; perimeter circulation around the basin |
| Fountain | 2.2 × 1.3-unit collision core, with 0.2 navigation clearance; visual basin extends slightly beyond |
| Humanoid scale | One visible-height baseline for player/major NPCs; independent readable UI |
| Camera | Shared forward/inverse affine projection; responsive zoom and foot anchors are preserved |

The fountain now blocks movement. Players and pathfinding must route around its basin instead of standing inside the artwork. Building entrances and market interactions remain accessible through actual input. Roof fade keeps the player readable when passing behind architecture. Broad contact gradients replace hard elliptical stamps under town props.

This scale system is provisional. Door openings, first-floor proportions and painted perspective still need close visual acceptance; the current original guild entrance is near the humanoid's visible height and needs more architectural clearance before this can be called final. Do not solve that by scaling every asset or shrinking the whole world. Preserve the open court, main/secondary/service distinction and benchmark ratios while re-authoring any deficient opening.

## Golden Sprite Character integration and review

Warrior, Mage and Ranger use the existing richly painted directional atlases. Eight authored front/side/rear/diagonal views preserve hair, cape, costume and weapon identity without image mirroring. Continuous movement/aim controls facing; presentation chooses the nearest authored angle. Distance-based gait and actual impact timing support manual combat. Existing hit/cast effects, trails, telegraphs and authored Node behaviors provide variation without additional hero sheets. The live game includes no low-poly character path.

Scope is 3–4 hero sets; preserve and refine the three existing sets before considering another. The attachment could not be opened, so the repository's original painted art is the working benchmark. Richer transitions, consistent rear cycles and illustrated charm at gameplay distance remain art review criteria.

For each deployed comparison, use a fresh cache and capture the court, Consortium approach, market frontage, city gate, field transition and four viewport sizes. Move, turn, attack and dodge the actual sprite hero. Compare visible scales, material detail frequency, focal hierarchy, light/shadow direction, entrances and ground edges with the previous pass. Inspect each class inside the actual town, not only in an atlas gallery. Both gates require user visual approval and public in-game inspection. Local screenshots and functional passes are supporting evidence only.

Public access was restored during this pass. The deployed game was opened in fresh Chromium and inspected at desktop, tablet and both phone orientations; normal input verified fountain blocking, guild/market access, walking through the gate into the field, targeting, attack, skill and dodge. The deployed v26 scripts/cache were verified with no runtime/resource errors. A fresh Ranger also completed the whole live expedition through camp, dungeon and guardian, returned, crafted and reloaded successfully. A fresh Mage town inspection found no console/runtime/resource errors. This completes functional/public inspection for this candidate, not either art approval. Doorway clearance and architecture perspective remain open alongside final visual review.
