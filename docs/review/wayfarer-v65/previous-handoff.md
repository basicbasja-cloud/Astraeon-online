# ASTRAEON paused checkpoint — 2026-10-04

## Pause instruction and repository

The user requested: pause all development, write a detailed handoff, push everything to Git, then shut down the computer. This is a preservation checkpoint, not completion. Do not resume development until the user requests rework/continuation.

Workspace: `C:/Users/Lenovo/Bas/Astra online`. Origin: `https://github.com/basicbasja-cloud/Astraeon-online.git`. Branch: `codex/world-pipeline-v3-proof`. Previous pushed checkpoint: `e5a132176c5634eb44369927a4226b6b6a2108ea` (v47). The commit containing this document preserves subsequent work through saved source64; its ID is available in Git history.

**Town acceptance=false. Locomotion acceptance=false. Cosmetics implemented=false.** The latest user rejected the dashboard because characters still slide and shift position, and rejected the town as flat, lifeless and below RO3 quality. Technical checks never override this rejection.

Authoritative pause metadata: `docs/review/pause-2026-10-04/summary.json`. That directory preserves current logs, source63 screenshots and all raw gait captures. `docs/review/wayfarer-v49/` is historical62 evidence. The superseded handoff is preserved as `docs/review/pause-2026-10-04/previous-handoff-history.md`; conflicting versions/next steps in that history do not apply.

## Requirements and reference authority

1. Approved `concept art.png` controls original ASTRAEON identity, macro layout, districts, landmark hierarchy and architecture design/depth/placement, including waterfalls. Consortium Hall must be massive relative to people. Translate the artwork into playable terraces and a town above water.
2. Local `RO3 Ref/` screenshots are the TOP presentation comparison for camera, rendering, directional sunlight, cast/contact shade, cohesive painterly materials, clear streets, density, props and roof/façade balance. Aim for Prontera-like person-relative travel and scale. Preserve original ASTRAEON IP; no literal Prontera reconstruction or imported proprietary models/sprites/texture pixels. Low-resolution references are not the output-resolution target.
3. Correct grounded full-body animation anatomy, size, frame mapping, anchors and timing/speed relationship. Simple RO1-like walking is acceptable. Town work precedes further character replacement. Future interchangeable original costumes/skins, hats and wings are requested; cosmetic shop, ownership and payment systems are not implemented.

Prioritize strong architectural silhouettes/deeper façades/roof massing/building-family identity, broad clean painterly color/value variation, directional lighting/contact grounding, functional dense frontage dressing and smoothly blended edges. Sharper/noisier textures alone do not satisfy the request. Judge actual gameplay screenshots and normal-speed movement.

References and limits:

- All ten local `RO3 Ref/` images were inspected: gates, houses, merchant crossroads, statue/fountain courts, civic portal, residential bays and avenues. They do not establish native texture dimensions or animation FPS.
- Supplied tour: `https://www.youtube.com/watch?v=RZ06YmcbxkU` (NunuSaPunso, 5:18, RO3 Beta Prontera City). Selected views0:30–4:46 and quarter-speed/frame advances around1:35–1:36 were inspected; latest revisit paused1:49. Deep roofs, warm sun/cool shade, paved streets and coherent body/cape travel are visible. Robes obscure exact contacts. No claim of full-video frame analysis or inferred native FPS. No video downloaded.
- `https://rathena.org/board/files/file/3563-prontera-small/`: live author page Cloudflare-blocked. Indexed metadata only; actual map and author screenshot were not inspected/downloaded.
- `research/prontera-scale-reference.json`: public rAthena revision `e985006171d2eb320ee512a653f4c83aea3d81b6`,312×392 navigation cells. Not an ASTRAEON world-unit conversion or direct-copy directive.
- Newly supplied `https://ragnarokresearchlab.github.io/rendering/animation-systems/#sprite-animations` was read. It describes experimental24ms ACT intervals versus traditional25ms estimates, stretched timings and60Hz quantization. Its internal-clock/state-machine explanation is a hypothesis. An ACT interval is not necessarily one pose. Blindly assigning our distance-driven poses24ms will not repair painted contacts.
- ACT anchor/layer documentation: `https://ragnarokresearchlab.github.io/file-formats/act/`. roBrowserLegacy distance cadence uses its own coordinate units. ActEditor is a useful mature layer/anchor/garment reference, not installed. Additional research and the proposed cosmetics contract are in `research/character-locomotion-and-cosmetics.md`.

## Exact saved state — outstanding bake and checks

Authoritative native source: `authoring/wayfarer-spatial.blend`; export: `world/v3/wayfarer-spatial.json`; layout `wayfarer-concept-terraced-town-v49`.

