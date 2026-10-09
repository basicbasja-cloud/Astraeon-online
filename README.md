Current character review: [repaired Swordsman animations](docs/review/character-bodywithoutfit-registration-v1/registration-report.md), with complete dressed-body swaps and an independent Head. Open `character-review.html`; all new art remains **OWNER VISUAL APPROVAL PENDING**. Ordinary game boot and equipment mechanics are unchanged.

# ASTRAEON - Worlds Beyond the Veil

Original browser-first 2.5D action RPG under an iterative MMORPG vertical-slice production pass. Progress saves in the current browser. The playable world uses authored 3D scenery and illustrated directional characters.

## Character rescue branch

`character/ro1-reference-engine-v1` separates reusable motion from painted raster appearance.
The [character review player](character-review.html) immediately autoplays the
ASTRAEON Swordsman Walk, with all eight directions and independent Hair A/B,
Sword A/B, shield, circlet and cape swaps. [Watch the owner animation](docs/review/character-ro1-animated-v1/swordsman-owner-preview.gif).
Idle, Walk and BasicAttack are actual painted animations, based on public RO1
rendered pose evidence. Exact ACT delays remain unknown. New art requires owner
visual approval. [Animated proof report](docs/review/character-ro1-animated-v1/REPORT.md).

[In-world visual review](character-gameplay-review.html) uses an isolated memory
save and existing Mage mechanics with a Swordsman presentation override. Ordinary
boot, gameplay and world files are unchanged. The older Swordsman creator still
requires its missing full-catalogue asset; this three-action proof does not invent
that catalogue. [Historical dummy engine review](character-engine-review.html).
Stop after these three actions until owner approval.

## Current build

Wayfarer is one original geometric regional capital. Architecture revision76 responds to the rejected repeated-house draft: 158 residential/commercial buildings (37 preserved originals, 121 new buildings across nine families), fourteen paired plots consolidated into larger buildings, and distinct Council, Archive and Exchange silhouettes. The royal street hierarchy, two gathering courts, plaza-facing entries, warm timber/clay theme, defended cliff banks and waterline remain. The user's52 decoded Prontera RO3 beta frames are the primary gameplay visual reference for proportions, street edges, frontage and local adjacency; RO1 Prontera, Colmar and Stormwind research supplies additional composition examples. RO3 remains the hard visual target. Authority: `authoring/wayfarer-spatial.blend`, export: `world/v3/wayfarer-spatial.json`. Native geometry, fresh lighting and gameplay review are in progress; visual acceptance remains open.

The town camera uses a 15-degree vertical perspective lens, 46-degree downward pitch, yaw zero, zoom 125 and centered smooth follow. The lens/control reference comes from roBrowser; the shallower pitch is an ASTRAEON choice following user feedback. These are not independently verified Gravity client settings. The earlier concept framing remains available at `?camera=concept38`.

Warrior retains the shipped eight-direction illustrated walk/run/sprint strips and contact-queued strategy transitions. Painted leg alternation, body/root registration, weapons and gait closure remain unaccepted; the diagnosis and held studies are in the current handoff. Mage and Ranger still reuse their existing walk atlases across movement modes. Full frames sample shared GPU textures, while action/fall composition retains Canvas. This town pass installs no replacement character art or cosmetics.

See [the current capital evidence](docs/review/wayfarer-capital-v76/README.md), [the floor correction](docs/review/wayfarer-v74/README.md), [the source73 finishing evidence](docs/review/wayfarer-v72/resumed/README.md), [applied research](research/wayfarer-applied.md), [current handoff](CURRENT_HANDOFF.md), [architecture](ARCHITECTURE.md) and [master plan](MASTER_PLAN.md). Golden visual acceptance remains open; City 2 production stays gated by the master plan.

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

Open `http://127.0.0.1:8011`. Localhost/HTTPS supports the service worker. Boot, page and service-worker cache versions are all 99. Software WebGL renders the world at native CSS resolution; hardware follows screen density up to 1.5×. The former forced half-resolution software path has been removed.

## Modular sprite foundation

[The modular 2D sprite contract](docs/MODULAR_SPRITES.md) provides shared eight-direction
poses, interchangeable character parts, registered sockets and per-frame draw order.
Open [the development compositor](sprite-preview.html) for the temporary Swordsman/Mage
alignment markers. These are `DEV_ONLY / PLACEHOLDER / NOT_FINAL_ART`; existing player
visuals remain active. Run `python tools/validate-sprites.py` to check metadata and atlases.

## Verification

```powershell
python tools/run-node-checks.py
python tools/validate-world-v3.py
$env:ASTRAEON_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
python tests/ragnarok_camera.py --output camera-review
python tests/golden_wayfarer.py --phase services --neighborhoods --travel-mode sprint --startup-timeout-ms 300000 --output town-review
python tests/cache_resume.py --output cache-review
python tests/movement_performance.py --output performance-review.json
```

The browser tools require Python Playwright. Set `ASTRAEON_BROWSER` to a local Chrome/Chromium executable; Windows checks use D3D11 and Linux cloud checks use SwiftShader. Cloud software timings do not certify physical-device performance. The Node helper runs each file separately and reports all individual checks. Saved Blender/export parity is checked by `tools/check-blender-export-v3.py` inside Blender or through the documented bpy runner in the current handoff.

Use the service/neighborhood phase above for the capital. The older `all`,
`spatial`, `market` and `districts` itineraries contain source74 town coordinates;
their captures are historical and need a capital itinerary before reuse. Motion
artwork review remains a separate phase.

Review uses ordinary gameplay input, read-only snapshots and actual screenshots. Fixed-position capture tools use disposable saves strictly for art comparison. Unit tests and exported geometry do not certify artwork quality, physical-device performance or Golden approval.

## Scope

This is a local simulation. There is no live multiplayer, account sync or production MMO server. Mage/Ranger locomotion and broader skill-art polish remain separate work. Historical Canvas/proof paths and older review reports are comparison evidence; default town gameplay uses the spatial renderer. No proprietary Ragnarok maps, sprites or textures are used by the playable runtime. The user-supplied screenshots in `RO3 Ref/` are reference-only evidence; see `ASSET_LICENSES.md`.
