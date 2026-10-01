# Ragnarok Online reference study → ASTRAEON production

The 2026-10-01 [master plan](MASTER_PLAN.md) integrates this study with the supplied
[research catalog](RESEARCH-SOURCES.md) and Blender/native-JSON pipeline. It retains
Canvas2D, current painted art and the Golden content freeze. Claims below retain
their pinned-source and v27/v28 baseline scope; catalog recommendations do not
constitute a fresh inspection of NostalRO or the newer roBrowser repository.

Research date: 2026-09-30. ASTRAEON baseline: `19311a08f7e26d9b08165384bf1a5f92a78ed4ce` (v27). Scope: **one painted Warrior inside Wayfarer Court**. Both Golden approvals remain pending; content expansion remains frozen.

## What the evidence establishes

Ragnarok Online's useful principle is the coordination of **directional sprite actors, a textured three-dimensional environment, a common camera, navigable ground and authored places**. A flat backdrop with independently attractive cutouts reproduces only part of that system.

The inspected community client loads terrain surfaces, model placements, walkability, lights and sprite animation as separate but connected data. Sprite direction incorporates camera direction; sprite brightness samples the ground shadow map; sprite parts use animation offsets and attachment positions. These mechanisms explain how different asset types can belong to one space. [S1–S7]

ASTRAEON keeps its richly painted sprites and Canvas2D world. It should reproduce the spatial relationships through world-aligned materials, registered feet, explicit ground footprints, consistent perspective, depth ordering, contact shadows and readable routes. This does not require changing the live hero to 3D or migrating engines before the Golden Scene passes.

**Evidence boundary:** roBrowser is a community client implementation; BrowEdit and ActEditor are community tools; rAthena is a community server implementation with converted guide dialogue. They provide inspectable technical evidence, not Gravity's internal art direction or original studio workflow. The archived roBrowser is useful for classic-format behavior, not a recommendation to adopt its dependencies. The city guide examples describe their particular script versions, not every historical or regional client. In particular, a `pre-re` path does not prove the earliest Payon layout.

Public iRO Wiki access returned proxy HTTP 403 in this environment. No fresh official town screenshot survey, developer interview or original-client playthrough is claimed. The four city studies below derive from inspected dialogue, destination coordinates and warp data. Render and art recommendations are identified as ASTRAEON decisions. No Ragnarok graphics, map files, sprite sheets or third-party source code are imported into the game.

## 1. Map placement: relationships before objects

### Four city case studies

| Reference | Source-confirmed spatial facts | Technique to carry into ASTRAEON |
|---|---|---|
| Prontera | The guide describes weapon/tool shops northeast/northwest of a central fountain, inns east/west, trading post southeast, pub behind it, libraries reached from an open area north of the fountain, and castle in the northern sector. Gate guides and field/interior warps occupy separate destinations. [S8] | Use a memorable public space to explain services. Give a civic destination a route beyond the meeting point. Keep a plaza, an entrance forecourt and a through-route distinct even when their paving connects. |
| Geffen | The guide places its tower in the centre, the Wizard Guild at the top and a dungeon underneath. Pub, inn, shops and academy are described relative to the tower or city centre. Warps confirm a tower entrance and separate north/east/west field exits. [S9] | Make the main landmark useful in gameplay. A landmark should explain the town's identity and organize navigation. This evidence supports landmark-centred navigation; it does not establish every street as a perfect radial plan. |
| Payon | The guide calls Payon a mountain city, locates the palace north and the Archer Village northeast, and places the Archer Guild and a dungeon entrance within that separate village. [S10] | Create a sequence of places and thresholds. Preserve a dominant regional architectural family. For the current slice, use the existing gate → road → field sequence; do not add another village or district. The script alone cannot establish terrain slopes or street curvature. |
| Alberta | The guide calls it a port city. Merchant Guild and forge share a building in the southwest, while other shops and an inn occupy distinct locations. [S11] | Cluster functions with a reason to be together. Crafting belongs beside a workshop; commerce belongs at an active frontage. Port identity is documented; detailed dock composition requires separate visual evidence. |

