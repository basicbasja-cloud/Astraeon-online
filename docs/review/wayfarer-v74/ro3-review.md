# Source74 RO3 reference review

Review all ten supplied images at their original 1536×709 size and the game at
native 1280×800, with its 1280×666 playfield at pixel ratio 1. The still comparison
camera uses ordinary controls: zoom 160, yaw 25°, pitch 46°. These captures do not
change the default camera, character scale, animation, resolution or movement pace.

| Supplied reference | Candidate views | Inspect |
| --- | --- | --- |
| 04_07_07 PM | gate, avenue | Paired gate masses, open approach, enclosing walls, owned planting, coherent sun |
| 04_08_00 PM | frontage-home, residential | Two-storey scale, clay roofs/dormers, recessed windows, timber relief, foundations, house-side green |
| 04_08_07 PM | plaza, avenue | Public-space scale, enclosing frontage, clear circulation, irregular paving distinct from lot brick |
| 04_08_14 PM | hall-axis, plaza | Civic hierarchy, formal planted edges, clear boundary geometry and contact shade |
| 04_08_20 PM | plaza | Tiered fountain/water, planted corner beds, sage benches, plaza scale and symmetric approaches |
| 04_08_24 PM | plaza, market | Warm broad sun/cast shade, street width, useful open space, shop-front access |
| 04_08_30 PM | shrine, hall-axis | Detailed civic façades, grounded tree islands, curved closed edges, stone/material separation |
| 04_08_34 PM | residential, inn | Steep roof silhouettes, side-wing relief, aged walls, building density, owned space |
| 04_08_39 PM | market, frontage-shop | Shop-facing stalls, accessory placement, public/private paving, shadow continuity |
| 04_08_45 PM | frontage-shop, blacksmith | Façade depth, recessed doors/windows, exterior goods, warm texture cohesion and grass edges |

Every candidate also needs a sweep for open curb ends, conflicting curb/stair
grades, isolated flowers, floating roots, stamped floor pads, material seams and
unreadable ground texture. Geometry checks support the review; they do not award
visual acceptance. Physical-GPU performance and the user's Golden acceptance
remain distinct from cloud screenshots and software-renderer measurements.

Current fixes and verification are summarized in `README.md`. The source73
plaza image was rejected for patchy public floor; its observations are not final
acceptance. Source74's unbatched plaza confirms the reported floor defect is
resolved. Final spatial-batch captures and exact same-state culling comparisons
are in progress in `native-batched/`. Findings will be added as each is inspected.

## Inspected final views

### Plaza

The source74 plaza at native resolution reads as one continuous public stone
surface. The former rectangular overlay fragments are gone; lot brick remains
inside the curb boundary. The intentional fountain foundation has pale stepped
stone, tiered turquoise water, four corner beds and sage benches. Warm broad cast
shade and soft contacts tie the surrounding roofs, trees and fountain to the
floor. The court is spacious, bounded by detailed two-storey frontage, and the
approaches meet it without texture-phase/tint jumps. This addresses references
04_08_07,04_08_20 and04_08_24 and the user's rejected random-floor image.

Exact same-state rendering at1280×666 finds zero different pixels when culling
is enabled versus exhaustive static submission (595,705→315,496 triangles in
this camera). This is graphics-preservation evidence, not an FPS or Golden pass.

### Avenue

The main approach has continuous irregular public stone with no rectangular
confetti or phase seams at the plaza connection. Two-storey frontage encloses
the street; dormers, projecting timber, window boxes, side-wing windows and
aged clay roofs remain readable. Narrow private brick margins, closed bevelled
curbs and rooted conifers distinguish owned lots from the broad public route.
Cast shadows cross both surfaces coherently. The scene matches the public/lot
relationship in04_08_07 and04_08_24 while retaining original ASTRAEON architecture.
The full/culling native frame comparison has zero differing pixels.

### Market

The raised merchant court now shares the public irregular-stone pattern instead
of reading as an unrelated rectangular patch. The stair/retaining edge still
communicates the level change. Six cloth-canopy/counter ensembles face usable
public circulation; pots/produce/folded cloth remain beneath their canopies.
Goods and flower accents follow shop ownership, and aged timber/plaster, clay
roofs and pale stone stay cohesive. This reflects04_08_24 and04_08_39. The
native pixel comparison again finds zero differences with culling.

### Shop frontage

The shop-facing court and market approach now use coherent public stone rather
than conflicting rectangular patches. Each shop keeps a clearly bounded private
brick margin with plinth courses, green seams, flower displays and small packing
props. Recessed paned windows, shutters/dormers, projecting timber, sage striped
awnings and aged roofs provide facade relief, as in04_08_00 and04_08_45. Public
benches and circulation sit outside the owned curb zone. Culling introduces
zero pixel differences in the native frame.

### Home frontage

The residential/market seam keeps public stone separate from the bounded lot
brick. Full opaque houses show two-storey scale, recessed door/window surrounds,
window-box details, dormers and weathered clay roofs. Owned flower/grass margins
remain within the closed edges; the retaining wall and raised market approach
keep their intentional stone level changes. This corresponds to04_08_00 and
04_08_34. The foreground house is translucent because the existing gameplay
occlusion reveal exposes the player behind it; this is retained behavior, not
missing building art. The same-state culling comparison includes that reveal
and still reports zero pixel differences.

### Inn

The inn's balcony/side wing, recessed openings, timber courses and steep aged
roof give the facade depth at the same person-relative scale as nearby houses.
Its service approach reads as an intentional public entry within bounded
private brick/grass margins; the curb closes around the owned space and tree
planting. No isolated flower pad or conflicting plaza texture appears. The
neighbouring house keeps a clear plinth and planted edge. These features support
04_08_00,04_08_34 and04_08_45. Culling leaves every native pixel unchanged.

### Hall axis

The fountain axis meets the wide civic stair symmetrically. Curved closed lot
edges contain paired conifer/grass areas beside the flanking blue-roofed civic
pavilions; broad public stone leads to intentionally rectangular stair treads.
Retaining courses fit the stair opening without stranded curb ends. Warm shade
separates posts, tree tiers, steps and paving, supporting04_08_14 and04_08_30.
This framing reviews the approach, not the Hall's tall facade; a supplementary
Hall-terrace/skyline capture is planned. The native culling comparison is exact.

### Shrine

The civic shrine's arched entry, recessed glazing, stone surrounds, blue/gold
roof sections and dressed foundation remain distinct from the timber houses.
Its private apron, curved closed edge, tree bed and planted margins meet a clear
public approach. The enclosing residential facades retain full window/wing
detail and owned grass areas. Warm casts ground the stone and conifer tiers,
supporting the civic/planting relationships in04_08_30. The uppermost spires
are outside this close framing; no facade detail is missing from the source.
The native culling comparison again has zero pixel differences.

### Residential, blacksmith and gate

Residential facades retain their recessed openings, roof detail, private margins
and existing player occlusion reveal. The artisan approach joins continuous
public stone to the owned workshop frontage. The gate retains dressed wall
courses, blue-roofed towers, banners, bridge, water and cliff contacts. All three
native views have zero pixel differences with culling and no errors. These close
views support the floor fix, not whole-city or Golden acceptance.

The next scope expands Wayfarer into a regional capital. Prontera is only a
scale/district reference, and the original concept is a theme; RO3 remains the
hard ultimate visual target. New districts and shoreline require fresh review.
