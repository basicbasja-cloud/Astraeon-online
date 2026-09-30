# Content authoring

Current production gate: stop content expansion until Golden Sprite Character and Golden Town Scene are approved in the deployed game. Refine the three existing painted Warrior/Mage/Ranger sets and Wayfarer Court; do not add maps, classes, districts, NPC families or decorative asset families. Ragnarok Online 1 is the presentation/planning reference; ASTRAEON remains original. Express Node variation through existing gameplay/VFX rather than new character sheets. See GOLDEN_SCENE.md.

1. Follow STYLE_GUIDE.md. Use original or explicitly licensed material and update ASSET_LICENSES.md.
2. Place props with Cartesian x/y ground coordinates, explicit dimensions and foot anchors. Mark trees/buildings for occlusion fading. Surround civic buildings with service NPCs, paths and useful detail.
3. Atlas entries must specify source rectangles and ground anchors. Inspect actual output, not just the source sheet. Transparent RGB colors can be misleading: validate alpha and rendered edges.
4. Author Base Skills in combat.js with targeting shape, range, timing, cost, cooldown, animation and deliberate gameplay identity. Declare compatible single-layer nodes in skill-nodes.js; one string choice per Base Skill, no arbitrary effect composer or nested progression. Verify every node through contact gameplay, not just a recolor. Defensive skills need not accept nodes.
5. Enemy species stats currently live beside the local integration in game.js. Eight original species use different speed, range, telegraph timing and durability. Boss patterns alternate close sweep, targeted charge and wider seal; phase two speeds up and summons adds.
6. Five-region identity planning exists in world-content.js. Prioritize Shenzhou town/field/forest/Moonveil before polishing or expanding inherited legacy zones.

Current content gaps: investigation/escort/environment quests; dedicated open-chest/pickup animation art; more enemy locomotion frames; building interiors. Do not treat menu entries or registry names as finished content. Only Warrior, Mage and Ranger Tier-1 training is active; Advanced Paths remain inactive.

Shenzhou zone objects, road splines and interactables are authored in `environment.js`. Dungeon rooms/passages and unlock boundaries live in `dungeon.js`. Attack plans in `enemy-combat.js` drive both damage geometry and the visible warning; edits must keep them in agreement. `navigation.js` is invisible route planning, not a tiled visual world. New players see only this region; saves with later legacy discoveries/chapters retain access to their inherited content.

Town scale and collision footprints live in `world-content.js`; responsive actor/camera dimensions live in `world-view.js`. Adjust their relationships together and review the plaza/market benchmark before extending other neighborhoods. Do not restore old pixel dimensions for compatibility. Public GitHub Pages is the primary acceptance target after each significant committed/pushed pass; local and subpath QA are supporting evidence only.