These examples also show why “one clear landmark” does not mean “only one useful place.” A meeting fountain, a civic building, shops and remote services can coexist if their roles and routes are legible. ASTRAEON's hierarchy is its own design decision: Consortium Hall first, fountain second, market third.

### ASTRAEON layout method

1. Write the place's purpose in one sentence: **A Shenzhou frontier town whose Consortium court gathers adventurers and trade onto the eastern road to Goldenfield.**
2. Draw the movement graph: hall threshold → court perimeter → market frontage → Caravan Gate → transition road → Goldenfield. Draw Registrar/Quest Board, Merchant and Artisan as destinations attached to that graph.
3. Reserve traversable ground, fountain clearance, door approaches and camera sight lines before positioning facades. An avenue is a connected public route, not a texture stripe drawn through obstacles.
4. Place existing buildings to define the edges of those spaces. Record where each entrance faces, where its ground footprint sits and which side of the street its facade supports. A roof cannot define a usable street edge by itself.
5. Connect secondary streets and service paths. They must lead to a destination or believable access point. Avoid paths that terminate against an inaccessible wall or merely weave around decorative cutouts.
6. Attach services to entrances/counters with a visible standing and interaction area. Keep queues and walkers out of the through-route. Test approach, interaction and departure with normal controls.
7. Group vegetation and props by use. Court planters frame space; courtyard trees have soil and roots; market crates stay near goods; gate supplies stay near the checkpoint. Keep the centre and exit mouth quieter.
8. Walk the route at normal camera zoom before adding detail. Check the arrival view, court crossing, hall approach, market and gate threshold. Readability must survive portrait cropping.

**Existing street contract:** 3.8-unit main avenue, 2.6-unit principal secondary streets, 1.1-unit dirt service paths and 1.9-unit field continuation. The southern connector is a narrower 1.9-unit stone street; do not claim all streets have identical dimensions. The six-sided court is roughly 9.6 × 8.2 units. These are ASTRAEON working dimensions, not measurements copied from Ragnarok.

**Negative space contract:** protect the hall-to-court approach, fountain circulation, market customer space and gate mouth. Judge available movement and foreground readability in gameplay rather than trying to reach a universal percentage of empty terrain. Extra props do not repair a weak block plan.

### Placement record for each existing building

Record this in the production brief before altering its runtime placement:

| Field | Meaning |
|---|---|
| Role and frontage | The service/public space it supports and the direction its entrance faces |
| Ground footprint | Occupied world-space polygon or rectangle, distinct from the sprite's canvas dimensions |
| Entrance and approach | Door/step position, clear walking area and reachable service position |
| Art registration | Source rectangle, source-space ground anchor and intended screen body dimensions |
| Occlusion | What can pass behind it, where the roof should fade and whether a single draw layer is sufficient |
| Material/light family | Jade/clay roof, warm plaster, dark timber, limestone, upper-left light |
| Review views | Arrival, approach, passing behind, departure; desktop and both phone orientations |

The current `townBlocks` and `townObjects` are separate lists, not a complete entrance-aware building record. Treat every placement edit as a paired art/collision/interaction change. Do not infer collision from transparent sprite bounds.

## 2. Map building: coordinate the layers

### What the RO formats reveal

| Layer | Inspected behavior | ASTRAEON equivalent |
|---|---|---|
| GND terrain | Ground surfaces have four heights, top/front/right surface references; tiles reference texture UVs, lightmap and colour. The loader constructs geometry and normals. [S1] | Connected ground polygons and world-aligned material courses; separate terrain shape from paint detail |
| RSW world | References GND/GAT and records positioned, rotated, scaled models plus lights, sounds and effects. [S2] | `world-content.js` placements, scene lighting conventions, ambient/VFX placement |
| RSM models | The model loader and renderer handle mesh data and placed model instances. [S3] | Painted building volumes with consistent projected bases; several authored orientations if needed later |
| GAT navigation | Cells contain four heights and a type mapped to walkable/water/other flags. [S4] | `townBlocks`, fountain clearance, `navigation.js`, world-space collision and usable approaches |
| Lighting | Ground rendering combines texture, tile colour and lighting; sprite brightness samples ground shadow values. BrowEdit documents lightmap authoring. [S5] | One upper-left sun, restrained baked asset shadows, common soft ground contact and matching ambient tone |

