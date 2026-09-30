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

## Scale benchmark and canonical Tier-1 skills — 2026-09-30

- Published the connected Shenzhou work as c7e4a73 and confirmed its successful matching Pages run. Public browser access then failed at the environment proxy; saved precise network additions and continued independent QA without claiming public acceptance.
- Replaced the old absolute player/building scale guideline with human-relative relationships. Enlarged town bounds, landmarks, service buildings and trees, widened main roads, added neighborhood anchors, rebalanced small props and actor dimensions, paired responsive zoom with accurate world-space input, and preserved painted direction views.
- Removed active Advanced Paths/free-form composition; authored twelve starting-class Base Skills and compatibility for six attacks with nine single-layer Nodes. Added locked-area pulses, meaningful contact mechanics, different resource recovery rhythms, selected-target facing during movement and reverse gait.
- Migrated saves to v3 while retaining legacy progress/archived fields. Added v25 core scripts/cache and kept all resource paths repository-relative.
- Fixed the portrait skill menu after screenshot inspection exposed combat controls overlapping cards; verified node selection and persistence through actual phone-sized UI input. Cropped cached-road draws to the visible source region.
- Pure, subpath smoke, real Node gameplay, live responsive iframe and fresh-Ranger expedition QA passed with no runtime/resource errors; detailed scope and performance limits are in AUDIT.md and PERFORMANCE.md. Public acceptance remains blocked until the environment draft's network settings are applied.

- Final camp QA found the inherited menu allowed resting remotely; camp rest/cooking now require the actual cleared caravan site. Six journey checks passed, including camp tuning and walking back to town before crafting. Supply accounting now handles loot discovered naturally during contract combat without expecting a second award.

## RO1-inspired sprite and Golden Town direction reset — 2026-09-30

- Paused content expansion. Kept three richly painted hero classes as the mainline presentation and removed the optional low-poly renderer from the client. Preserved the unapproved technical experiment outside the checkout; it is not shipped or accepted as character art.
- Defined separate pending Golden Sprite Character and Golden Town Scene gates. Ragnarok Online 1 guides town planning and presentation; ASTRAEON lore, Tier-1 skills, Nodes and manual combat remain intact.
- Rebuilt the central court with a fountain focal point, grouped Consortium/market services, perimeter seating and purposeful courtyard vegetation. Relocated the existing shrine into its connected western courtyard. Added explicit avenue/street/service/field hierarchy and stone-to-dirt transition at the existing Caravan Gate.
- Replaced flat screen-axis paving with original painted limestone transformed into world coordinates, integrated ground edges/wear and shared soft contact shadows. Added fountain collision and retained accessible service approaches.
- Passed pure, regular-client subpath, town-interaction and connected-expedition regression locally. No new gameplay content or actor families were added. Door clearance, visual approval, public browser access and physical-device performance remain open.
