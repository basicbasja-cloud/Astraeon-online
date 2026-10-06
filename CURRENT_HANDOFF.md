# ASTRAEON handoff — source72 paused at user request

Updated 2026-10-06. The user requested: “Please stop, all write a handoff and push all”.
Implementation has stopped. All current work is saved for continuation on
`codex/world-pipeline-v3-proof` in `/workspace/Astraeon-online`.
Origin: `https://github.com/basicbasja-cloud/Astraeon-online.git`.
Keep the existing localhost8011 development server alive (PID2201 at handoff).
No PR, deployment, merge or further implementation was requested.

## Saved native state

Authority: `authoring/wayfarer-spatial.blend`; saved export:
`world/v3/wayfarer-spatial.json`. Both completed the last patrol-author save.
Source72 versions cover blueprint, planting, contacts, profiles, stair fit,
ornament fit and patrol repairs. Cache is still78 in boot.js, sw.js and index.html.
The inherited layout ID remains `wayfarer-concept-terraced-town-v49`.
There are120 collections; world bounds remain112×128.

The latest requirement is a coherent town blueprint: closed curbs separate
building zones from public walking space, with curved plaza edges, a larger plaza
and symmetric cross approaches. Source71 clipped curb strips alone did not meet
this requirement; source72 replaces them with closed native boundaries.

- Rounded plaza bounds [40,43,68,62.5], center [54,52.75], radius3. Its footprint
  grows from324.915 to538.194 square meters (+65.64%); four planted civic islands
  are cut out of the actual paving. The whole fountain group follows its center.
- Four approaches are width8, with symmetric west/east and north/south lengths.
  Existing road centerlines and detailed lot aprons fit the revised public space.
- Seven native curb meshes represent nineteen logical closed building/civic
  outlines: three shared district blocks and four planted crest-post islands.
  Curbs are0.36m wide,0.20m high, with0.035m bevel and dark fascia. Entrance
  crossings stay continuous and smoothly grade flush, with0.0003m surface offset.
- Five whole house groups and five whole tree groups move into coherent frontage
  space. All37 ordinary houses retain exterior detail and dimensions. Tree count
  remains62 conifers plus two intentional broadleaf accents.
- Eighteen retaining-wall/coping/buttress parts widen the Hall stair opening;
  stair treads are unchanged. Four crest-post groups move south0.35m into paired
  planted islands. Old independent curbs, lot rims and roadside verges are retired.
- Twenty new soft curb-margin strips, four civic green islands,27 owned ground
  flower groups,308 foundation-grass strips/2464 clumps and160 mortar grass clumps
  fit the native floors and private boundaries. Flowers follow nearby house owners.
- Seven walker routes were repaired around the new boundaries. All10 walkers
  retain art/archetype/pace; final traversal passes every route and patrol.

Native RO3 references remain in `RO3 Ref/` (ten JPGs). Continue matching facade
relief, architecture, building density, fountain, aged textures, high-quality
curbs/trees, warm shading and planted edges. Public irregular stone should read
separately from rectangular building-lot brick. Avoid random polygon/PNG pads,
free-standing flower clusters and open curb ends. Retain native full resolution,
character scale/art/pace and detailed house accessories.
Warm lighting retained: ambient0.44, ambientColor[1.04,1,0.90], sunStrength0.65,
sunColor[1.18,1.05,0.79], cast[-0.42,0.55], angularRadius0.018, shadowColor#514d44.

## Verification and limitations

Evidence: `docs/review/wayfarer-v72/` (README, status, final plan, native extraction,
boundary report, authoring logs, patrol plan, traversal, tests and tree contacts).

Completed before stopping:
- Native topology/boundary check PASS: no open curb ends, public-path overlaps,
  curb/solid-volume overlaps or curb intersections; fountain centered.
- Direct world tests:20 pass,0 fail, including actual floor-face hole containment.
- Traversal:17 destinations reachable;10 patrols pass with no extra repair needed.
- Native patrol-author log confirms seven repairs saved and JSON exported.
- All64 trunk contacts measured. Five moved trees preserve prior floor offsets
  within0.00001m. Two large inherited offsets (plaza-oak-east-root and
  garden-v4-tree-7-trunk) need visual inspection; no acceptance implied.
- Four schemas passed on an earlier source72 snapshot, not the final patrol save.

Pending: final schemas, Blender/export parity, source72 architecture/foliage/floor
bakes, cache bump, native browser captures, ordinary services/cache checks and
isolated performance. The modified floor atlas is the completed source71 flower
bake; it is STALE for source72. Export deliberately omits stale groundShadow and
uses geometric fallback. Source71 logs are historical. No source72 visual pass,
user Golden acceptance or physical-GPU result exists. Source70 visual acceptance
was superseded by the user's curb-placement corrections. Earlier software-renderer
FPS failure is historical, not a source72 measurement. Do not lower resolution
or thresholds to call performance passed.

