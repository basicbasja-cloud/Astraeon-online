# ASTRAEON — regional capital source75

Updated 6 October 2026 (Asia/Bangkok). Work is authorized on
`codex/world-pipeline-v3-proof`; complete and push the existing branch.
No PR, merge or deployment is requested. The earlier source72 pause is historical.

## Current direction and source

Expand and reorganize the same Wayfarer town into one geometric regional capital.
Prontera informs scale, block placement and street hierarchy; Wayfarer retains
its own royal geometric blueprint. The latest steering rejects alley-width public streets.
The original concept supplies the theme, and all ten `RO3 Ref` images remain the
hard ultimate visual target. The user rejected both a separate old-town annex
and the subsequent irregular street plan, then requested royal impact, formal
geometry, substantial civic buildings and greater housing density.

Authority: `authoring/wayfarer-spatial.blend`; matching export:
`world/v3/wayfarer-spatial.json`. Active layout: `wayfarer-regional-capital-v75`,
256 × 288 world bounds, 54,848 square world units contiguous city land, 278 exported objects,
172 houses (37 original assemblies reorganized, 135 detailed component-built
additions), 78 trees and three new civic landmarks. The original Hall heads the
ceremonial axis; Council Chambers, Grand Archive and Trade Exchange support it.
Warm timber/plaster/clay housing retains the concept theme; civic stone, blue
roofs and gold establish the hierarchy. Four cardinal gates serve formal avenues.
Both original field destinations and all eight services retain their identities.
Actor art, gameplay pace, camera defaults and save semantics are unchanged.

The continuous floor correction is already pushed through `7b72b3f` (source74,
cache81). The expanded city retains world-space public irregular stone and closed
private rectangular paving, now clipped against actual streets, gardens and
raised contacts. There are 423 planned floor meshes and 42 closed curb boundary loops, plus the retained stairs and newly authored entrance contacts.
Native cliffs, waterline detail, defended walls and bridge foundations complete
the enlarged shoreline. Archived legacy meshes are excluded from export and bakes.

## Verification

Final export SHA256: `4faa2cb8c9cf3e84f9373adcaa35d61b092d3b47c8891a3be49ea746cd10ca75`.


Evidence: `docs/review/wayfarer-capital-v75/`.
The independent assembly/floor check passes: 280,145 original transformed
vertices and 211,953 UV faces preserved; zero public/private overlap; all 78 tree
roots grounded with .015-world-unit embed and clear of nonvegetation solids/avenues;
formal gardens do not overlap roads. All 904 cliff faces point outward and all
226 native waterline faces point upward; their vertices/UVs are retained. The
shared-block check finds 426 outward curb faces across 40 owned blocks. All
26 destinations and 28 complete patrols are reachable/clear. The current suite has 96 passing individual checks across six files, and four
public schemas pass.

The user clarified that smaller gaps alone were insufficient: characters must
walk through real neighborhoods matching the RO3 gameplay reference. The active
plan has continuous street-facing rows, paired frontages and shared back courts.
It reorganizes 163 complete movable modules into larger inhabited blocks,
keeping all 172 homes from the preceding draft. There are 97 homes in the inner neighborhoods (49 before), with
a median visible facade gap of .80 world units (3.84 world units before). All 37 original house
assemblies retain their indexed shape and UVs. RO3 Ref is the hard target for
street scale, density, curb placement, materials and overall visual quality.

Continuous owned-block paving and curbs define the walking-street edges;
individual island aprons are removed within the neighborhoods. Secondary roads
are at least 8 world units, district streets 9 and the circuit 10, with
ceremonial axes 14/12. Five redundant through lanes are removed. Eighteen local residents join
the original ten; per-frame actor budgets are unchanged. Geometry and all patrol routes pass on the final export. Full architecture,
original-alpha foliage and 4096² ground lighting have been rebaked after the
plaza changes, and saved native/export parity passes. Native
street/civic/perimeter views, ordinary service
and neighborhood walking, offline/save migration and current performance still
need to finish. Cache82 is an unpublished draft. Historical 136-home views are in
`before-density/`; the intermediate 140-home captures are diagnostic only.

Golden visual acceptance remains open. Cloud SwiftShader on two CPUs
cannot certify physical-GPU performance. The source74 performance gate failed;
the source75 result must be recorded without weakening the native-resolution,
FPS/frame-time or moving-frame gates. Existing Warrior painted-leg, weapon and
registration acceptance is also open and separate from this city pass.

## Safe continuation

Do not rerun the initial one-shot author or regenerate occupied lots. The reviewed
`plan.json` is the current planning authority; `blueprint.png` is a planning map,
not a gameplay capture. Edit that plan, derive native floor geometry with
`prepare-wayfarer-capital-geometry-v75.py`, then use the guarded native refiners.
`draw-wayfarer-capital-v75.py` redraws the existing reviewed lots. Rejected annex
and organic plans are diagnostic history and never the active source.

Offline Shapely 2.1.2 is at `/tmp/astraeon-curb-geometry`; set `PYTHONPATH` for
planners/checkers. Its ABI differs from Blender's Python: prepare geometry outside
Blender, then apply with the native companion. New decorative component joins
retain original component vertex groups; collision cores stay separate.

After geometry changes, run architecture, foliage and ground lighting serially
with Blender. Prepare original cutout alpha using `prepare-shadow-alpha.py`, then
set `ASTRAEON_SHADOW_ALPHA_CACHE` for foliage and floor bakes. Optional
`ASTRAEON_BAKE_COLLECTIONS` limits architecture receivers but still builds the BVH
from every active architectural caster. Use a full bake when changed casts can
affect neighboring receivers. Check saved native/export parity after baking.

Use one browser at a time. Start the local server with output redirected to a file
so an unread PTY cannot stall it. Review at 1280 × 800, scene 1280 × 666, ratio1,
zoom160/yaw25°/pitch46°; preserve default gameplay camera settings. Capture
fixtures are only for visual inspection; ordinary service/field verification uses
real keyboard/click input. `golden_wayfarer.py --travel-mode sprint` holds normal
Shift input during long journeys and does not alter simulation speed or tolerances.

Two owned inward-facing courts now give selected blocks their own purpose.
Artisans’ Court turns three complete homes/shops toward a shared well, craft
tables, noticeboard, benches and planting. Willow Court turns four frontages
toward a gathering well and planted seating. Main public widths remain 8–10
world units. Two existing local residents walk court routes; the total remains
28 and per-frame actor budgets are unchanged. Both courts are ordinary reachable
route destinations and are included in the service/neighborhood walking review.

The square now has ten complete nearby building frontages oriented toward the
fountain plaza, with doors, awnings and accessories moving together. Three
neighboring assemblies shift slightly to keep full visible gaps and street
clearance. Two edge homes join the square frontage; Artisans’ Court keeps three
inward-facing models and Willow Court keeps four. Trees and lamps are grounded
clear of the revised buildings, and one existing local resident walks the
square perimeter. Final lighting and saved native/export parity are complete. Playable evidence
is being captured for this latest native geometry.