- Last saved/exported source pass: **64**,119objects.
- `boot.js`/`index.html` cache **63**, `sw.js` cache **62**. Mismatch recorded; not repaired during pause. Update consistently after finishing artifacts on resume.
- Corner bake64 completed: **387637corners /9869meshes /14.7seconds**. It was already running when pause arrived and finished its existing save/export operation.
- Last ground-shadow bake **63**,1024²,615909land/326015shadowed pixels,69.6seconds. Historical filename `assets/wayfarer-ground-shadow-v54.png` retained.
- **Current export contains no `lighting.groundShadow`.** Flora64 changed geometry; exporter correctly invalidated the stale63 ground bake. No64 ground bake was started. Re-bake current geometry on resume; never restore stale63 metadata just to show shadows.
- Lighting sun.72/coolambient.36/castvector(.62,-.40).
- No64 gameplay, schemas, saved-source parity or performance review was performed. Do not describe64 as visually verified.

File sizes/SHA256 are in the pause summary. Current blend8,962,171bytes; export27,240,670bytes. Never reconstruct by rerunning historical builders or the one-time migration. Source save/export operations must be sequential.

## Town changes preserved

Earlier saved passes48–62:

- Hall X1.8/Y1.12/Z2.0 about entrance datum plus civic terrace; recessed/open portal, rose/lancets, pierced side bays, nave/aisles, unequal towers, ribbed crowned dome and flying buttresses. Bounds approximatelyX38.52–69.48/Y8.638–28.1675/Z.7925–41.8925, about17 nominal hero heights. Crown can clip in close gameplay framing; composition remains open.
- Original inn/shrine/forge families and twelve frontage groups with attached wings, projecting upper floors, dormers/oriels, shutters, porches and chimneys. Pass59 repaired24 erroneous full-depth timber corner slabs into actual posts and added48 recessed side windows. Pass62 added12 open attic bays, recessed glazing, structural fan braces and roof crowns.
- Continuous paved interior with unequal flagstones; civic terrace+1.4, retaining walls/coping and three eight-tread.175 flights. Road/entry/native-floor/actor/camera contacts agree in source.
- Joined river-bank strata below water-6.696, submerged talus, three masonry scuppers with original SVG cascade/foam and enlarged celestial fountain with volumetric draped figure/halo/feather layers.
- Ninety-four existing road segments use quieter original avenue paving.608 real alpha-tested leaf cards cast in native offline shadows. Joined114-section field grass/earth/rock shore blends below water; approach repair, not map expansion.
- Ten closed civilian patrols replanned against native lots. Seventeen NPC role appearances select Warrior/Mage/Ranger independently of service kind; reuse, not new citizen art or completed MMO life.
- Current-sprite alpha cast shadows project onto native floors with contact disks/land clipping. Loading warms fade materials. Offline floor bake uses actual building triangles/openings/overhangs and foliage alpha rather than opaque broad boxes.

**Pass63 market:** `tools/author-market-court-v63.py` saved an irregular+.72 merchant terrace, floor+.045, outline[(73,55),(98.5,55),(100.5,58),(100.5,76),(88,79),(73,79)]. Six complete placement roots and nearby props follow the raised floor. Four six-tread.12 flights, retaining walls/coping/pilasters and access gaps. Four existing stall counter lots retained; old plain roofs/goods hidden as references. Six original draped cloth canopy assemblies with curved valances, trusses/braces and stocked trays/textiles/pottery/produce; two new trader counters and four bench/urn/plant ensembles. Ten patrols replanned/applied. Both63 corner and ground bakes completed.

Market flight upper→lower centers: westnorth(73,59)→(70.6,59), width4; westsouth(73,67)→(70.6,67),width4; north(88.5,55)→(88.5,52.6),width4; south(79,79)→(79,81.4),width6.

**Pass64 flora:** `tools/ground-street-flora-v64.py` moves310 whole original stem/petal groups previously floating.4–1+units above paving to highest native walkable floor at group centroid. Minimum stem floor+.20, stored baseline and relative geometry retained. Rooted soil mound and six broad leaves per group. No runtime height patch, image editing or new collision. Source/export and corner64 saved; ground64/visual review outstanding.

Remaining town defects: simplified/blocky architecture, inadequate façade/roof nuance/family identity, monotony/sparse areas, density/life below RO3, and insufficiently convincing depth/composition. Terraces/flowers are partial work, not acceptance. Reassess structure against concept and RO3 instead of accumulating detail on an inadequate layout.

## Locomotion diagnosis and runtime repair

All72 ordinary-input cases captured: Warrior/Mage/Ranger ×walk/run/sprint ×eight headings. Every selected pose change and RAF recorded, with actual sprite crops, timelines, raw video, normal/quarter-speed GIFs. Nine actual0..7..0 sheets inspected. No observed skipped selected columns, Warrior phase mismatches or held rendered roots. **This does not validate anatomy, painted contacts, pelvis or body registration.**

