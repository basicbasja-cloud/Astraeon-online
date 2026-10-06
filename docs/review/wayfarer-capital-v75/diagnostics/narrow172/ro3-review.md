# Source75 RO3 baseline review

All ten supplied RO3 screenshots are the hard visual reference. Prontera's map
informs capital scale and density; Wayfarer keeps its own geometric blueprint and
the original concept's architectural theme. A planning map or a passing geometry
check cannot substitute for the playable view.

## Review criteria

| Reference | Current views | Required result |
| --- | --- | --- |
| 04_08_00, 04_08_34 | street-west, street-east, street-borough | Closely spaced two-storey frontages on both sides; steep clay roofs, recessed openings, timber relief and useful exterior accessories |
| 04_08_07, 04_08_24 | street-artisan, plaza, avenue | Continuous irregular public stone, readable walking space, coherent warm casts and enclosing frontage |
| 04_08_39, 04_08_45 | market, blacksmith, inn | Shop-facing accessories, distinct private paving, grounded foundations and green edges |
| 04_08_14, 04_08_30 | hall-axis, council, archive, exchange | Royal hierarchy, detailed civic stonework, formal planting and clear approaches |
| 04_08_20 | plaza | Tiered turquoise fountain, four owned planted corners, benches and symmetric connections |
| 04_07_07 | gate, bank-east | Defended gate, bridge and water/cliff/wall foundations with the city's material quality |

Inspect continuous curbs around inhabited blocks, accessible entrances, side
passages, shared back courts, grounded planting, floor seams and shadow continuity
in every street view. Secondary streets should feel inhabited at the unchanged
person scale; the ceremonial avenues and civic courts deliberately remain broader.

Standard comparison captures use native 1280 × 800 screenshots, a 1280 × 666
playfield at pixel ratio 1, and ordinary camera controls at zoom160/yaw25/pitch46.
Separate wide civic/shoreline captures identify their camera and viewport in their
manifests. Visual fixtures place an isolated review character; service and
neighborhood traversal evidence uses ordinary input without save teleports.

## Current verification boundary

Source geometry has 172 houses, 118 in inner neighborhoods, with a median visible
building gap of .80 m. All 37 original assemblies retain their shapes and UVs.
Shared inhabited blocks have continuous paving and outward curb faces. All 24
destinations and 28 complete resident patrols are clear. These checks support the
visual review; they do not certify it.

Final native screenshots and ordinary walking evidence are being inspected.
RO3 visual acceptance, Warrior artwork acceptance and physical-GPU performance
remain open until supported by the corresponding evidence. The cloud machine
has no physical GPU; its software-renderer result must retain the existing gates.

## Inspected native streets

### Western residential street

`native-streets/street-west.png` shows an enclosed residential street with paired
frontage rows, closely spaced clay roofs, two-storey timber/plaster facades,
recessed paned windows and narrow private brick sidewalks. Shared curbs follow
the inhabited block edge and turn at the cross street. Irregular public stone
continues through the junction; no disconnected island aprons or massive gaps
appear. Warm casts cross both public and owned paving. Window boxes remain at
the facades. The foreground house fades through the existing player-reveal
behavior; its indexed model is retained.

The frontage/circulation relationship supports references 04_08_00,04_08_07 and
04_08_34. Resident patrols are present in the manifest, but this still alone does
not establish the experience of walking past them. Remaining districts and real
walking need inspection before overall acceptance. Native same-state culling
comparison: 1,432,541 → 145,035 triangles, 3,537 → 268 calls, zero differing pixels.

### Eastern residential street

`native-streets/street-east.png` also has paired closely spaced frontages, with
varied house widths, purple/clay roofs and the retained larger shop/home assembly
at the court edge. A local resident appears farther along the walking street.
Shared paving and curbs distinguish the narrow public route from the adjoining
back court; the court connects to entrances and side passages. Recessed glazing,
window boxes, sage awnings, chimneys and dormers remain readable at person scale.
The foreground house uses the same player reveal. No large isolated-house gap or
random public-floor overlay appears in the inspected frame. Native culling:
1,430,219 → 106,127 triangles, 3,539 → 234 calls, zero differing pixels; no browser
errors in either inspected street view.

### Artisan neighborhood street

`native-streets/street-artisan.png` connects the retained workshop court to a
continuous paired residential street. The workshop's covered working frontage,
an artisan service actor and a local mage resident are visible in the same
frame. The shared court is wider than the residential lane and serves the
workshop entrance; it is not a gap between isolated frontage islands. Balconies,
sage awnings, recessed windows and steep clay roofs keep the original theme.
Public irregular stone and private rectangular paving meet at the continuous
block curb without patches. Native culling: 1,429,335 → 140,573 triangles,
3,540 → 242 calls, zero differing pixels and no browser errors.

### Southern borough street

`native-streets/street-borough.png` shows the same paired residential frontage
continuing to a district junction. Shared private courts sit behind the rows,
and a local resident appears farther along the path. Narrow side gaps, balconies,
window boxes and varied roof colors preserve a domestic scale within the formal
capital plan. Curbs turn around shared block ends and separate the cross street
from owned rectangular paving. No individual island apron or disconnected floor
patch appears. This view has no faded building. Native culling:
1,422,955 → 90,135 triangles, 3,513 → 185 calls, zero differing pixels and no
browser errors. All four standard street comparisons preserve visible pixels.
