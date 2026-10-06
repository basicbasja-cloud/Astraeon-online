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

## Actual entrance correction

The first rendered sweep found that `ro3-infill-approach-1` retained a west-facing
door despite a south-facing placement heading. The complete retained assembly
now rotates 90 degrees clockwise and shifts .4 world units west, with its
indexed geometry, UVs and entrance contacts preserved. A `frontageOffset` records
its legacy model’s geometric front independently from its assembly rotation.
The independent check now verifies actual door planes for all ten square-facing
frontages, as well as their intended headings and whole visible envelopes.

The preceding checkpoint’s captures and review are retained in
`diagnostics/pre-entry-correction/`; they are historical comparison evidence.
Full architecture, original-alpha foliage and ground lighting are being refreshed
after this correction. Fresh native views and ordinary walking will verify the
corrected immutable source before the final report.

## Corrected-source rendered findings

The wide fountain-plaza scene was inspected at native 1920 × 666,
zoom325/yaw25/pitch64.88. Private rectangular paving and closed curbs define
the surrounding frontage blocks and Artisans’ Court, while irregular public
stone runs continuously around the retained fountain. Nearby roofs, facades,
planted edges and the visible market civic edge establish the broader capital
context. The northern entry row is beyond this camera’s upper edge; the
street-level north-frontage view and independent actual-door-plane check
verify those entrances separately. Three nearby actors are recorded.

This corrected capture records source SHA256
`a4933847937f633ef9a27751c9ca306f3684f1b41f24b42409e8e5d382397850`,
zero browser errors and zero culling pixel/channel difference, with 288,389
submitted triangles versus 1,423,797 exhaustive. This is a wide inspection
view, not a claim that default-camera square views show all ten facades.
