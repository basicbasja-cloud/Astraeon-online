# Content authoring

1. Follow STYLE_GUIDE.md. Use original or explicitly licensed material and update ASSET_LICENSES.md.
2. Place props with Cartesian x/y ground coordinates, explicit dimensions and foot anchors. Mark trees/buildings for occlusion fading. Surround civic buildings with service NPCs, paths and useful detail.
3. Atlas entries must specify source rectangles and ground anchors. Inspect actual output, not just the source sheet. Transparent RGB colors can be misleading: validate alpha and rendered edges.
4. Ability definitions in combat.js contain targeting shape, range, timing, cost, cooldown, animation, element and composable effect tags. Validate impact timing and hit geometry. Expose only composer options that have working behavior.
5. Enemy definitions currently live beside the local integration in game.js. Eight original species use different speed, range, telegraph timing and durability. Boss patterns alternate close sweep, targeted charge and wider seal; phase two speeds up and summons adds.
6. Five-region identity planning exists in world-content.js. Prioritize Shenzhou town/field/forest/Moonveil before polishing or expanding inherited legacy zones.

Current content gaps: authored dungeon corridors and room navigation; investigation/escort/environment quests; persistent loot pickup presentation; more enemy locomotion frames; class-specific resources; building interiors. Do not treat menu entries or registry names as finished content.
