# World pipeline v3 — local review candidate

This pass integrates the supplied master pipeline and research guidance into
[the master plan](../../../MASTER_PLAN.md). Canvas2D remains the browser renderer.
No Ragnarok assets, maps, proprietary content or new engine dependency are included.
Golden Town and Golden Character approval remain open; content expansion is paused.

## Review entries

- `proof.html`: limited structural scene, real pillar passage, separate overhead
  layers, persistent cast/contact shadows and original painted Warrior.
- `index.html?world=court-v3`: current painted game using the native court manifest.
  Default `index.html` retains the legacy data path during review.
- `authoring/golden-proof.blend` and `authoring/wayfarer-court.blend`: editable source.
  Edited placement parents move presentation, occupied volume and linked forecourt.

The court importer preserves 45 existing object placements and 10 existing occupied
rectangles. It imports roads/plaza/forecourts and existing art references. Visual-only
props gain no inferred collision. NPCs, walkers and some art masks remain legacy
consumers; the import is not a completed town rebuild. Do not move services or make
this path the default before their references and traversal review are migrated.
Court mass heights are approximate blockout values; painted buildings retain their
current rendering. These masses are not reviewed roof, elevation or lighting geometry.

The proof uses one shared native contract for geometry, collision, navigation,
overhead regions, shadows, light sources and portal approaches. The two pillars
are solid; the span is overhead. Roof/canopy alpha changes do not alter shadow
volumes or fade walls/trunk. Actor and parts share projected ground-depth sorting.
This is a fixed-camera Canvas solution, not general multi-level 3D depth/navigation.

Walk, run and sprint have separate 8-direction/8-phase atlases, contact duties,
cycle distances, lift and body-pitch strategies. Timing, anchors, contacts, events
and attachments are recorded in the native manifest. Larger 256-pixel frame cells
protect sprint boot/weapon margins. Only the proof uses these new clips; existing
combat and mainline class presentation remain intact pending character review.

## Evidence

| Check | Result |
|---|---|
| Existing motion/combat/registration tests | 47 passed |
| Spatial/import/locomotion contract tests | 12 passed |
| Four public JSON schemas | Both world exports and animation data validated |
| Default game browser suite | 46 passed; no runtime/resource errors |
| Native court browser suite | 46 passed; no runtime/resource errors |
| Native court full service/gate/field review | 9 passed across desktop/phone/tablet views |
| Proof traversal/visibility/contact/responsive scenarios | 6 passed; 96 direction/contact samples |
| Saved Blender export parity | Both sources reproduced their JSON |
| Parent-transform propagation | Placement, solid and forecourt moved together |
| Inspector exit/input focus | Movement facing and camera-relative keys restored |
| Offline first visit | Precached proof and native court loaded; saved character retained |

[Proof video](video/proof-traversal-and-contact.webm) records actual traversal and
the contact scrubber. Screenshots include
[the painted import](images/painted-native-court.png),
[roof visibility](images/roof-selective.png),
[canopy approach](images/canopy-approach.png),
[shared geometry](images/shared-geometry-overlays.png), and
[manifest anchors](images/contact-anchors.png).

The proof report's performance sample has all debug overlays enabled. Use
`isolated-performance.json` for the separate normal/debug sample after caching
static overlay drawing. Both are cloud/headless
measurements, not physical-phone or public deployment approval.
The isolated sample recorded a 16.7 ms median and 16.8 ms p95 in both normal play
and with all four cached debug overlays enabled (180 frames per mode).

## Reproduce

Serve the repository with a static HTTP server. Browser QA requires Python
Playwright and Chromium; video recording also requires Playwright's ffmpeg runtime.
Blender and jsonschema are authoring/validation dependencies, not player downloads.

```sh
node --test tests/motion.test.cjs tests/golden_pipeline.test.cjs
node tests/world_v3.test.cjs
python3 tools/validate-world-v3.py
blender -b authoring/golden-proof.blend --python tools/check-blender-export-v3.py
blender -b authoring/wayfarer-court.blend --python tools/check-blender-export-v3.py
python3 tests/browser_smoke.py --url http://127.0.0.1:8010
python3 tests/browser_smoke.py --url http://127.0.0.1:8010 --world court-v3
python3 tests/golden_scene.py --url http://127.0.0.1:8010 --world court-v3
python3 tests/world_v3_browser.py --url http://127.0.0.1:8010
python3 tests/world_v3_performance.py --url http://127.0.0.1:8010
```

Use `tools/export-world-v3.py` on an edited saved Blender file. The builder scripts
create the initial fixtures and should not replace edited source files. Rebuild
Warrior review clips with `python3 tools/build-locomotion-v3.py`.

Public publishing was not performed. Local verification does not close either
Golden approval or demonstrate public deployment/mobile hardware performance.