- Warrior shipped strips: eight directions/eight poses/320-square slots, declared root(160,264),height176. Cycle distances1.05/1.8/2.3, speeds1.3/2.7/4.1; approximately101/83.3/70.1ms per pose before60Hz quantization. Walk repeats one leading leg; north pose0 two swords; east run/sprint weapon flips at7; southwest sprint crouches/hops.
- Mage/Ranger reuse one eight-pose walk atlas for all modes, variable unregistered tight crops/smaller silhouette, frame heights155–162. Cycle distance2.1allmodes, speeds1.3/3.5/4.6. Walk~200ms/pose,run66.7–83.2,sprint50. No measured painted-contact calibration; Ranger north is not convincing rear art.
- Start/stop simulation states have no authored startup/settle. Immediate eight-view changes expose mismatched drawings. Runtime phase/displacement agreement cannot prove planted stance feet.
- Existing `tools/register-painted-locomotion.py` centers each frame using detected head centroid, per-row median bottom and clip scale. It can shift bodies despite fixed declared roots and unconditionally writes production assets/manifest. Do not reuse unchanged for the shared-source-root pipeline.

Confirmed61 repair in `world/v3/locomotion.js`: `setStrategy` previously bypassed the contact queue. Now changes wait for the next exact.0/.5cycle contact, with old-distance travel through contact and leftover travel under the new stride split correctly. Stationary/start exceptions explicit; debug transition exposed.19 targeted tests cover all six changes at30/60/120Hz plus cancellation/stationary. Actual ordinary-input switches occurred at gait21/21.5/22.5. Timing repair only; no production character art replaced.

Required pipeline: approved original in-game seed → entire coherent full-body action strip → one shared scale/bottom-center/root → actual feet/body/weapon/silhouette checks → normal/slow GIF/video inspecting every transition → integration only after acceptance. No unrelated individual frames, procedural legs beneath a static torso, per-pose head/boot centering, interpolation/blur/faster playback/camera tricks to hide defects.

Each walk/run/sprint requires exactly two legs, stable proportions/costume/weapon/scale/root, correct alternating contacts, coherent torso/arms, no inappropriate hopping/pelvis jumps, smooth closure and measured stance travel matching world displacement. Future cosmetics should use body-owned pose clocks and registered head/back/hand attachments; planned, not implemented.

## Held/rejected studies — do not auto-install

- v50 full-body native/painted: rejected low pelvis/half-squat walking. Mathematical contacts do not approve art.
- v51 upright native rig: fixed legs.57+.57/arms.32+.30, heel/sole/toe roll/full-body hip/arms/cape,80keys+closure, duty.62/cycle1.129032258064516; support knee18.93–28.06degrees/contacterror~1e-7. Coarse/toylike, below illustrated seed quality.
- v52 all-eight guides: gameplay pitch46/ortho3.3/384-square/sharedroot~(192,291.425), evaluated body/feet points in `facing-registration.json`. PaintedS/E feet differ~2–24px. Other six painted directions, separate run/sprint and Mage/Ranger remain unfinished.
- `authoring/characters/held-material-atlas-v53/`: original generated material study/provenance, unapplied/uninstalled.
- `authoring/characters/warrior-painted-v63/E/`: one coherent eight-body4×2 imagegen strip from approved seed/full native guide. Raw1774×887RGBA normalized with one whole-canvas transform to1536×768; eight slots/GIF/metadata preserved. Alternation improves but painted soles diverge from guide and boot/body shapes vary. **Held/unapproved/uninstalled.** Contact annotations are native targets, not measured painted contacts. Separate native-guide comparison preserved. No other63direction/modes generated.

Presence in Git does not approve production use.

## Evidence and scoped verification

- `docs/review/locomotion-v61/`:72-case diagnosis, nine actual gameplay sheets and selected normal/slow previews.
- `docs/review/pause-2026-10-04/archives/`: all raw60gait/61transition captures in13 independent ZIPs with SHA256/byte/file-count manifest. Extract all parts into the same directory; do not concatenate. Dashboard HTML preserved; see README.
- Pause folder contains source63 market/residential/plaza screenshots/view report and63authoring/bake/test logs plus64flora/corner logs. **No64 screenshot review.**
- Source63:94Node passed before one new market-contact test. Focused seven-test file then passed including new test; full suite would total95 but was not rerun after addition. Public schemasPASS63. Market flights verified monotonic≤.15steps/clear contacts/retaining blockers/counter-floor alignment.
- Source63 three actual views atzoom160/yaw25/pitch46 reviewed, runtime/resourceerrors[]. Still below visual acceptance. No new full normal-input stair/service route review or isolated performance.
- Last source/export parity/Hall transform/stale-bake invalidation check62. Last isolated sound-on desktop62:60.0015FPS/p9516.8ms/max17.7ms/root holds0/errors[]. Last normal-input13stairs/gates plus field/save59. These historical checks do not certify changed63/64geometry or other devices.
- Source64: saved/exported flora and corner bake only. Ground bake, parity/schemas/full tests/routes/views/isolated performance remain required on resume.

