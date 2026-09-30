# ASTRAEON — Worlds Beyond the Veil

Original browser-first 2.5D action RPG under an iterative MMORPG vertical-slice production pass. GitHub Pages serves static files. Open the game in a browser; no native client or account is required. Progress saves on that browser/device.

## Play

Phone: joystick left, action buttons right. Tap ground to walk, creature to select/pursue, and glowing exits to change zones. Portrait and landscape have dedicated layouts; rotation preserves the live session.

Desktop: WASD/arrows move, Shift sprint, F attack, Space dodge, 1–4 class skills, Q flask, E interact, Tab cycle nearby targets. Click-to-move is also available. Character menu in town can switch between Warrior, Mage and Ranger for training while keeping progression. More → Preferences selects quality and sound. Sound begins after an interaction, in accordance with browser audio rules.

## Current work

Original Shenzhou architecture, marketplace/plaza/gate props, paired high-angle camera and full-screen terrain; three illustrated animation atlases; contact-timed combat, swept projectiles, combo, dodge immunity and recovery, burn/slow/knockback and compiled skill nodes; eight monster species and an evolving Moonveil encounter; existing loot, crafting, shop, quest and save systems; ambient walkers and gradual atmospheric changes; generated WebAudio soundtrack/feedback.

## Limits

This is local simulation. Guild, party, market, housing and sparring are local features. There is no live multiplayer or account sync. The 22-class registry and legacy maps are retained for compatibility, not evidence of 22 completed classes or five polished regions. The dungeon remains a wave encounter pending authored room production. Animation transitions, environment density, audio composition and mobile hardware performance must pass further inspection before calling the slice production-ready.

See AUDIT.md, ARCHITECTURE.md, STYLE_GUIDE.md, CONTENT_GUIDE.md, ASSET_LICENSES.md, PERFORMANCE.md and DEVELOPMENT_LOG.md. `qa.html` tests actual desktop/portrait/landscape/tablet CSS viewports in the same game instance.

## Local run

Serve this directory with a static web server. There is no dependency install or build step. HTTPS/localhost is required for service workers. No proprietary Ragnarok assets or maps are used.
