# ASTRAEON — Worlds Beyond the Veil

A browser-first, cross-platform 2.5D action RPG prototype. It runs as a static site on GitHub Pages and adapts to phone portrait, phone landscape, tablet, and desktop. No install or account is required to play; character progress is saved in the browser on that device.

## Play

Open the GitHub Pages link and create an adventurer. On a phone, use the virtual joystick on the left and the combat buttons along the bottom. Tap a creature to target it, the ground to move, or a glowing map gate to travel through an exit. Both orientations work; landscape gives the action scene more horizontal room.

Desktop controls: WASD or arrow keys to move, click the ground to walk, click an enemy to target, Space to attack, Shift to dodge, 1–4 for skills, Q for a potion, and E near an NPC to interact. The menus are available from the top bar.

## Prototype systems

- 14 playable races, 22 starting classes, two advanced paths per class, and character origins.
- Higher 3/4 MMORPG field camera with a full-screen organic ground surface, a live minimap, classic click-to-move combat, animated 16-frame hero and wolf atlases, multiple distinct enemy silhouettes, targeting, a three-hit attack combo, dodge with brief invulnerability, guard, healing, Skill Weaving, burst attacks, and readable attack telegraphs.
- Five distinct maps: the safe Shenzhou capital hub, Moonbamboo forest, Goldenfield grassland, Helion magitech rail yard, and the Veyr ruins. Terrain now extends beyond the camera viewport so the playable area fills the screen instead of ending at a diamond-shaped border. Wayfarer Square has a readable central fountain plaza, four surrounding civic blocks, crossing cobblestone streets, lit market stalls, plaza lamps, clustered services, and gates aligned to the main roads. Each map has its own architecture, foliage, animated landmark, and glowing walk-through exits.
- Contract board, Astral Gate travel, level and rank progression, loot, equipment, crafting, NPC market, housing, camp, professions, reputation, personal guild, sparring arena, and a solo boss encounter.
- Four linked story chapters across the field regions. Each chapter has a three-room solo dungeon followed by a two-phase boss with a telegraphed area attack and adds. First clears unlock the next chapter and award a named relic; repeat clears give resources. A failed run returns to the city, while completed character progression remains saved locally.
- Original hand-painted grassland ground texture, with a mobile field HUD inspired by the supplied camera/layout reference: compact status and quest on the left, map on the right, joystick left, circular combat controls over the lower right of the world.
- Skill Weaving composer with Core, Form, Motion, Delivery, Energy, Modifier, Trigger, and Cost Rule nodes.
- Installable web app shell with an offline cache for the game and art. Saves remain in the browser's local storage and do not sync between devices.
- Original ASTRAEON outpost key art and custom illustrated sprite atlases, layered canvas lighting and hit effects, and a custom vector app icon; no third-party runtime dependencies or remote assets.

The camera and map-to-map flow take inspiration from classic MMORPGs such as Ragnarok Online. ASTRAEON uses original locations, names, code, and art; it does not include Ragnarok Online assets or copied maps.

## Current scope

This is a playable single-player campaign prototype, not a live MMO. Guild, market, party, PvP, and housing functions are local simulations. Real multiplayer, account-backed saves, shared economy, authoritative combat, unique ability kits for all 22 classes, and large-scale raids still need server and content work. Active dungeon runs reset on reload; character, equipment, story clears, and quests persist locally.

## Run locally

Serve this folder with any static web server; opening `index.html` directly works for play, but offline installation requires HTTPS or localhost. GitHub Pages serves the repository root.