`native.json` predates only the patrol-route save; geometry is unchanged. Its
`actorAndNavigationMetadataPreserved` field checks navigation/spawn/safeSpawn/
route/districts, not walker routes. Seven patrol routes intentionally changed.

## Implementation notes for continuation

`world/v3/spatial.js` now uses actual indexed floor triangles for land outside
mainland instead of arbitrary vertex polygons; this preserves disconnected floor
bands and holes. `tools/bake-ground-shadows-v54.py` uses actual floor ray hits for
the same purpose, but has not run on source72. Original1536² resolution, eight sun
samples, four contact samples and cutout alpha remain. Exporter supports explicit
native centerline_json/road_width for triangulated roads.

Offline planner/checker uses Shapely2.1.2, currently installed only in
`/tmp/astraeon-curb-geometry`. If needed:

```sh
python3 -m pip install --target /tmp/astraeon-curb-geometry shapely==2.1.2
PYTHONPATH=/tmp/astraeon-curb-geometry python3 tools/check-ro3-blueprint-v72.py --native docs/review/wayfarer-v72/native.json --output /tmp/boundary-check-v72.json
```

Final plan is `docs/review/wayfarer-v72/blueprint.json`. Do NOT rerun the initial
one-shot `author-ro3-blueprint-v72.py` on current source72. Initial author,
planting/contact fitters and later reprofile are successive phases; reprofile
contains retaining-wall/civic-island fits and version guards against double moves.
Temporary pre72 baseline JSON/blend remain in `/tmp/astraeon-ro3-72/before.*`;
not duplicated in Git. If lost, reconstruct source71 from3b702c8 and the included
`author-ro3-public-planting-v71.py` in an isolated checkout for baseline comparisons.
Do not overwrite current authority. All native authoring tools are in `tools/`.

## Next authorized continuation (wait for the user to resume)

1. Check final schemas and Blender/export parity, review tree-contact outliers.
   Existing world tests/traversal pass; rerun after any new edits.
2. Bake architecture, THEN foliage, THEN floor shadows serially. Architecture
   changes civic-tree alpha; foliage must restore native foliage shading before
   the floor bake. Regenerate original alpha cache if temporary files are gone:

```sh
python3 tools/prepare-shadow-alpha.py --output /tmp/astraeon-ro3-72/composition-alpha.json
blender -b authoring/wayfarer-spatial.blend --python-exit-code 1 --python tools/bake-town-depth-v48.py
ASTRAEON_SHADOW_ALPHA_CACHE=/tmp/astraeon-ro3-72/composition-alpha.json blender -b authoring/wayfarer-spatial.blend --python-exit-code 1 --python tools/bake-ro3-foliage-v70.py
ASTRAEON_SHADOW_ALPHA_CACHE=/tmp/astraeon-ro3-72/composition-alpha.json blender -b authoring/wayfarer-spatial.blend --python-exit-code 1 --python tools/bake-ground-shadows-v54.py
```

3. Bump boot.js/sw.js/index.html cache78→79 together after stable bakes.
4. Capture native1280×800 HUD/1280×666 scene at1×, one browser, and compare all
   ten RO3 references. Inspect closed boundaries, court curves, facades, floor
   transitions, planting ownership and shadows across plaza, avenue, market,
   shop/home frontage, inn, Hall axis, shrine, residential and blacksmith:

```sh
python3 tools/capture-wayfarer-views.py --output docs/review/wayfarer-v72/native --views plaza,avenue,market,frontage-shop,frontage-home,inn,hall-axis,shrine,residential,blacksmith --zoom 160 --yaw 25 --pitch 46
python3 tests/golden_wayfarer.py --phase services --service-names 'Merchant,Artisan,Housing Keeper' --output docs/review/wayfarer-v72/services
python3 tests/cache_resume.py --output docs/review/wayfarer-v72/cache
python3 tests/movement_performance.py --startup-timeout-ms 120000 --output docs/review/wayfarer-v72/performance.json
```

5. Performance last, isolated: unchanged >55FPS, p95<25ms, max<80ms,
   >100 moving pairs and0 frozen, sound on, native resolution. Record software
   renderer limitations honestly; physical-GPU and user acceptance remain separate.
6. Commit and push each completed step as requested. Keep server8011 alive.
   Do not deploy, merge, create a PR or claim visual acceptance prematurely.