The lesson is to **separate responsibilities while sharing coordinates**. Visual terrain and walkability can have different representations, but their boundaries must agree. A stone road does not automatically become walkable; a sprite doorway does not automatically become an entrance.

BrowEdit supports object move/rotate/scale, grid snapping and setting an object to floor height. Its documented lightmapper calculates illumination using occlusion from models. The documentation explicitly says that calculation differs from the original lightmap calculation; its 8 × 8 tile lightmaps with shared borders describe that tool's workflow. Do not present BrowEdit's raytracer as proof of Gravity's original bake process. [S5, S6]

### Build order for the existing Golden Scene

**A. Spatial blockout.** Work with simple ground outlines and footprint masses first. Confirm the plaza perimeter, hall steps/forecourt, market approach, main avenue and gate. A top-down plan answers connectivity; a gameplay view answers facade, scale and focal hierarchy. Both are required.

**B. Projection.** Use `world-view.js` for all ground positions, inverse input and VFX. Its v28 basis is `(48, 14)` for world X and `(-32, 22)` for world Y; it is an affine high-angle view, not a literal copy of RO's rotatable 3D camera. Place a temporary projected rectangle beside each facade to check its base and perspective. Do not rotate a flat building sprite in the screen plane to pretend it has a different frontage: the roof, door and shadows will rotate with it incorrectly.

**C. Architecture.** Preserve the dominant Shenzhou vocabulary: pale warm plaster, ochre/dark timber, weathered limestone bases, layered upturned eaves, jade civic roofs, muted clay domestic roofs, teal/ivory cloth and restrained brass/gold. Align doors, step landings and exposed bases to the street they serve. Reusing a facade is acceptable only where its authored orientation fits the placement. If a block needs a genuinely different-facing facade, re-author that existing building after the Golden composition is established; this is replacement work, not a decorative pack.

**D. Ground.** Build one connected material domain for avenue, plaza and forecourt. Use the same stone family with subtle changes in wear, coursing or border treatment to distinguish function. Service routes and the field transition use worn soil. Treat material boundaries as spatial edges: drainage at road sides, dust near thresholds, wheel wear on the gate route, garden soil beneath vegetation. Change several nearby edges together rather than placing a large blurred stain over a whole block.

**E. Light and grounding.** Keep highlights upper left, cast shadows toward the opposite side and contact darkening at actual bases. Contact shadows should be tighter than cast shadows. Avoid double shadowing where art already contains a painted cast shadow. A uniform tint cannot repair conflicting light direction, horizon or perspective. Source-confirmed RO sprite shadow sampling suggests a useful later refinement—subtle shared ambient shade under architecture—but the current Canvas renderer does not implement that spatial light sampling. Do not claim it does.

**F. Occlusion.** Sort world objects and actors by projected ground depth, never by image top edge. The v28 sort uses `14*x + 22*y`. A whole building sprite can still produce wrong overlaps when a footprint spans a street or multiple depth layers. Use the existing roof fade during review; if a specific overlap fails, split that existing asset into base/front/roof layers or revise placement. Fading alone is a readability aid, not correct three-dimensional occlusion.

**G. Surface cohesion.** Compare character, important NPC, hall, market and ground together at normal zoom. Ground should carry less contrast/detail than the actor; landmark accents should be concentrated at the facade and threshold. Review value grouping, saturation, edge softness, texture frequency and light direction. Adding blur everywhere would erase readable doors, weapons and faces.

**H. Threshold.** Preserve a road that physically continues through the Caravan Gate, guards/checkpoint use, worn paving becoming soil, a less maintained verge and the Goldenfield arrival road. The next map should inherit the route's direction and material story. A glowing exit marker supplements the architecture; it cannot carry the entire sense of transition.

### Why the current facade approach has a limit

