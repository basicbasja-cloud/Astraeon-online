# Wayfarer regional capital — source75 evidence

The active capital expands and reorganizes the same Wayfarer town. Its original
royal geometric blueprint uses the Hall–fountain axis, formal civic precincts,
ordered neighborhoods and four gates. Prontera informs street hierarchy and
block placement; the original concept supplies the architectural theme. All ten
RO3 references remain the hard visual target.

## Current native implementation

- 172 complete homes: 37 preserved original assemblies and 135 detailed additions;
  97 homes in the inner neighborhoods, with a median visible envelope gap of .80
  world units.
- Public cross streets 8 world units, district streets 9, perimeter circuit 10;
  ceremonial avenues 14/12. Five redundant through lanes are removed.
- Ten complete building frontages face the fountain square. Three neighboring
  assemblies shift for clearance; their doors, awnings and exterior accessories
  move together. One existing local resident walks the square perimeter.
- Artisans’ Court has three inward-facing frontages, a shared well, craft tables,
  noticeboard, benches and planting. Willow Court has four inward-facing frontages,
  a well and planted seating. Side passages connect both courts to public streets.
- Original Hall plus Council Chambers, Grand Archive and Trade Exchange; 78 trees,
  28 residents, both original field destinations and all eight original services.
- Shared private paving enclosed by 42 closed curb loops across 40 owned blocks;
  continuous irregular public stone with no public/private overlap. Water, cliff
  courses, curtain walls and foundations use the city’s material quality.

Authority is `authoring/wayfarer-spatial.blend`, with matching export
`world/v3/wayfarer-spatial.json`. Export SHA256:
`a4933847937f633ef9a27751c9ca306f3684f1b41f24b42409e8e5d382397850`.
`plan.json` and `native-plan.json` record the reviewed planning and native derived
geometry. `blueprint.png` is a planning map, not a gameplay screenshot.

Implementation checkpoint: [`2466611`](https://github.com/basicbasja-cloud/Astraeon-online/commit/246661150bc4f08108b6103677f56f46833e3907), pushed to `codex/world-pipeline-v3-proof`.

## Verification index

| Evidence | What it establishes |
| --- | --- |
| `assembly-and-floor-parity.json` | 280,145 original transformed vertices and 211,953 UV faces retained; zero paving overlap; grounded trees; correct public widths, court/plaza orientations and shoreline/curb normals |
| `density-review.json` | Visible model envelopes, shared blocks and current density |
| `traversal-final.json` | All 26 destinations reachable and all 28 entire patrol loops clear |
| `architecture-bake-wide.log`, `foliage-bake-wide.log`, `floor-bake-wide.log` | Full lighting refreshed after the final plaza changes; original foliage alpha and native 4096² ground atlas |
| `native-parity.log` | Saved native/export parity, shared Hall transform propagation and stale-bake invalidation |
| `node-final/report.json`, `schema.log` | 96 individual checks pass across six files; four public schemas pass |
| `native-streets/views.json` | Four current native street views; culling versus exhaustive rendering differs by zero pixels |
| `native-courts/`, `native-civic/`, `native-shore/`, `native-districts/` | Current rendered court, civic, perimeter and plaza inspection; manifests record source digest, camera, resolution and errors |
| `services/` | Ordinary keyboard/click input through eight services and ten neighborhood/court/plaza stops, field travel and save reload |
| `cache/` | Cache82, saved-character migration and actual offline reload |
| `performance.json` | Isolated sound-on native-resolution measurement against the unchanged gate |

The last browser stages are running; their completed reports, images and actual
performance result are required before marking them verified. Read
`ro3-review.md` for the visual findings and `reference-scale-study.md` for the
per-reference scale/placement study. Structural checks establish geometry and
playability, not final artistic acceptance.

Current street comparison images use native 1280 × 800 screenshots with a
1280 × 666 playfield, pixel ratio1, zoom160/yaw25/pitch46. Wide court/civic/shore
captures specify their cameras separately. Ordinary traversal retains the
unchanged default gameplay camera and uses normal Shift sprint input; it does
not teleport the review character. Capture fixtures are visual inspection only.

## Historical diagnostics

`before-density/` contains the initial 136-home draft;
`diagnostics/density-geometry/` the intermediate 140-home gap patch;
`diagnostics/narrow172/` the rejected 4–5-unit street revision. Rejected annex and
organic plans are also retained as history. Earlier `*-final.log` bake records
precede the current `*-wide.log` bakes. None replaces current-source evidence.

This cloud environment uses SwiftShader and has no physical GPU. Report its
actual result without lowering resolution or weakening FPS/frame-time and
moving-frame thresholds. Physical-device performance and overall Golden/RO3
acceptance remain open; existing Warrior artwork acceptance is separate.

The actual-door audit found one retained infill home whose model front differed
from its placement heading. Its whole assembly rotates clockwise to face the
square and shifts .4 world units for roof clearance. Original indexed shape and
UVs remain. `frontageOffset` records that model’s geometric front, and the source
check verifies all ten actual door-plane directions. Final lighting and saved native/export parity pass. Browser
evidence is being captured for this corrected source. The first checkpoint’s
views are historical in `diagnostics/pre-entry-correction/`.
