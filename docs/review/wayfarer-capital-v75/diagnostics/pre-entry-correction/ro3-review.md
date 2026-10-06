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

## Wider-street revision

The user rejected the preceding 4–5-unit public streets as too narrow. See
`reference-scale-study.md` for the re-inspection of all ten RO3 images and the
RO1 placement principles. This revision uses 8-unit cross streets, 9-unit
neighborhood spines, a 10-unit circuit and 14/12-unit ceremonial avenues.
Five redundant through lanes are removed. All 172 complete house models remain,
with 97 in the inner neighborhoods and a median nearest visible envelope gap
of .80 world units. All original model scales, shapes and UVs are retained.

The narrow-street captures are historical diagnostics in
`diagnostics/narrow172/`, including the earlier council view. They are not
acceptance evidence for this revision. Full lighting and native/export parity are complete. Fresh views, ordinary
input traversal, cache migration and the unchanged performance gate are being checked.

An exported geometry check establishes clearance and preservation, not visual
acceptance. The final RO3 review must inspect actual rendered streets, civic
buildings, planting, foundations and nearby people. A physical GPU is unavailable
in this cloud environment; its measured software-renderer result must be reported
without relaxing performance gates. Warrior artwork acceptance remains separate.

## Current rendered findings

The four current `native-streets/` images were inspected at their native
1280 × 800 resolution against the residential/commercial references. Multiple
closely spaced two-storey houses enclose each broad public road. Complete
original shop models, awnings, window boxes, varied clay roof masses, chimneys
and recessed timber openings supply frontage variation. Shared rectangular
paving and continuous curbs bound the inhabited areas, while irregular public
stone continues through the junctions without randomly overlapping floor pads.
All four views include nearby residents. The eastern/right-hand views reveal
simpler rear/side gables as well as richer fronts; these must not be mistaken
for an assertion that every facade matches the final artistic target.

The current wide Artisans’ Court scene was inspected at native 1920 × 666.
Three frontages enclose its shared well, worktables, noticeboard, benches and
planting. Its rectangular private paving connects through side passages to
public stone; the fountain remains visible as the adjacent civic center.
Changing the two edge homes to face the square retains the owned court’s
remaining frontage and purpose. The wide camera is inspection evidence;
ordinary default-camera walking is checked separately.

Every inspected manifest records export SHA256
`4faa2cb8c9cf3e84f9373adcaa35d61b092d3b47c8891a3be49ea746cd10ca75`.
All four street views and Artisans’ Court have zero browser errors and zero
pixel/channel difference between culled and exhaustive rendering. Street
submission falls from roughly 1.424 million triangles to 78,098–127,076.
This establishes culling fidelity for these views, not a full performance pass.

Willow Court was inspected at native 1920 × 666. Varied complete houses
enclose its well, seating and planter edges, with side passages connecting to
the wider streets. Its foreground `capital-residential-071` fades through the
existing character-occlusion behavior; the building remains present. Four
nearby actors are recorded. Its culling comparison also has zero pixel/channel
difference and no browser errors (175,609 submitted triangles versus
1,431,917 exhaustive).

The Council Chambers wide scene was inspected at native 1920 × 666,
zoom325/yaw0/pitch64.88. The multi-wing blue roof, cupola and gold ridges
establish a civic mass well above nearby two-storey homes. Stone facade
openings, stepped approach and closed forecourt meet the public avenue.
The neighboring retained Hall is visible in the same scene. No cracks,
missing roof faces or curb interruptions were observed in this capture;
zero browser errors and zero culling pixel/channel differences are recorded.
The steep wide inspection camera establishes full-building context and does
not replace normal player-camera evidence.

The Grand Archive was inspected with the same wide civic camera. Its arched
entry, circular feature window, stone steps and multi-wing blue roof retain
a clear civic hierarchy above surrounding homes. The perimeter street, wall
and planted strip remain continuous beside it. It records no browser errors
and zero culling differences (198,977 submitted triangles). Council and Archive
share a civic roof vocabulary; this is not a claim of exact RO3 civic modeling.

The Trade Exchange wide scene was inspected at native 1920 × 666. Its
large blue roof and stone commercial facade, striped storefront awnings and
stepped counter approach distinguish the market landmark from nearby warm
timber housing. Shared planted private blocks face the surrounding public
routes; the eastern wall and crossing gate remain connected. The capture
has zero browser errors and zero culling pixel/channel differences (186,508
submitted triangles).

The east shoreline was inspected from outside-facing yaw90 at native
1920 × 666, zoom325/pitch46. Curtain-wall courses and repeated buttresses
stand over the native cliff foundation, with a narrow waterline and matching
stone bridge approach. Houses, curb ownership and rooted perimeter planting
remain visible behind the wall. No backface holes, floating foundation gap
or missing bridge contact were observed. The cliff face deliberately has
less geometric subdivision than the player-facing city, while keeping the
shared material vocabulary. The capture records zero browser errors and
zero culling differences (188,420 submitted triangles).