RO's placed model instances can rotate in three dimensions. ASTRAEON's painted facade cannot acquire a new viewpoint by changing an `x/y` coordinate or by mirroring. Current buildings reuse a small set of authored orientations. This constrains street walls, corners and courtyards even when each painting is attractive. Keep the camera fixed and solve the Golden composition using compatible existing orientations first. Do not promise a freely rotatable town or justify a new asset library before the current scene passes.

## 3. Character building: pose, direction, timing and registration

### What the sprite system actually does

The SPR loader stores indexed/palette frames and RGBA frames. ACT stores actions, animation frames, layer image indices, offsets, mirror flags, scale, colour, rotation, timing, sound references and additional positions. The entity renderer selects an action using the action group and an eight-direction index, then draws body/head/equipment layers with direction-dependent ordering and attachment offsets. ActEditor independently exposes eight direction buttons per action group and visible anchor controls. [S7, S12]

This supports the practical lesson that **animation data is more than a grid of pictures**. Direction, pose timing, frame registration, part alignment and order matter as much as source resolution. It does not prove every RO sprite has eight independently painted unique views: ACT and the inspected renderer explicitly support mirroring. ASTRAEON's asymmetric sword, costume and light direction make eight authored views the preferred live standard, without mirroring.

Do not describe classic RO's pixel-oriented sprites as today's high-resolution generated paintings. ASTRAEON deliberately adopts a softer painted aesthetic while retaining directional readability and disciplined animation data. No evidence in these sources establishes that Gravity generated its characters from 3D turntables or used a particular modern painting tool.

### Golden Warrior production workflow

1. **Canonical identity.** Freeze one face, hair silhouette, head/body proportion, navy/cream costume layers, gold trim, cape fastening, boots, sword design and handedness. Record front/side/back construction before animating. Avoid changing costume details independently in every generated row.
2. **Directional turn sheet.** Establish front, back, both sides and all four diagonals under the exact game camera convention. Register the authored row order to `directionRow`; do not infer screen-facing from a compass label alone under the affine projection. Review visible back/shoulder/face information, weapon hand and cloth layering in a rotating gameplay gallery. “Beautiful but facing the wrong way” fails.
3. **Gameplay silhouette.** Judge the rendered character at the current approximately 70-pixel visible body height before responsive zoom, not by a large portrait. Separate head/hair, torso/cape and sword masses. Keep a small readable facial grouping; excessive armor microdetail can become noise at this size.
4. **Pose keys before frames.** Approve idle, locomotion contacts/passing poses, attack anticipation/contact/recovery, shared cast, dodge, hit and fallen death. Establish weight transfer and weapon path. More frames cannot correct an inconsistent pose family.
5. **Motion continuity.** Animate stride by travelled distance; running can change cadence/cloth/lean without a second costume sheet. Keep the planted boot coherent with movement. Backward movement must preserve facing and reverse appropriate gait timing. The current north/northwest shorter fallback and skipped corrupted Warrior stride are unresolved art debt, not finished eight-frame coverage.
6. **Frame registration.** Record each source rectangle, source boot contact and standing body reference. Preserve weapon/cape reach outside the body reference. Reactions must inherit standing scale: never scale a fallen character back up to a standing-height box. ACT attachment positions are evidence for the need for registration; ASTRAEON boot contacts are its own implementation.
7. **Timed gameplay.** Bind anticipation/contact/recovery to the actual combat timeline. Keep sword arcs, hit sparks and damage contact aligned. Cast variations may share a motion, but their effects and mechanics must differ. The v28 attack/cast presentation returns from anticipation/contact to idle during recovery, with bounded foot-pivot weight changes. These are presentation refinements, not newly authored limb frames.
8. **VFX and sound.** Reuse slash ribbons, dodge dust, cast rings and elemental overlays. Effects need a grounded origin, deliberate duration and clear silhouette. Do not paint persistent glow into every body frame or hide weak anatomy behind a full-screen burst. ASTRAEON's hit stop, dodge feedback and manual aim are modern adaptations, not claims about the classic game's controls.
9. **In-scene review.** Stand/walk/attack/cast/dodge/hit/fall beside Registrar, hall door, fountain, stall and an open patch of road. Review eight facing headings and all device framings. Compare actor/NPC stature by visible anatomy; an atlas width or bounding box including a staff is not a human-height measurement.

