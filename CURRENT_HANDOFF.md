# ASTRAEON — regional capital source75

Updated 6 October 2026. Work is authorized on `codex/world-pipeline-v3-proof`:
continue and push verified checkpoints to the existing branch. No PR, merge or
deployment is requested. The earlier source72 pause is historical.

## Current city and latest request

Wayfarer is one reorganized geometric regional capital. Prontera informs scale,
block placement and street hierarchy; Wayfarer retains its own royal blueprint.
The original concept supplies the architectural theme. All ten RO3 references
remain the hard ultimate visual target.

The latest change turns ten complete frontages toward the fountain square.
Doors, awnings, accessories and entrance contacts move with their buildings.
Three neighboring assemblies shift for clearance, with two trees and two lamps
set back. One existing local resident walks the square perimeter. The actual-door
check exposed a legacy infill whose root heading differed from its geometric
front: its whole model now rotates clockwise and shifts .4 world units west.
`frontageOffset` records that legacy distinction, and all ten actual door planes
are independently verified against the intended plaza direction.

Artisans’ Court has three inward-facing frontages, a well, craft tables,
noticeboard, benches and planting. Willow Court has four inward-facing frontages,
a well and planted seating. Both connect through side passages to public streets;
two existing residents use local court loops.

Authority: `authoring/wayfarer-spatial.blend`; matching export:
`world/v3/wayfarer-spatial.json`, layout `wayfarer-regional-capital-v75`.
Final export SHA256:
`a4933847937f633ef9a27751c9ca306f3684f1b41f24b42409e8e5d382397850`.

- 256 × 288 bounds; 54,848 square world units contiguous land; 278 objects.
- 172 complete homes: 37 original assemblies and 135 detailed additions.
  There are 97 inner homes; median visible-envelope gap .80 world units.
- Public cross streets 8, district spines 9 and perimeter circuit 10 world units;
  ceremonial avenues 14/12. Five redundant through lanes are removed.
- Original Hall plus Council Chambers, Grand Archive and Trade Exchange;
  four gates, 78 trees and 28 residents. Actor art, pace, camera defaults,
  per-frame actor budgets, eight service identities and two field destinations
  remain authoritative.
- Continuous irregular public stone, shared rectangular private paving,
  423 planned floor meshes, 40 owned blocks and 42 closed curb loops.
  Native walls, cliff foundations, waterline and bridge approaches complete
  the perimeter. Legacy authoring references are excluded from export and bakes.

The preceding implementation checkpoint `2466611` is pushed. Its first rendered
sweep preceded the legacy entrance correction; those captures and their review
are archived in `docs/review/wayfarer-capital-v75/diagnostics/pre-entry-correction/`.
The source74 floor correction is pushed through `7b72b3f`.

## Verification and remaining review

Evidence is in `docs/review/wayfarer-capital-v75/`.

Current saved native/export parity passes, including an intentional unsaved Hall
transform and stale-bake invalidation. The independent source check preserves
280,145 original transformed vertices and 211,953 UV faces, with maximum error
5.56e-5. Public/private and garden/road overlap are zero; all 78 tree roots are
grounded with .015-unit embed and clear of solids/avenues. There are 904 outward
cliff faces, 226 upward waterline faces and 426 outward curb faces. All 26
destinations and 28 entire patrols are clear. All ten actual plaza door directions
pass. The current six-file suite has 96 individual passing checks; four public
schemas pass against this export.

Full architecture, original-alpha foliage and 4096² ground lighting are complete
after the actual entrance correction. Fresh plaza, district, court, street,
civic and shoreline captures are running on the immutable source. Ordinary
keyboard/click input through eight services and ten neighborhood/court/plaza
stops, field/save reload, cache82 migration/offline reload and isolated sound-on
performance follow. Do not mark these browser stages verified until their final
reports exist and their native images have been inspected.

Overall Golden/RO3 visual acceptance remains open. Cloud SwiftShader has no
physical GPU. Report its actual measurement without weakening the existing
native-resolution, FPS/frame-time or moving-frame gates. Existing Warrior
painted-leg, weapon and registration acceptance remains separate.

## Safe continuation

Do not rerun the initial one-shot author or regenerate occupied lots.
`plan.json` is the reviewed planning authority; `native-plan.json` is derived
native geometry. `blueprint.png` is a planning map, not a gameplay screenshot.
Use the guarded refiners for reviewed changes, regenerate native floor geometry
with `prepare-wayfarer-capital-geometry-v75.py`, and redraw existing lots with
`draw-wayfarer-capital-v75.py`. Preserve `frontageOffset` when changing the legacy
model; the actual door-plane check is required after plaza changes.

Offline Shapely 2.1.2 is at `/tmp/astraeon-curb-geometry`; set `PYTHONPATH` for
planners/checkers. Its ABI differs from Blender’s Python: derive geometry outside
Blender, then apply the native companion. Decorative joins retain component
vertex groups; collision cores stay separate.

After geometry changes, run architecture, foliage and ground lighting serially
with Blender. Prepare original cutout alpha with `prepare-shadow-alpha.py`, then
set `ASTRAEON_SHADOW_ALPHA_CACHE`. A limited architecture receiver bake still
needs all active casters; use a full bake if neighboring casts change. Check
saved native/export parity afterward.

Use one browser at a time and redirect the local server output to a file.
Browser execution in this cloud needs the network sandbox capability for
Chromium’s local sockets. Native street comparisons use 1280 × 800 screenshots,
1280 × 666 playfield, ratio1, zoom160/yaw25/pitch46; wide views declare their
own camera and viewport. Capture fixtures are visual inspection only.
`golden_wayfarer.py --phase services --neighborhoods --travel-mode sprint`
uses normal Shift input with unchanged simulation speed and arrival tolerance.
Older all/spatial/districts/market itineraries still contain source74 coordinates.
