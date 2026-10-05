# Development log

## 2026-09-30 — Ragnarok reference research and production application

- Inspected pinned roBrowser terrain/world/navigation/model/sprite code, BrowEdit object/lightmap documentation, ActEditor direction/anchor controls and rAthena guides/warps for four towns. Recorded source-confirmed behavior separately from ASTRAEON recommendations in RAGNAROK_REFERENCE.md. Public iRO Wiki access returned proxy HTTP 403; no fresh official screenshot survey or original studio workflow is claimed.
- Applied route-first placement, paired entrance/footprint/art registration, shared projected ground, coherent material/light and bounded Warrior pose-production rules to STYLE_GUIDE.md, CONTENT_GUIDE.md and GOLDEN_SCENE.md.
- Added an original source-generated ground-plan diagnostic and regeneration tool. The diagram distinguishes collision blocks from painted anchors and services. Corrected earlier prose: current guard routes patrol the court, not the Caravan Gate.
- The plan exposed southeast service/stone route points inside the residence collision footprint. Added paired road/footprint repair to the next Golden layout brief; existing navigation success does not validate painted-road placement.
- Identified the focused next repair order without expanding content: hall hierarchy/frontage, forecourt readability, rear gait defects, functional circulation and material/occlusion refinement. Runtime v27 and both pending visual gates retain their current status.

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
- Passed pure, regular-client subpath, town-interaction and connected-expedition regression locally. No new gameplay content or actor families were added. Public access was restored after the earlier proxy denial. Trusted the installed environment proxy CA by public-key fingerprints for Chromium and verified the deployed candidate through actual input and four viewport screenshots. The full six-check fresh-Ranger expedition also passed on GitHub Pages through camp, four rooms, guardian, return, crafting and reload. A fresh Mage town check reported no console/runtime/resource errors. Door clearance, final art approval and physical-device performance remain open.

## Golden Warrior / Consortium Court recovery — 2026-09-30

- Began from clean `abd713e`; confirmed remote main and the preceding successful Pages deployment. No failed-run completion was assumed.
- Selected the existing painted Warrior as the first Golden Character, defined the Shenzhou frontier-town concept and made the Consortium Hall the primary civic landmark. Content expansion and low-poly character work remain frozen.
- Registered Warrior boot contacts and one visible body-height baseline across directions and gait sheets. Added eight distinct standing-hit/fallen-death frames in four cardinal views; diagonal reactions select the nearest authored view. Kept the accepted rear locomotion fallback. Rejected the inconsistent 24-frame reaction attempt.
- Refined only the existing Consortium Hall with a taller open entrance and shallow stairs. Connected its forecourt to a wider eastbound main avenue; kept narrower north/south streets, service paths and gate-to-field continuation.
- Quieted and world-aligned the existing grass material, added soil aprons, softer paving edges, shallow side drainage, root soil and traffic wear. Relocated the existing Registrar/Quest Board, Artisan, Housing Keeper and Gatekeeper to their actual facilities, preserving their interactions.
- Added reusable directional slash ribbons/contact highlights and ground-projected dodge dust. Kept the existing base skills, single-layer Nodes, saves and campaign progression. Bumped scripts and service-worker cache to v27.
- Local validation: 42 pure tests; 45 browser checks across the smoke run and focused corrected stride/registration reruns; 10 actual Node gameplay checks; nine fresh-Warrior Golden town checks with four viewport captures; six fresh-Ranger expedition checks through all rooms, boss phases/reward, crafting and reload. All final checks had no runtime/resource errors. The stride gallery now isolates artwork from gradient-shadow rasterization while retaining its original seven/eight/eight distinct-frame requirement.
- Environment restarted during completion; the modified checkout and QA artifacts survived and were re-inspected. Public Pages requests remain denied by the proxy (HTTP 403 / ERR_TUNNEL_CONNECTION_FAILED). GitHub repository/Actions access is available. Local QA and deployment do not confer either art approval.

## Apply Ragnarok reference techniques in the live client — 2026-10-01 / v28