### Minimum sheet budget

| Motion | Current strategy / focused target | Reuse rule |
|---|---|---|
| Idle | Eight readable directions; restrained breathing | One canonical outfit |
| Walk/run | Eight-direction logic; repair the two rear fallbacks before broadening frame counts | Distance-driven gait; reuse canonical body |
| Basic attack | Readable anticipation, contact and recovery | Trail aligned to existing attack geometry |
| Existing Base Skills | Shared compatible motion families for the Golden review | Nodes change effects and behavior, not costumes |
| Dodge | Readable body weight and travel with dust/streak | One motion family |
| Hit | Four authored cardinal views, nearest-cardinal diagonals in the current candidate | Expand only if in-scene facing mismatch is visible |
| Death | Four fallen views, standing scale retained, pose held before fade | Never reuse an upright hit pose as final death |

This is a bounded refinement brief, not a demand to regenerate every sheet. The first subject stays Warrior. Mage/Ranger refinement waits for the first Golden Character review. Existing Base Skills + one Node layer remain unchanged; no Advanced Class or equipment permutation production begins.

### Generation and paint-over brief

For an individual replacement view or motion, provide the canonical Warrior reference and exact target heading/pose. Specify the game camera, visible weight-bearing boot, same sword hand, same cape fastening, same costume layers, upper-left light, transparent background and enough margin for weapon/cloth reach. Request a bounded set of related poses, inspect it, then register/crop it. Do not ask one generation to solve all actions and directions at once.

Reject invented front-facing faces in rear views, switched hands, disconnected limbs, clipped weapons, neighbouring-cell fragments and changing costume proportions. Repair the rejected view using the accepted identity reference. Review at gameplay size before accepting any generated result. This is an ASTRAEON asset-production recommendation, not a historical RO method.

## 4. Applying the research to v27

The inspected local Consortium screenshot shows an improved open hall threshold and shared stone paving. It also shows why neither Golden gate should be marked complete: foreground planting overlaps the hall edge; close character/name placements compete at the forecourt; the ground uses a visibly repeated material; architecture remains made from independently authored cutouts. These are observations of the saved local candidate, not a fresh public build inspection.

| Priority | Current evidence | Focused next repair / acceptance |
|---|---|---|
| 1. Landmark hierarchy | `north-house` reuses guild artwork at 500 × 573, versus primary hall at 478 × 437; height alone does not establish dominance, but the reused civic silhouette is a competing candidate | Review arrival/court/portrait views together. Reduce prominence, occlude or re-author the existing secondary facade only where it competes. Keep one recognizable civic entrance. |
| 2. Ground/collision agreement and entrances | Separate collision blocks/art anchors; several buildings reuse the same facing. The southeast service path's `(31,26)` point and southern stone connector's `(30,29)` point fall inside the residence collision rectangle `(27,25,5.5,4.6)` | Repair these existing route/footprint conflicts as a paired layout change, leaving enough corridor width and human clearance around the residence. Then register door approaches and test painted bases against projection. Keep the hall → court → market route clear. |
| 3. Forecourt readability | Saved screenshot has overlapping actor names near Registrar/Warrior/Quest Board and planting close to steps | Separate standing/interaction spaces within the existing forecourt; review labels and player silhouette during approach. Do not add a larger forecourt UI overlay to solve spatial overlap. |
| 4. Warrior continuity | North/northwest use shorter accepted poses; one extended stride is intentionally skipped; four-view reactions remain a compromise | Replace only defective rear/stride views first. Confirm identity, boot contact and height through motion beside the hall and NPCs. |
| 5. Functional circulation | At the v27 baseline `walkers` defines two guard loops around the court, despite earlier prose describing gate patrols | Evaluate gate security use and plaza traffic in actual movement. If guards move, change routes with reachable ground and review crowding; a diagram is not a route test. |
| 6. Ground integration | Shared world-aligned limestone, soil aprons, drainage and wear already exist; soil/wear gradients remain approximate | Break obvious repetition with controlled wear at the existing threshold/frontages and quieter terrain values. Preserve material logic and frame-time budget. |
| 7. Shade and occlusion | Ground-depth sort, roof fade and contact gradients already exist; no per-position sprite light sampling | First fix visible overlap and double shadowing. Consider subtle environment shade only after the basic art/space contract holds; do not introduce an engine migration for this pass. |