## Resume sequence — only after user continuation

1. Read current handoff/pause summary/steering, inspect concept/RO3 refs and rejected gait evidence. Preserve user save/progression.
2. Reopen saved native source. Re-bake64 ground shadows using actual original foliage alpha, update cache versions consistently, verify export/geometry digest. Never attach stale63metadata.
3. Run parity/schemas/six relevant Node files. Review actual64 gameplay and normal-input market/civic stairs, services/patrols/gates/field/save. Isolated performance after heavy jobs finish.
4. Rework town first: person-relative street/building scale, Hall silhouette, façade depth/roof massing, functional density, tiered composition, painterly materials/light/shadow. Do not promote current checkpoint.
5. Then repair full-body animation and production registration using diagnosis/ResearchLab timing/anchors. Measure actual painted contacts/body drift/closure. Kinematically valid but stylistically inadequate guides are not production replacements. Validate all characters/headings/modes at normal speed.
6. Cosmetic attachment/ownership work waits for stable original body animation. No payment/feature implementation is authorized by this pause.

## Tools and restart

No npm/build step. Previous preview `http://127.0.0.1:8011/`; diagnostic `http://127.0.0.1:8012/locomotion-dashboard.html` from `C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation`. Shutdown ends servers/tool sessions; their IDs cannot resume. Recreate loopback-only servers after reboot as needed:

```powershell
& 'C:/Python314/python.exe' -m http.server 8011 --bind 127.0.0.1 --directory 'C:/Users/Lenovo/Bas/Astra online'
# Separate terminal, after extracting captures and copying dashboard HTML:
& 'C:/Python314/python.exe' -m http.server 8012 --bind 127.0.0.1 --directory '<extracted diagnostic root>'
```

Blender4.3GUI locally fails SideBySide; official bpy4.3 works with bundledPython3.11:

```powershell
$env:PYTHONPATH='C:/Users/Lenovo/AppData/Local/AstraeonTools/bpy43'
& 'C:/Users/Lenovo/AppData/Local/AstraeonTools/blender-4.3.2-windows-x64/4.3/python/bin/python.exe' tools/run-bpy-task.py authoring/wayfarer-spatial.blend tools/<task>.py
```

Corner bake `tools/bake-town-depth-v48.py`. Ground bake: `tools/prepare-shadow-alpha.py --output <cache.json>`, set `ASTRAEON_SHADOW_ALPHA_CACHE`, then `tools/bake-ground-shadows-v54.py` (saves PNG/source/export). Mutations/save/export sequential; never concurrent with performance. Replan/apply patrols when lots/contacts change. `tools/check-blender-export-v3.py` moves Hall in RAM without saving; deliberate stale-bake diagnostic expected. Schemas `tools/validate-world-v3.py`.

Node files: `tests/motion.test.cjs`, `world_v3.test.cjs`, `painted_locomotion.test.cjs`, `golden_pipeline.test.cjs`, `expanded_town.test.cjs`, `locomotion-transitions.test.cjs`. Actual views `tools/capture-wayfarer-views.py`. Ordinary-input `tests/golden_wayfarer.py` spatial/services/motion with motion-series/video/archetype. Isolated sound-on `tests/movement_performance.py`. Sprite tools `audit-shipped-sprites.py`, `analyze-locomotion-capture.py`, `locomotion-review-sheets.py` under tools.

QA Python `C:/Python314/python.exe`; Chrome `C:/Program Files/Google/Chrome/Application/chrome.exe` via `ASTRAEON_BROWSER`, hardwareD3D11/Radeon780M. Do not run `save-review-checkpoint-v62.py` against64: hardcoded version would mislabel evidence.

Camera15degree lens/46downpitch/yaw0/defaultzoom125/control65–325; source63views160/yaw25. World112×128/paved~89×85/nominalWarrior2.421world units tall. Not proprietary Prontera units; map-cell counts cannot be directly equated.

No new plugins installed. Sprite-pipeline/imagegen/game-playtest/Three.js guidance used; built-in imagegen raster generation/editing, Python authorized normalization/crop/read-only QA. No subagents authorized; no active goal. User explicitly authorizes pushing all repo changes including references and held studies. Preserve save/progression and unrelated apps/files.

After successful push/remote verification, shut down as requested without forced app termination. Until a new user instruction, remain paused.
