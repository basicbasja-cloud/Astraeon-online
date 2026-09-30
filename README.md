# ASTRAEON — Worlds Beyond the Veil

A browser-first, cross-platform 2.5D action RPG prototype. It runs as a static site on GitHub Pages and adapts to phone portrait, phone landscape, tablet, and desktop. No install or account is required to play; character progress is saved in the browser on that device.

## Play

Open the GitHub Pages link and create an adventurer. On a phone, use the virtual joystick on the left and the combat buttons along the bottom. Tap a creature to target it, the ground to move, or a glowing map gate to travel through an exit. Both orientations work; landscape gives the action scene more horizontal room.

Desktop controls: WASD or arrow keys to move, click the ground to walk, click an enemy to target, Space to attack, Shift to dodge, 1–4 for skills, Q for a potion, and E near an NPC to interact. The menus are available from the top bar.

## Prototype systems

- 14 playable races, 22 starting classes, two advanced paths per class, and character origins.
- Elevated 3/4 MMORPG camera with classic click-to-move combat, animated 16-frame hero and wolf atlases, enemy targeting, three-hit attack combo, dodge with brief invulnerability, guard, healing, class skill, burst attacks, and enemy encounters.
- Five distinct maps: the safe Shenzhou capital hub, Moonbamboo forest, Goldenfield grassland, Helion magitech rail yard, and the Veyr ruins. Wayfarer Square now has a readable central fountain plaza, four surrounding civic blocks, crossing cobblestone streets, lit market stalls, plaza lamps, clustered services, and gates aligned to the main roads. Each map has its own architecture, foliage, animated landmark, and glowing walk-through exits.
- Contract board, Astral Gate travel, level and rank progression, loot, equipment, crafting, NPC market, housing, camp, professions, reputation, personal guild, sparring arena, and a solo boss encounter.
- Skill Weaving composer with Core, Form, Motion, Delivery, Energy, Modifier, Trigger, and Cost Rule nodes.
- Installable web app shell with an offline cache for the game and art. Saves remain in the browser's local storage and do not sync between devices.
- Original ASTRAEON outpost key art and custom illustrated sprite atlases, layered canvas lighting and hit effects, and a custom vector app icon; no third-party runtime dependencies or remote assets.

The camera and map-to-map flow take inspiration from classic MMORPGs such as Ragnarok Online. ASTRAEON uses original locations, names, code, and art; it does not include Ragnarok Online assets or copied maps.

## Current scope

This is a playable single-player prototype, not a live MMO. Guild, market, party, PvP, raid, and housing functions are local simulations. Real multiplayer, account-backed saves, shared economy, authoritative combat, and full unique abilities for every class still need server and content work.

## Run locally

Serve this folder with any static web server; opening `index.html` directly works for play, but offline installation requires HTTPS or localhost. GitHub Pages serves the repository root.