These findings are now incorporated in STYLE_GUIDE.md, CONTENT_GUIDE.md and GOLDEN_SCENE.md. The accompanying [current layout diagram](docs/reference/wayfarer-plan.svg) is an original diagnostic generated from ASTRAEON's actual authored road, plaza, collision, anchor and service data. It is not Ragnarok artwork, a proposed expansion or a finished town illustration. Regenerate it with `node tools/reference-plan.cjs` after a layout change.

The diagram exposes ground/collision disagreements that functional navigation can route around. Passing an interaction test therefore does not prove the painted road itself is correctly placed. Check the complete corridor width against footprints, not just its centreline. Fixing these conflicts is existing-town consolidation, not permission to add streets or buildings.

## 5. Review procedure

Use the same fresh Warrior, normal responsive camera and repeatable route on each candidate. Capture arrival, hall approach, court perimeter, market, gate and field threshold at desktop 1280 × 800, tablet 768 × 1024, portrait 390 × 844 and landscape 844 × 390. Include a clip or sequence for walking, attack, cast and dodge; a still screenshot cannot establish animation quality.

At each view, verify hierarchy, visible human/door relationships, connected traversable space, logical service approaches, shared projected ground, controlled texture detail, light direction, character identity, weapon readability and unobscured gameplay. Inspect the player passing both in front of and behind architecture. A top-down plan can establish connectivity but cannot approve perspective or painted charm.

For runtime visual changes: build/run the static game, run the relevant existing interaction/motion checks, deploy, verify the matching Pages run and inspect the actual public game at https://basicbasja-cloud.github.io/Astraeon-online/ . Local screenshots support iteration; automatic test passes do not approve art. Public access remains subject to the environment proxy; failed browsing must be recorded, never substituted with an unqualified approval claim.

This research pass changes documentation and creates a diagnostic diagram, not runtime art or gameplay. It closes the reference-study task; it does not close either Golden gate.

## Inspected source register

Links are pinned to inspected revisions so claims remain reproducible. Retrieved 2026-09-30. Source comments and unknown fields are not treated as authoritative explanations.

