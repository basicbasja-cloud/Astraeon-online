# Content authoring

Current production gate: stop content expansion until Golden Sprite Character and Golden Town Scene are approved in the deployed game. Refine the three existing painted Warrior/Mage/Ranger sets and Wayfarer Court; do not add maps, classes, districts, NPC families or decorative asset families. Ragnarok Online 1 is the presentation/planning reference; ASTRAEON remains original. Express Node variation through existing gameplay/VFX rather than new character sheets. See GOLDEN_SCENE.md.

Reference workflow: read [RAGNAROK_REFERENCE.md](./RAGNAROK_REFERENCE.md), then use the current [ground plan](./docs/reference/wayfarer-plan.svg) alongside actual gameplay views. The plan is diagnostic; facade perspective, actor beauty and animation require in-scene review. It reads current source with `node tools/reference-plan.cjs` and adds no runtime assets.

1. Follow STYLE_GUIDE.md. Use original or explicitly licensed material and update ASSET_LICENSES.md.
2. Place props with Cartesian x/y ground coordinates, explicit dimensions and foot anchors. Mark trees/buildings for occlusion fading. Surround civic buildings with service NPCs, paths and useful detail.
3. Atlas entries must specify source rectangles and ground anchors. Inspect actual output, not just the source sheet. Transparent RGB colors can be misleading: validate alpha and rendered edges.
4. Author Base Skills in combat.js with targeting shape, range, timing, cost, cooldown, animation and deliberate gameplay identity. Declare compatible single-layer nodes in skill-nodes.js; one string choice per Base Skill, no arbitrary effect composer or nested progression. Verify every node through contact gameplay, not just a recolor. Defensive skills need not accept nodes.
5. Enemy species stats currently live beside the local integration in game.js. Eight original species use different speed, range, telegraph timing and durability. Boss patterns alternate close sweep, targeted charge and wider seal; phase two speeds up and summons adds.
6. Five-region identity planning exists in world-content.js. Prioritize Shenzhou town/field/forest/Moonveil before polishing or expanding inherited legacy zones.

Current content gaps: investigation/escort/environment quests; dedicated open-chest/pickup animation art; more enemy locomotion frames; building interiors. Do not treat menu entries or registry names as finished content. Only Warrior, Mage and Ranger Tier-1 training is active; Advanced Paths remain inactive.

Shenzhou zone objects, road splines and interactables are authored in `environment.js`. Dungeon rooms/passages and unlock boundaries live in `dungeon.js`. Attack plans in `enemy-combat.js` drive both damage geometry and the visible warning; edits must keep them in agreement. `navigation.js` is invisible route planning, not a tiled visual world. New players see only this region; saves with later legacy discoveries/chapters retain access to their inherited content.

Town scale and collision footprints live in `world-content.js`; responsive actor/camera dimensions live in `world-view.js`. Adjust their relationships together and review the plaza/market benchmark before extending other neighborhoods. Do not restore old pixel dimensions for compatibility. Public GitHub Pages is the primary acceptance target after each significant committed/pushed pass; local and subpath QA are supporting evidence only.

## Existing-town placement pass

Before changing an existing building, record role/frontage, occupied ground, entrance/clear approach, source anchor, projected dimensions, occlusion and shared material/light family. Edit the corresponding `townObjects`, `townBlocks`, road edge and service position together as needed. Functional NPC positions live in `game.js`; the four forecourt polygons live in `world-content.js`. They are not all contained in one building record.

Review the hall → court → market → Caravan Gate route first. Keep the fountain perimeter and exit mouth open. Register frontages against projected base outlines. Do not rotate a painted facade in screen space to change which street it faces. Narrow dirt routes lead to services/courtyards; stone secondary streets remain distinct from the main avenue. Two existing guards now patrol at the gate; one customer circulates at the market. Review reachable routes and leave the central court quiet.

The v27 reference plan exposed roads inside the residence footprint. In v28 the residence/art/service were moved together, the southern street runs at y=28.6, the service route approaches along y=28.7, and the shrine route reaches its front around the occupied volume. A pure regression samples every road segment against every footprint with 0.2-unit human clearance, including full corridor width and round end caps. This verifies authored rectangles, not the painted facade perspective.

## Golden Warrior replacement pass

Freeze one identity and game-camera convention. Replace only the rejected rear/stride views or other specifically failed poses. Inspect direction, handedness, face/hair/cape continuity and silhouette before registering source rectangles and boot contacts in `hero-registration.js` / `directional-metadata.js`. Preserve standing scale in hit/death poses. Review normal-size motion alongside the Registrar, hall door, fountain and stall; do not accept an atlas solely at enlarged viewing size. Existing Nodes reuse body motion and vary contact behavior/VFX.
