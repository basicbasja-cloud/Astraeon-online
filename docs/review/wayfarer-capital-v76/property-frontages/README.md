# Property frontages and tone — after the checkpoint audit

The user requested very similar local placement and tone to the supplied RO3
beta frames, with Wayfarer's own theme. This continues the building-variety and
balanced-neighborhood task after restoring the audited `d7f9f15` source.

## Observed issue

Four ordinary 1280×800 neighborhood views are preserved in `../streets/`, source
`ad5956f55b4a4d1fb00c665754f5bc28f13b001a7f1456bf0e6c3e01894155dc`.
Their source/camera/position metadata is in `views.json`. All had zero runtime
errors and zero pixel changes from ordinary static culling. Building spacing and
roof heights vary, but ground-floor treatment and empty aprons still repeat.

RO3 house frames01:40 and03:35 show sheltered shop fronts, broad/narrow mixed
houses, low work buildings, planted courts and purposeful entry terraces. These
local relationships guide the new meshes. No unseen complete map is inferred.

## Authored candidate

- 18 shops: actual pierced front walls, recessed display bays, segmented awnings,
  supported counters and different provisioner, clothier and herbalist displays.
- 17 workshops: exterior tool racks and geometric trade emblems.
  Usable benches place the tools below actual ground glazing; generic produce
  counters/flowers are cleared from those work bays.
- 11 homes: gabled/shed entries and shutters matched to saved window bounds.
  Two projecting oriel homes keep shutters without an intersecting second porch.
- Existing construction materials and textures; editable component groups remain.
- 91 owned lawns (85 before plaza enclosure) replace the uniform perimeter ribbons with curved inner
  edges and planted pockets. Actual door paths remain 2.2 units clear; work
  bays, roads, curbs and underlying private paving stay intact. Planted area
  changes from 1,273 to 1,778 square units.
- 78 evergreen crowns use 90 overlapping boughs each and three fullness
profiles. Existing trunks, roots, collision and full-resolution foliage
textures remain. Original-alpha lighting is refreshed after the crown edits.
- A restrained palette pass warms clay/rose roofs, warms timber, neutralizes
  paving and cools shadow/ambient color. Domestic timber/clay/ivory and civic
  blue/gold remain Wayfarer's visual vocabulary. These are authored values, not
  measured RO3 colors.

`authoring.json` records the exact properties and triangle budget. `tone.json`
records exact old/new color values. The authoring guard compares public floors,
navigation, anchors, every solid and actual door leaf before saving. The palette
guard allows only its declared colors and light colors to change.
`landscape-authoring.json` separately records the 23,050 added landscape
triangles and retained roots. The independent landscape check measures native
triangles, private ownership, actual entrance paths and source-matched crown
lighting. New grass shapes are geometry; reference pixels were not imported.
The runtime now honors the revised native timber color, which its legacy swatch
previously overrode. Lawn detail mixing increases from 0.24 to 0.72 and uses
anisotropic filtering; source images, UV scale and resolution stay intact.

## Verification and acceptance

The user also specified the RO3 camera as the baseline. Matched910×512 studies
at50° and55° are in `camera-study/`. The selected default is55° pitch,20° orbit,
125 distance and15° field of view. These are Wayfarer's calibrated parameters,
not extracted RO3 telemetry. Initial projection, control targets and resets share
one baseline. The renderer uses a canonical sprite axis so nonzero default yaw
does not rotate sprites twice, and pitch changes preserve artwork aspect ratios.

New capture manifests include alpha-tight player bounds, projected nearby door
bounds, runtime file hashes and floor-atlas hashes. Door rectangles are projected
geometry and do not imply that a door is unobscured in the selected image.

The candidate requires refreshed source-matched lighting, native parity,
geometry/door/route/schema checks and ordinary gameplay comparison. Those logs
are written here, with exact verified source hashes after completion. The older
beta-edge integrity receipt applies to its historical source; it does not accept
this intentionally changed architecture and palette.

Gameplay images, their manifest and the side-by-side viewer must establish the
visible result. A larger number of meshes or a structural pass cannot establish
the hard RO3 baseline. Visual acceptance is open until those images are reviewed.

The audited source survives in Git and in
`/tmp/astraeon-before-property-frontages-v76/`. The discarded six-walker model
experiment was not used. Cache 86 delivers the changed world/floor atlas together.

## Plaza enclosure and grass/stone transition

The910×512 source-matched plaza capture showed excess empty foreground compared
with fountain00:35. The four side properties move 10 units inward as complete
assemblies, with doors, physical cores and entrance contacts.314.4 square units
of surplus plaza paving become joined private terraces; main avenues remain
8/9/10/14/12 units wide. The existing plaza patrol takes a clear inner circuit.
No buildings or residents are added, and the entire-city resize authorization
remains available. These local frames cannot establish Prontera’s global size.