| ID | Source / inspected location | What it supports |
|---|---|---|
| S1 | [roBrowser GND loader](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Loaders/Ground.js), `parseTiles`, `parseSurfaces`, `compile` | Terrain heights, surface references, UVs, lightmap/colour references and generated geometry |
| S2 | [roBrowser world loader](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Loaders/World.js), `load`; [BrowEdit RSW documentation](https://github.com/Borf/BrowEdit3/blob/ad89aef809ca52ad32c3a06c162dc508ace7d7f4/docs/formats/Rsw.md) | World references, model transforms, lights/sounds/effects; version-specific formats |
| S3 | [roBrowser model loader](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Loaders/Model.js) and [map model renderer](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Map/Models.js) | Models/meshes and positioned 3D environment instances |
| S4 | [roBrowser GAT loader](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Loaders/Altitude.js), `TYPE_TABLE`, `load` | Ground heights and navigation type mapping; some type semantics explicitly uncertain |
| S5 | [roBrowser ground renderer](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Map/Ground.js), shaders, `getShadowFactor`; [BrowEdit lightmapping](https://github.com/Borf/BrowEdit3/blob/ad89aef809ca52ad32c3a06c162dc508ace7d7f4/docs/Lightmapping.md) | Terrain lighting, shadow sampling and the editor's explicitly distinct bake method |
| S6 | [BrowEdit object placement](https://github.com/Borf/BrowEdit3/blob/ad89aef809ca52ad32c3a06c162dc508ace7d7f4/docs/ObjectEdit.md) and [editor guide](https://github.com/Borf/BrowEdit3/blob/ad89aef809ca52ad32c3a06c162dc508ace7d7f4/docs/Readme.md) | Object categories, transforms, snapping, floor placement and editing responsibilities |
| S7 | [SPR loader](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Loaders/Sprite.js), [ACT loader](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Loaders/Action.js), [entity rendering](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Entity/EntityRender.js), [sprite shader](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/SpriteRenderer.js), [camera direction](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Camera.js) | Sprite formats, eight-direction action lookup, timing, attachments, mirror support, billboarding and ground shadow brightness |
| S8 | [Prontera guide](https://github.com/rathena/rathena/blob/e985006171d2eb320ee512a653f4c83aea3d81b6/npc/pre-re/guides/guides_prontera.txt), [city warps](https://github.com/rathena/rathena/blob/e985006171d2eb320ee512a653f4c83aea3d81b6/npc/warps/cities/prontera.txt), [pre-renewal castle warp](https://github.com/rathena/rathena/blob/e985006171d2eb320ee512a653f4c83aea3d81b6/npc/pre-re/warps/cities/prontera.txt) | Fountain-relative services, civic destinations, gates and interior/field connections |
| S9 | [Geffen guide](https://github.com/rathena/rathena/blob/e985006171d2eb320ee512a653f4c83aea3d81b6/npc/pre-re/guides/guides_geffen.txt), [city warps](https://github.com/rathena/rathena/blob/e985006171d2eb320ee512a653f4c83aea3d81b6/npc/warps/cities/geffen.txt) | Central tower with guild/dungeon function; relative services and distinct exits |
| S10 | [Payon guide](https://github.com/rathena/rathena/blob/e985006171d2eb320ee512a653f4c83aea3d81b6/npc/pre-re/guides/guides_payon.txt) | Mountain-city identity, palace, separate Archer Village and village dungeon threshold; version caveat |
| S11 | [Alberta guide](https://github.com/rathena/rathena/blob/e985006171d2eb320ee512a653f4c83aea3d81b6/npc/pre-re/guides/guides_alberta.txt) | Port identity and forge/Merchant Guild colocation |
| S12 | [ActEditor direction selector](https://github.com/Tokeiburu/ActEditor/blob/c12198b6aaaedcaa1a3850a8d06e0618c2d4fd0c/ActEditor/Core/WPF/EditorControls/ActSelectorComponents/ActionDirectionalControl.xaml.cs), [anchor drawing](https://github.com/Tokeiburu/ActEditor/blob/c12198b6aaaedcaa1a3850a8d06e0618c2d4fd0c/ActEditor/Core/DrawingComponents/AnchorDraw.cs) | Independent editor evidence for groups of eight directions and explicit animation anchors |

For local comparison, inspect `world-content.js`, `world-view.js`, `scene.js`, `hero-registration.js`, `directional-art.js` and `game.js` at the baseline revision. The saved local hall screenshot used here is `/tmp/astraeon-recovery/golden/consortium-1280-800.png`; it is transient QA evidence, not a durable public reference image.

## Applied runtime follow-through — 2026-10-01 / v28

The repair table above describes the inspected v27 baseline. The playable v28 candidate now replaces the competing northern civic facade with an existing smaller shop, repairs full-width route/footprint conflicts, shares four entrance forecourts, clears planting at steps, separates nearby labels and relocates existing guards to the gate. Ground materials and road strokes share the revised facade-compatible projection; sprite view selection uses projected facing. Warrior motion uses even accepted stride cadence and explicit anticipation/contact/recovery offsets.

Three rear-walk generation attempts failed alternating-foot/identity review and were excluded. The shorter accepted rear cycle and four-cardinal reactions remain documented limitations. These changes apply the researched spatial/animation relationships; they do not recreate RO assets, claim a 3D client or close either art gate. See GOLDEN_SCENE.md for in-game QA and public access status.
