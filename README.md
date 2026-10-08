# ASTRAEON - Worlds Beyond the Veil

Original browser-first 2.5D action RPG under an iterative MMORPG vertical-slice production pass. Progress saves in the current browser. The playable world uses authored 3D scenery and illustrated directional characters.

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

Open `http://127.0.0.1:8011`. Localhost/HTTPS supports the service worker. Boot, page and service-worker cache versions are all 91. Software WebGL renders the world at native CSS resolution; hardware follows screen density up to 1.5×. The former forced half-resolution software path has been removed.

The progression/stat/save foundation of Backbone 0.0.1 uses independent Base/Job
EXP, validated STR/AGI/VIT/INT/DEX/LUK allocation, data-driven derived stats and
save version 5. Legacy saves migrate through compatibility adapters. Open
`http://127.0.0.1:8011/tools/progression.html` for the isolated developer harness;
`?qa=1&dev=1` exposes the same APIs on a disposable playable character. See
[the system contract and compatibility notes](docs/CORE_SPINE_PROGRESSION.md).
This foundation does not complete the whole Core Spine patch.

The Base skill tree extension supports Swordsman (the existing Warrior adapter)
and Mage: immutable definitions, Job/prerequisite/rank gates, Skill Point spend,
debug paid refunds, automatic passive modifiers and persisted ranks. The same
harness now supports skill inspection, learning, rank-up, eight-slot assignment
and compatible Nodes. New characters start unlearned/unassigned; returning saves
retain the documented fixed-button compatibility. Existing four buttons bridge
slots 1–4; production learning UI and controls for slots 5–8 remain future work.
See [the skill architecture and compatibility contract](docs/CORE_SPINE_SKILL_TREE.md).

The staged combat foundation routes player physical/magical contacts through an
immutable resolver with injected RNG, separate Perfect Dodge, CRIT, DEF/MDEF,
penetration, resistance and mitigation. Open `tools/combat.html` for fixture
inspection. Future saves are blocked without overwriting storage; Stat refunds
retain actual paid expenditure across cost changes. All combat coefficients are
provisional; incoming enemy contacts now use the same resolver through the
Monster Lifecycle adapter. Status/presentation remain separate. See
[combat contracts](docs/CORE_SPINE_COMBAT.md) and
[verification report](docs/CORE_SPINE_COMBAT_REPORT.md).

All eight learned skill slots now share explicit-time eligibility, authored
cooldowns and an atomic launch/resource commit. The existing controls use slots
1–4; slots 5–8 execute through developer tooling. Basic Attack and Potion remain
separate. In-combat configuration changes lock all eight slots; class changes
retain incompatible assignments as dormant. Configuration survives transitions
and reload, while cooldown timestamps are transient. See
[Action Loadout contracts](docs/CORE_SPINE_ACTION_LOADOUT.md) and
[verification report](docs/CORE_SPINE_ACTION_LOADOUT_REPORT.md). This completes
only the eight-slot behavior/persistence/cooldown foundation, not Patch 0.0.1.

The [Action Item foundation](docs/CORE_SPINE_ACTION_ITEMS.md) routes the current
Potion and Ration through validated effects, non-mutating prepare, exact-once
atomic effect/debit commit and deterministic item/function cooldowns. They remain
outside learned slots 1–8. Full resources reject without consumption; provisional
cooldowns are configured separately from skills. Save version remains 5; clocks
survive death/travel on the same timeline and reset on reload. The inventory
harness now includes deterministic item-time controls. See
[verified Action Item handoff](docs/CORE_SPINE_ACTION_ITEMS_REPORT.md).

The [Monster Loot foundation](docs/CORE_SPINE_MONSTER_LOOT.md) connects registered
monster deaths to validated immutable tables, injected RNG, pure resolution and
owned per-life claims. Mixed stack/ItemInstance/gold rewards commit once through
canonical ownership; Base/Job EXP and quest credit retain their existing
separate authorities. Current direct-on-death rewards and prototype kill cycles
are retained. Final drop balance, ground-loot UI and Monster Box opening remain
future work. `/tools/monster-loot.html` is an isolated
in-memory sandbox. See [verified loot handoff](docs/CORE_SPINE_MONSTER_LOOT_REPORT.md).
Patch 0.0.1 and Core Spine remain incomplete.

The [Monster Lifecycle foundation](docs/CORE_SPINE_MONSTER_LIFECYCLE.md) adds
immutable mechanical definitions, explicit spawn/runtime/life identity and
deterministic detection, target ownership, chase/attack intents, home leash,
return, authoritative death and per-life respawn. Existing navigation consumes
movement intents; shared Combat applies enemy contacts and existing Loot commits
death rewards once. Four generic mechanical fixtures are provisional. AI state
is transient; save version stays 5. `/tools/monster-lifecycle.html` is an isolated
in-memory clock/target/death/respawn sandbox. See
[verified lifecycle handoff](docs/CORE_SPINE_MONSTER_LIFECYCLE_REPORT.md).
Final monster content, balance, navigation and presentation remain future work.

## Verification

The [Item / Inventory / Equipment foundation](docs/CORE_SPINE_ITEMS.md) now owns
definition-ID stacks, stable non-stack instances and equipped instance references.
Existing crafting, merchant, rewards and consumables use the shared canonical API.
Save version is **5**, migrated deterministically from earlier saves; cache version
is **91**. `/tools/inventory.html` provides an isolated developer sandbox.
See [verified results and handoff](docs/CORE_SPINE_ITEMS_REPORT.md). Final inventory
UI, item balance/content and the remaining Patch 0.0.1 systems are still open.

```powershell
python tools/run-node-checks.py
python tests/monster_lifecycle_browser.py --url http://127.0.0.1:8011
python tests/monster_loot_browser.py --url http://127.0.0.1:8011
python tests/action_item_browser.py --url http://127.0.0.1:8011
python tests/inventory_browser.py --url http://127.0.0.1:8011
python tests/action_loadout_browser.py --url http://127.0.0.1:8011
python tests/combat_browser.py --url http://127.0.0.1:8011
python tests/skill_tree_browser.py --url http://127.0.0.1:8011
python tests/progression_browser.py --url http://127.0.0.1:8011
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
