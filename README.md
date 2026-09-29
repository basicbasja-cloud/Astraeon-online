# ASTRAEON — Worlds Beyond the Veil

A browser-first, cross-platform 2.5D action RPG prototype. It runs as a static site on GitHub Pages and adapts to phone portrait, phone landscape, tablet, and desktop. No install or account is required to play; character progress is saved in the browser on that device.

## Play

Open the GitHub Pages link and create an adventurer. On a phone, use the virtual joystick on the left and the combat buttons along the bottom. Tap a creature to target it, or tap the ground to move. Both orientations work; landscape gives the action scene more horizontal room.

Desktop controls: WASD or arrow keys to move, click the ground to walk, click an enemy to target, Space to attack, Shift to dodge, 1–4 for skills, Q for a potion, and E near an NPC to interact. The menus are available from the top bar.

## Prototype systems

- 14 playable races, 22 starting classes, two advanced paths per class, and character origins.
- Isometric action scene with enemy targeting, movement, three-hit attack combo, dodge with brief invulnerability, guard, healing, class skill, burst attacks, and enemy encounters.
- Contract board, five zones, Astral Gate travel, level and rank progression, loot, equipment, crafting, NPC market, housing, camp, professions, reputation, personal guild, sparring arena, and a solo boss encounter.
- Skill Weaving composer with Core, Form, Motion, Delivery, Energy, Modifier, Trigger, and Cost Rule nodes.
- Installable web app shell with a small offline cache. Saves remain in the browser's local storage and do not sync between devices.
- Hand-drawn canvas scene and a custom vector app icon; no third-party runtime dependencies or remote assets.

## Current scope

This is a playable single-player prototype, not a live MMO. Guild, market, party, PvP, raid, and housing functions are local simulations. Real multiplayer, account-backed saves, shared economy, authoritative combat, and full unique abilities for every class still need server and content work.

## Run locally

Serve this folder with any static web server; opening `index.html` directly works for play, but offline installation requires HTTPS or localhost. GitHub Pages serves the repository root.
