# ASTRAEON — Worlds Beyond the Veil

Original browser-first 2.5D action RPG under an iterative MMORPG vertical-slice production pass. GitHub Pages serves static files. Open the game in a browser; no native client or account is required. Progress saves on that browser/device.

## Play

Phone: joystick left, action buttons right. Tap ground to walk, creature to select/pursue, and glowing exits to change zones. Portrait and landscape have dedicated layouts; rotation preserves the live session.

Desktop: WASD/arrows move, Shift sprint, F attack, Space dodge, 1–4 class skills, Q flask, E interact, Tab cycle nearby targets. Click-to-move is also available. Character menu in town can switch between Warrior, Mage and Ranger for training while keeping progression. More → Preferences selects quality and sound. Sound begins after an interaction, in accordance with browser audio rules.

## Current work

One connected Shenzhou route: Wayfarer town → Goldenfield Crossroads → Moonbamboo Trail → four-room Moonveil dungeon and guardian. Painted field/forest terrain, authored roads and landmarks, herb/supply interactions, safe camps, wall-aware click pursuit, distinct enemy attacks and matching boss warnings. New players see this region; returning saves retain access to their legacy discoveries.

Original Shenzhou architecture, marketplace/plaza/gate props, paired high-angle camera and full-screen terrain; three illustrated eight-direction character atlases with continuous world-space facing; contact-timed combat, swept projectiles, combo, dodge immunity and recovery, burn/slow/knockback and compiled skill nodes; eight monster species and an evolving Moonveil encounter; existing loot, crafting, shop, quest and save systems; ambient walkers and gradual atmospheric changes; generated WebAudio soundtrack/feedback.

## Limits

This is local simulation. Guild, party, market, housing and sparring are local features. There is no live multiplayer or account sync. The 22-class registry and legacy maps are retained for compatibility, not evidence of 22 completed classes or five polished regions. Moonveil has three connected chambers and a guardian court with collidable walls and gates. Directional views cover the circle in 45° steps; this is painted 2.5D art, not a skinned 3D model. Richer action/death animations, directional art consistency, audio composition and mobile hardware performance must pass further inspection before calling the slice production-ready.

See AUDIT.md, ARCHITECTURE.md, STYLE_GUIDE.md, CONTENT_GUIDE.md, ASSET_LICENSES.md, PERFORMANCE.md and DEVELOPMENT_LOG.md. `qa.html` tests actual desktop/portrait/landscape/tablet CSS viewports in the same game instance.

## Local run

Serve this directory with a static web server. There is no dependency install or build step. HTTPS/localhost is required for service workers. No proprietary Ragnarok assets or maps are used.

## Validation

Run `node --test tests/motion.test.cjs` for movement/combat geometry. With the static server running, run `python3 tests/browser_smoke.py`; this requires Python Playwright and Chromium at `/usr/bin/chromium`. Disposable browser contexts check controls, class attacks, directional views, progression, saves and responsive layout. Outputs default to `/tmp/astraeon-qa`. Run `python3 tests/vertical_slice.py` for a complete new-Ranger town-to-boss journey through normal UI input, then crafting and save reload. It writes artifacts to `/tmp/astraeon-slice-qa`. Neither browser suite adds runtime mutation hooks.