The user identified the hard grass/stone border. Native lawns are tessellated
into opaque interiors and0.28-unit translucent fringes, using generic optional
`vertexOpacity` exported from Blender’s `SurfaceOpacity` point attribute. Existing
world-space grass UVs, texture resolution and the owned planting mask remain.
The existing feather shader reveals stone beneath the transition. This adds
13,679 triangles within a separate 20,000 triangle limit, with no texture,
collider or dynamic shadow cost. Renderer batches retain spatial culling.

Plans and authoring receipts: `plaza-enclosure-plan.json`,
`plaza-enclosure-authoring.json`, `grass-feather-plan.json`. Independent checks
verify translated complete fronts, declared floor edits, closed curbs, unchanged
other geometry/anchors, exact opacity data and retained planting ownership.
The earlier8e5f2a85 captures are before these changes, not acceptance of them.

## Resumed RO3 daylight and planting candidate

After the mobile gate, the second plaza iteration moves the same four whole
properties a further6 units inward (16 total), with their doors, physical cores,
entrance contacts and joined curbs. The joined private extension now occupies
518.39 square units; the fountain stays at its existing size and position.
The resulting public plaza is920.54 square units. Broader city resizing remains
authorized; these adjustments do not establish the final RO3 scale acceptance.

Small rounded groundcover keepouts now use16 sides, with slightly larger radii
whose minimum radial clearance exceeds the previous0.20/0.12-unit limits.
This removes unnecessary contact facets while preserving planting protection.
There are93 lawn pieces covering1,825.64 square units, with14,177 triangles,
including8,386 feather triangles inside the unchanged20,000 feather budget.

`ro3-daylight-authoring.json` records the restrained warmer stone and neutral
shadow candidate. Lawn grain is normalized using the measured linear mean of
its original image; `paletteNative` explicitly lets the native lawn palette own
its color. Existing images, tile size, world UV scale and resolution stay intact.
There are800 small lawn-edge tufts and400 roots sampled from actual dark paving
joints near planted curbs,3,600 triangles total. They share the existing lawn
image, add no gameplay obstacles and keep2.2-unit door passages clear.
`grass-ingress-plan.json` and `grass-ingress-check.json` record/check exact roots,
painted joints, floor height, native geometry, UVs and budgets.

The latest user steering includes camera angle as part of the hard RO3 target.
Fresh angle studies must compare roof/façade balance, street depth and framing
alongside placement. The current55°/20°/125 default remains provisional; these
are project parameters rather than recovered RO3 camera telemetry. Rebuild and
verify source transport after every native change before fresh captures.

## Camera selection and original plaza activity

Four fresh paired studies compare45°/20°/125,50°/10°/125,45°/10°/110 and
50°/10°/110 with the preceding55°/20°/125 default. The selected gameplay default
is45° pitch,10° yaw,110 distance and15° field of view. The lower roof emphasis,
more forward street view and roughly58-pixel player alpha height at910×512
fit the supplied street framing more closely. `ro3-camera-decision.json` records
these observed choices. Initial view, control targets and resets use one default;
artwork, input, native geometry and image resolution retain their existing paths.
These camera values are project calibration, not extracted RO3 telemetry.

Seven broader default-camera captures are in `ro3-polish-final/`, source
a8872a1daf7caa5076e2fa2cf5f52b55a75597a833e85d4b01bd109717b216a3.
They show the plaza, street, tree contact, merchant frontage, Willow Court,
ceremonial approach and eastern ward. All have0 runtime errors and0 pixel
changes between ordinary and exhaustive static culling. This review still found
only two visible actors at the fountain. RO3 fountain00:35 supports a more active
center, but its real-player crowd is not a blueprint for copied NPC identities.

Eight original Wayfarer citizens add local watch, visitors and couriers around
plaza fronts. They reuse existing warrior/mage/ranger art and add no images,
static triangles, collision objects or lighting changes. The original28 resident
records remain; total36. `plaza-life-plan.json` records original roles and safe
routes; the native author preserves all other exported values exactly.
`plaza-life-check.json` independently removes only these eight records and checks
that the complete preceding export reconstructs byte for byte. Existing patrol
sampling checks every original/new route. This justifies keeping the verified
baked lighting rather than paying to bake an unchanged static scene again.

Source-matched captures after this population pass remain separately labeled.
Whole-city scale/composition acceptance is assessed from those views, with full
resizing still authorized. Physical iPhone Safari acceptance remains PENDING.
