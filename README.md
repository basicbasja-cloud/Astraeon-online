# ASTRAEON - Worlds Beyond the Veil

Original browser-first 2.5D action RPG under an iterative MMORPG vertical-slice production pass. Progress saves in the current browser. The playable world uses authored 3D scenery and illustrated directional characters.

## Current build

Wayfarer source68 uses the saved Blender town and matching Three.js geometry. RO3 is the hard reference for exteriors, scale, textures, shading, street enclosure and the fountain. All 36 ordinary house envelopes are rebuilt, with one new approach house and 13.1% more occupied house ground. Timber facades have paned openings and steep clay roofs with paired dormers or shuttered gables. The fountain has tiered pools, a scalloped rim, planted corners, green benches, real walkable steps and animated water. Source67's original texture atlas continues with refreshed native lighting. Source: `authoring/wayfarer-spatial.blend`; export: `world/v3/wayfarer-spatial.json`. Review evidence and limits are linked below.

The town camera uses a 15-degree vertical perspective lens, 46-degree downward pitch, yaw zero, zoom 125 and centered smooth follow. The lens/control reference comes from roBrowser; the shallower pitch is an ASTRAEON choice following user feedback. These are not independently verified Gravity client settings. The earlier concept framing remains available at `?camera=concept38`.

Warrior retains the shipped eight-direction illustrated walk/run/sprint strips and contact-queued strategy transitions. Painted leg alternation, body/root registration, weapons and gait closure remain unaccepted; the diagnosis and held studies are in the current handoff. Mage and Ranger still reuse their existing walk atlases across movement modes. Full frames sample shared GPU textures, while action/fall composition retains Canvas. This town pass installs no replacement character art or cosmetics.

See [the source68 review](docs/review/wayfarer-v68/README.md), [applied research](research/wayfarer-applied.md), [current handoff](CURRENT_HANDOFF.md), [architecture](ARCHITECTURE.md) and [master plan](MASTER_PLAN.md). Golden visual acceptance remains open; City 2 production stays gated by the master plan.

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

Open `http://127.0.0.1:8011`. Localhost/HTTPS supports the service worker. Boot, page and service-worker cache versions are all 68. Software WebGL renders the world at native CSS resolution; hardware follows screen density up to 1.5×. The former forced half-resolution software path has been removed.

## Verification

```powershell
python tools/run-node-checks.py
python tools/validate-world-v3.py
$env:ASTRAEON_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python tests/ragnarok_camera.py --output camera-review
python tests/golden_wayfarer.py --phase all --motion-series --output town-review
python tests/cache_resume.py --output cache-review
python tests/movement_performance.py --output performance-review.json
```

The browser tools require Python Playwright. Set `ASTRAEON_BROWSER` to a local Chrome/Chromium executable; Windows checks use D3D11 and Linux cloud checks use SwiftShader. Cloud software timings do not certify physical-device performance. The Node helper runs each file separately and reports all individual checks. Saved Blender/export parity is checked by `tools/check-blender-export-v3.py` inside Blender or through the documented bpy runner in the current handoff.

Review uses ordinary gameplay input, read-only snapshots and actual screenshots. Fixed-position capture tools use disposable saves strictly for art comparison. Unit tests and exported geometry do not certify artwork quality, physical-device performance or Golden approval.

## Scope

This is a local simulation. There is no live multiplayer, account sync or production MMO server. Mage/Ranger locomotion and broader skill-art polish remain separate work. Historical Canvas/proof paths and older review reports are comparison evidence; default town gameplay uses the spatial renderer. No proprietary Ragnarok maps, sprites or textures are included.