- Resumed from clean `525272a`, verified recent commits/current source, served and played the actual game in Chromium, and attempted public Pages browsing. This pass implements the source-based study rather than stopping at documentation.
- Aligned the shared ground projection with painted foundation planes. Town and outdoor/dungeon materials, road widths, inverse input, depth sorting, sprite view selection and effects use the same basis. Retained the fixed camera, responsive zoom and existing city footprint.
- Reduced the competing northern civic frontage using the existing shop artwork. Added shared source records for four existing door landings, quieter court value/border/meeting rings, clipped wear and occupied-volume contact shadows. Moved existing planting off steps/streets, separated service standing space and nearby labels, placed both existing guards at the gate and made service NPCs turn toward nearby players.
- Repaired residence art/footprint/service placement and southern/shrine routes together. Added full-width road-clearance coverage with humanoid padding; normal navigation alone no longer hides a street drawn through an obstacle.
- Added presentation-only foot-pivot weight, attack anticipation/contact/recovery, cast/dodge/hit feedback and even timing across seven accepted Warrior stride keys. Screen-space direction selection follows the camera; damage stays controlled by the world-space combat timeline. No new class, map, district, quest, building or decorative pack.
- Three generated rear-walk candidates failed identity/alternating-foot review and are excluded. Two shorter rear cycles and four-cardinal reactions remain explicit art limitations. Both Golden gates and content freeze remain in effect.
- Final local supporting checks so far: 44 pure checks; 44 smoke checks plus the corrected diagonal-dodge check; nine normal-input fresh-Warrior Golden town checks with four viewport captures; ten actual Node gameplay checks; repository-subpath loading/cache/state continuity. Final checks report no runtime/resource errors. The dodge test now samples its active/recovery frames instead of assuming Python round trips stay within a short animation. Expedition automation checks exposed ground before clicking waypoints so the revised camera cannot route a click into the HUD/minimap.
- The final six-check fresh-Ranger expedition passes through actual UI: field contract, one-time supplies, cleared camp rest/Node tuning, forest/shrine entrance, all four rooms and both guardian phases/three attacks, safe return, crafting and reload. No runtime/resource errors. Camp approach uses nearby movement plus E interaction so camera settling cannot cause an automated marker miss.
- Recorded a separate normal-input Warrior court video (movement, basic attack, skills and dodge) and serial desktop/portrait timing samples. Desktop remains below the 60 FPS target in this cloud software renderer; measured limits are recorded in PERFORMANCE.md. Public visual approval remains separate from functional QA.


## Saved-town continuation and native render resolution — 2026-10-05

- Continued branch `codex/world-pipeline-v3-proof` from the saved source64 pause; restored its missing native ground bake, then saved source65 architectural work. Twelve existing frontage envelopes now have larger splayed openings, recessed glazing and projecting sills. Roof-owned cross gables meet cut openings in the original curved roof planes. Related home/merchant/workshop finishes use existing original atlases.
- Preserved terrain, walkable floors, navigation, service/portal/presentation anchors, patrols and every solid's geometry. Both source65 corner and alpha-aware ground bakes are current; export parity and geometry-digest invalidation passed. Visible triangles decreased slightly to 231,062 while eight material batches were added.
- The user's blurry gameplay screenshot exposed the software renderer's forced 0.5 pixel ratio. Removed that silent reduction: software now renders at native CSS resolution, hardware uses at least 1× with screen density capped at 1.5×. Boot/page/service-worker revision66 consistently loads the correction.
- Added portable Linux/Windows browser QA, individual Node test reporting and fresh-context service-worker/offline-save checks. All 95 registered Node checks and public schemas passed. Review evidence and scoped browser/performance outcomes are in `docs/review/wayfarer-v65/`.
- Town and locomotion remain unaccepted. No replacement character art or cosmetics were installed; painted contact/anatomy defects and broader town composition/density remain open. Cloud software performance cannot certify physical devices.

## RO3 exterior detail, original texture and daylight pass — 2026-10-05

- Continued saved source65 against all ten local `RO3 Ref/` presentation images. Source67 adds layered eave trim, rafter ends, ridge caps, side joinery, sills/shutter louvers and dressed-stone entrances on twelve frontages; twenty-two other existing lots gain wall framing. Existing footprint, floor, collision, service/portal and patrol contracts are preserved.
- Generated an original four-material diffuse atlas and retained its PNG master/provenance. Runtime WebP is a lossless encoding. The actual 1254² source has four 627² tiles; quality improvement comes from the painting, slope-aware roof UVs and palette-relative texture contrast, not increased source pixel count. No proprietary reference pixels were copied.
- Exported source-owned warm sun/cool ambient tones; strengthened 16-ray corner contact AO and raised the alpha-aware native floor bake to 1536². Both source67 bakes and saved export parity are current. Runtime uses the actual bake resolution and keeps native software gameplay pixels.
- QA caught lower stone door trim extending beyond the existing .18-unit collision margin. Narrowed it and rebaked; every new low vertex now lies in the source65 blocked region under the 2.3-unit body-height assumption. Geometry grows +5.71% to 244,256 visible triangles; 61 visible materials remain. These costs do not imply an FPS improvement.
- All 95 individual Node checks, public schemas and native source/export parity pass. Matched stills and final scoped browser/cache/performance results are recorded in `docs/review/wayfarer-v67/`. Town and locomotion remain unaccepted; character art and cosmetics were not changed.
