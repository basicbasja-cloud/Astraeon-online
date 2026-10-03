# ASTRAEON - Worlds Beyond the Veil

Original browser-first 2.5D action RPG under an iterative MMORPG vertical-slice production pass. Progress saves in the current browser. The playable world uses authored 3D scenery and illustrated directional characters.

## Current build

Wayfarer v47 uses the saved Blender town, exported meshes, materials, navigation, stairs, services and portals in a shared Three.js depth buffer. The town has four times its previous land area, twelve new frontage lots and a connected civic spine and neighbourhood street network. The concept supplies atmosphere and landmark hierarchy; it is not an exact layout template. The source pass reauthors the Consortium Hall, public streets, fountain monument, district buildings, market, gardens, fortified river banks and street furniture. The source is `authoring/wayfarer-spatial.blend`; its matching runtime export is `world/v3/wayfarer-spatial.json`.

The town camera uses a 15-degree vertical perspective lens, 46-degree downward pitch, yaw zero, zoom 125 and centered smooth follow. The lens/control reference comes from roBrowser; the shallower pitch is an ASTRAEON choice following user feedback. These are not independently verified Gravity client settings. The earlier concept framing remains available at `?camera=concept38`.

Warrior walk, run and sprint each have eight complete illustrated frames in eight directions. The corrected run cycle includes contact, passing and flight poses; measured visible boot soles drive whole-body registration. Complete frames sample shared GPU textures, while action/fall composition retains Canvas. Audio warms before movement to avoid the first-footstep hitch. Full-body art replaces procedural locomotion limb overlays. Source sheets, repairs, registration and previews are preserved in `authoring/characters/painted-v4` and `painted-v44`. Hit/death artwork and combat timing retain their existing paths.

See [applied research](research/wayfarer-applied.md), [current handoff](CURRENT_HANDOFF.md), [v47 visual review](docs/review/wayfarer-v47/README.md), [architecture](ARCHITECTURE.md) and [master plan](MASTER_PLAN.md). Golden visual acceptance remains open; City 2 production stays gated by the master plan.

## Play

Desktop: WASD/arrows move, Alt walks, Shift sprints, F attacks, Space dodges, 1-4 use class skills, Q uses the flask, E interacts and Tab cycles nearby targets. Click ground to navigate, actors to interact and exits to change zones. Character training can switch Warrior, Mage and Ranger while retaining progression.

Town camera: wheel zoom; right-drag rotates; Shift-right-drag tilts; Ctrl-right-drag zooms. Double-right-click resets yaw, with Shift resets tilt and with Ctrl resets zoom. Camera gestures do not issue movement commands.

Phone: left joystick and action buttons, with tap navigation and interactions. Portrait, landscape and tablet layouts preserve the live session. More > Preferences controls quality and sound.

The connected route remains Wayfarer > Goldenfield Crossroads > Moonbamboo Trail > four-room Moonveil dungeon and guardian. Existing quests, supply discoveries, loot, crafting, class resources, Base Skills with one compatible Node, combat and saves are retained.

## Local run

No build step or npm install is required. Serve the checkout with a static server:

```powershell
python -m http.server 8011 --bind 127.0.0.1
```

Open `http://127.0.0.1:8011`. Localhost/HTTPS supports the service worker. Runtime cache version is 47.

## Verification

```powershell
node --test tests/*.test.cjs
python tools/validate-world-v3.py
$env:ASTRAEON_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python tests/ragnarok_camera.py --output camera-review
python tests/golden_wayfarer.py --phase all --motion-series --output town-review
python tests/movement_performance.py --output performance-review.json
```

The browser tools require Python Playwright. Set `ASTRAEON_BROWSER` to a local Chrome/Chromium executable; the Windows checks use hardware D3D11. Saved Blender/export parity is checked by `tools/check-blender-export-v3.py` inside Blender or through the documented bpy runner in the current handoff.

Review uses ordinary gameplay input, read-only snapshots and actual screenshots. Fixed-position capture tools use disposable saves strictly for art comparison. Unit tests and exported geometry do not certify artwork quality, physical-device performance or Golden approval.

## Scope

This is a local simulation. There is no live multiplayer, account sync or production MMO server. Mage/Ranger locomotion and broader skill-art polish remain separate work. Historical Canvas/proof paths and older review reports are comparison evidence; default town gameplay uses the spatial renderer. No proprietary Ragnarok maps, sprites or textures are included.
