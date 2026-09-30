# Development log

## 2026-09-30 — Audit and production scope
- Audited the existing static Canvas2D client and live Pages build.
- Preserved inventory, saves, menus, quests and campaign rules.
- Fixed priority to one Shenzhou slice, three archetypes and one city benchmark.
- Recorded current visual/combat failures in AUDIT.md and created STYLE_GUIDE.md.
- Next: replace primitive benchmark presentation, authored ground paths and camera startup; then timed combat/animation.

## Animation / combat foundation pass
- Added original three-class 36-pose atlases, eight-species and Moonveil boss atlases; metadata includes explicit row extraction for uneven generated gutters.
- Split device bindings, ability timeline/geometry, animation presentation and ambient systems from existing progression integration. Preserved save key, equipment, crafting, shops and quest logic.
- Contact-time damage, true projectile travel with swept collision, recovery/cooldown, movement scaling while casting, continuous dodge/cancel and death presentation before recovery.
- Enemy timing/speed/range differ across eight species; phase-two boss alternates three target patterns and summons adds. Corrected world-space telegraphs.
- Added authored secondary city props, cached paved square, service walkers, quality preferences, gradual atmosphere and original synthesized audio. Removed auto combat from the active flow.
- Pure regression checks passed: no pre-impact damage, forward cone geometry, swept first-hit projectile and piercing multiple contacts.
- Browser production QA pending for this new source commit. Existing city benchmark was visually inspected in desktop and 390×844 portrait; no world boundary/void visible, but old status/quest panels were too large.
- Known gaps: no full animation blend/rig pipeline, enemy locomotion limited, dungeon authored corridors, chunk streaming, true online adapter, real phone profiling. Current benchmark gate remains under review.

## Directional characters and authored Moonveil — 2026-09-30

- Preserved the previous painted character style with eight authored views for three archetypes, eight enemy species and the guardian. Removed blocky actor geometry from the runtime.
- Separated continuous world-space position, smooth yaw, facing modes, analog speed and gait into `character-motion.js`; attacks wait for facing convergence and effects share the same aim.
- Added four connected Moonveil rooms, physical wall collision and player-controlled gates while retaining existing rewards and progression.
- Preserved local saves, added heading persistence and movement autosave, and refreshed the service-worker cache to v22.
- Added pure geometry regression tests and browser controls/combat/save/layout checks. See PERFORMANCE.md for validation scope and hardware limitations.

## Connected Shenzhou production pass — 2026-09-30

- Added original outdoor/ruin atlases and four terrain materials; authored road branches, supply/herb/camp/shrine interactions, painted ruin walls and actual room minimap. Removed abandoned low-poly renderer and unused tiled/arena presentation.
- Added distinct hostile sweep/charge/projectile/hazard plans sharing their visible warning geometry, guardian phase UI and wall-safe projectiles. Fixed normal player pursuit through obstacles, reachable gates, retained next-room targets and safe post-clear return.
- Added bounded route planning, one-time world claims, versioned save normalization, asynchronous zone preparation/retry, core-only asset precache and service worker v24. Preserved existing progression IDs and legacy access.
- Compacted phone HUD/quest controls and added original SVG icons and spatial water ambience. Extended six directions to eight painted walk phases for each archetype, retaining accepted shorter north/northwest cycles where generated sheets did not preserve orientation.
- Fresh-Ranger UI run passed all five journey checks including all guardian attacks, crafting/equipment and reload. Final regression/performance evidence is recorded in PERFORMANCE.md. Further production art, elevation, network simulation and real-device gates remain open.

- Final inspection corrected first-clear guidance to stay in Shenzhou, aligned contract/forest creature names with the authored region, and verified returning saves still expose their legacy maps/chapters. Raised the desktop guardian HUD to keep more of the actor visible. Added adjacent-wall muzzle collision coverage.
