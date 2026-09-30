# ASTRAEON — Worlds Beyond the Veil

Original browser-first 2.5D action RPG under an iterative MMORPG vertical-slice production pass. GitHub Pages serves static files. Open the game in a browser; no native client or account is required. Progress saves on that browser/device.

## Play

Phone: joystick left, action buttons right. Tap ground to walk, creature to select/pursue, and glowing exits to change zones. Portrait and landscape have dedicated layouts; rotation preserves the live session.

Desktop: WASD/arrows move, Shift sprint, F attack, Space dodge, 1–4 class skills, Q flask, E interact, Tab cycle nearby targets. Click-to-move is also available. Character menu in town can switch between Warrior, Mage and Ranger for training while keeping progression. More → Preferences selects quality and sound. Sound begins after an interaction, in accordance with browser audio rules.

## Visual consolidation

Content expansion is paused. The central Wayfarer court is the Golden Scene candidate: the primary Consortium Hall and its open forecourt, a smaller fountain meeting point, coherent market frontage, world-aligned painted limestone and distinct circulation widths. Ragnarok Online 1 guides current presentation and town planning. Warrior is the first Golden Character, with registered locomotion and distinct painted hit/death poses. Warrior, Mage and Ranger retain painted directional sprites; the low-poly prototype is excluded from the live client. **Golden Sprite Character and Golden Town Scene approval are pending.** See [GOLDEN_SCENE.md](./GOLDEN_SCENE.md).

## Current work

One connected Shenzhou route: Wayfarer town → Goldenfield Crossroads → Moonbamboo Trail → four-room Moonveil dungeon and guardian. Painted field/forest terrain, authored roads and landmarks, herb/supply interactions, safe camps, wall-aware click pursuit, distinct enemy attacks and matching boss warnings. New players see this region; returning saves retain access to their legacy discoveries.

Original Shenzhou architecture, marketplace/plaza/gate props, paired high-angle camera and full-screen terrain; three illustrated eight-direction character atlases with continuous world-space facing; contact-timed combat, swept projectiles, combo, dodge immunity and recovery, three Tier-1 resource rhythms and authored Base Skills with one compatible gameplay-changing Node; eight monster species and an evolving Moonveil encounter; existing loot, crafting, shop, quest and save systems; ambient walkers and gradual atmospheric changes; generated WebAudio soundtrack/feedback.

The city benchmark has a larger 44 × 40 footprint, widened main avenues, neighborhood anchors and architecture sized relative to a humanoid baseline. Skills can be tuned in town or at a cleared camp. Advanced Path evolution and the free-form composer are inactive; legacy progress remains saved.

## Limits

This is local simulation. Guild, party, market, housing and sparring are local features. There is no live multiplayer or account sync. The 22-class registry and legacy maps are retained for compatibility, not evidence of 22 completed classes or five polished regions. Moonveil has three connected chambers and a guardian court with collidable walls and gates. The regular game retains painted directional actors. Richer transitions beyond the Warrior reaction refinement, directional art consistency, audio composition and mobile hardware performance must pass further inspection before calling the slice production-ready.

See AUDIT.md, ARCHITECTURE.md, STYLE_GUIDE.md, CONTENT_GUIDE.md, ASSET_LICENSES.md, PERFORMANCE.md and DEVELOPMENT_LOG.md. `qa.html` tests actual desktop/portrait/landscape/tablet CSS viewports in the same game instance.

## Local run

Serve this directory with a static web server. There is no dependency install or build step. HTTPS/localhost is required for service workers. No proprietary Ragnarok assets or maps are used.

## Validation

Start `python3 -m http.server 8001 --bind 127.0.0.1` from this directory. Pass `--url http://127.0.0.1:8001` to browser suites (their fallback port is 8000). Run `node --test tests/motion.test.cjs` for movement/combat geometry. With the static server running, run `python3 tests/browser_smoke.py`; this requires Python Playwright and Chromium at `/usr/bin/chromium`. Disposable browser contexts check controls, class attacks, directional views, progression, saves and responsive layout. Outputs default to `/tmp/astraeon-qa`. Run `python3 tests/vertical_slice.py` for a complete new-Ranger town-to-boss journey through normal UI input, including a cleared camp and Node tuning, then crafting and save reload. It writes artifacts to `/tmp/astraeon-slice-qa`. Neither browser suite adds runtime mutation hooks.

Run `python3 tests/skill_nodes.py --url http://127.0.0.1:8001` for compatible one-node selection, reload and actual node effects across all three starting classes. Use a server rooted in the parent directory to validate `/Astraeon-online/` asset and service-worker paths.

Production QA target: https://basicbasja-cloud.github.io/Astraeon-online/ . Commit/push significant changes, confirm the matching Pages deployment succeeds, then play the public build with a fresh browser context and inspect screenshots/console across viewports. A successful workflow or localhost test alone does not close visual acceptance.

Run `python3 tests/golden_scene.py --url http://127.0.0.1:8001` for a fresh Warrior court review through normal input: circulation, eight movement headings, directional attacks, existing skills, dodge, all relocated services and the physical gate/field threshold. It captures four viewports at each approach. Golden approvals remain pending; see GOLDEN_SCENE.md for current public-access limits.
