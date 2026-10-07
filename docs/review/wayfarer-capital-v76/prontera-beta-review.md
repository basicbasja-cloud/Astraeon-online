# Prontera RO3 beta: direct visual reference

The user supplied these frames on 7 October 2026 and requested their use after
pausing city work. Reference commits 797e7a4 and e546c30 are integrated into the
working branch. The 52 original910×512 frames, timestamps and hashes are recorded
in `prontera-beta-reference-manifest.json`. All four chronological contact sheets
were inspected; representative individual frames were opened at original size.

These decoded gameplay frames take priority over reconstructed reference images
when judging visible RO3 scale and local urban composition. Wayfarer retains an
original geometric royal city plan and its concept's timber, clay, ivory, blue
and gold theme. The references establish local visual relationships, not surveyed
world dimensions or a complete global blueprint.

| Evidence | Observed in the supplied frame | Wayfarer review criterion |
| --- | --- | --- |
| Fountain00:35,00:40,05:15 | Fountain, planted compartments, benches and lamps form one social centerpiece; ample paving surrounds it and buildings frame its approaches. | Keep an accessible central gathering space, plaza-facing entries and a recognizable fountain ensemble. Judge actual gameplay composition, not the overhead plan alone. |
| Houses01:40,01:45,03:25–03:35 | Narrow and broad timber houses share materials but differ in roof mass, dormers, corner treatments and frontage uses. | Neighboring buildings need visibly different whole silhouettes; check the mix of broad and narrow fronts against character and door size. Nine labels alone do not establish success. |
| Streets02:00,02:05,03:05 | Irregular small stone roads meet rectangular private-edge paving; continuous curb lines organize junctions. | Preserve uninterrupted public routes and distinguish road, private apron and raised edge without disconnected curbs or random floor overlap. |
| Houses02:10,03:15,03:20 | Small green strips, trees, low fences, benches, goods and awnings occupy the space beside houses. | Empty setbacks should become purposeful local frontage space where appropriate; entrances and junctions must stay clear. Avoid filling every spare surface with props. |
| Training02:30–02:40 | Two identifiable activity courts have sand floors, low borders, seats and practice equipment along an open street. | Shared courts need a legible purpose, distinct surfaces and inward-facing occupants. Court entries and surrounding pedestrian routes must remain usable. |
| Cathedral01:15–01:25 | Monumental facade, projecting portal, statue, planted formal trees and a generous forecourt establish institutional importance. | Civic buildings need distinct massing, credible facade depth and readable forecourts. A taller repeated house is insufficient. |
| Gate04:05–04:25 | A wide gate approach has a clear road, planted borders, banners, benches and a consistent stone enclosure. | Gate, wall footing and approach detail need the same material care as the city, with open passage and coherent shore transitions. |

## Camera and scale discipline

Compare buildings to visible characters, door leaves, benches and the road in
the same frame. Pixel counts across differently pitched or zoomed cameras are
not absolute world measurements. The clip's UI and minimap remain in its decoded
frames. Keep ordinary native gameplay captures alongside scene-only images;
larger or specially aimed presentation captures do not replace the walking view.

Current native geometry has 158 residential/commercial buildings, including 37
retained originals, 121 new buildings across nine families, and 14 paired-plot
consolidations. New-house median width is 4.2 world units. This is a measurement of
Wayfarer, **not** a dimension established for Prontera. The actual narrow/broad
mix still needs image review; the count and geometry passes do not prove the
reference's inhabited streets or architectural scale.

## Limits and remaining work

The 04:55 loading screen is not city geometry evidence. Other visible players do
not establish an NPC population budget. Unseen sides, gate compass directions,
castle identity and global street connections remain unverified in this clip.

Architecture and foliage bakes completed before the pause. Ground lighting is
complete for the saved architecture. Schema review caught unsupported `guild`
metadata on the three civic additions; the native repair uses the existing
`civic` family and proves all geometry, materials and lighting unchanged. The
corrected source is
`554df2f70f949ba3ba350f467770eb6d5ca8d49740640b34a0c98a4856427deb`. Final native/export parity, geometry and
navigation reports, fresh street/plaza/court/civic/shore images, ordinary service
walking, save/cache behavior and performance remain required. Review those
actual images against the rows above before further visual changes or claiming
that Wayfarer meets the hard RO3 baseline.

## Changes selected from the direct comparison

The first910×512 default-camera captures are preserved in
`diagnostics/before-beta-edges/beta-default/`, source
`554df2f70f949ba3ba350f467770eb6d5ca8d49740640b34a0c98a4856427deb`.
The player's projected geometry height was49.83 pixels. Building size did not
justify changing the user-directed camera defaults. The visible road stones were
large beside the beta's smaller cobbles, and many owned frontages remained bare.

The native public stone repeat is now3.2 world units instead of8; private pavers
remain8. This is a Wayfarer design choice derived from the visual comparison, not
a surveyed Prontera dimension. All244 public floor meshes share the new continuous
world-space UV phase, including raised public paving.

Planted bands follow existing neighborhood block edges and are clipped clear of
actual doors, courts, props and streets. Eighty-four connected pieces cover about
1,273 square world units and add4,680 triangles. They reuse the existing grass
texture and sit7mm above the private paving, below the15mm shadow receivers.
No collision obstacle, actor, runtime shadow effect or additional texture is
introduced. The original source-matched4096² cast atlas remains valid.

`beta-edge-check.json` verifies all 158 actual door paths and zero public-road
overlap. An integrity digest preserves every other source field, including all
building geometry/UVs, private paving, navigation, materials and lighting; only
public UV density, its declared texture scale and the new groundcover are allowed
to differ. The complete saved source remains subject to fresh gameplay inspection.


## Resumed visual comparison — 7 October

The checkpoint audit restored `d7f9f15`; its exact export hash is
`ad5956f55b4a4d1fb00c665754f5bc28f13b001a7f1456bf0e6c3e01894155dc`.
The subsequent frontage/landscape candidate at
`8e5f2a85a48d84a75fabbae5e76bc96c714446a2eeaff4f0aa6db65745fab8ad`
passed the complete source checks. Its captures are preserved in
`property-frontages/diagnostics/before-plaza-enclosure/`; those captures establish
what was inspected before the following corrections.

- West street: continuous adjoining fronts now show varied entry/shop/work uses.
  Door comparisons use actual projected vertical edges, not their angled screen
  rectangles. At 910×512 the player alpha height is about41 pixels; nearby
  vertical door edges are about43–51 pixels. These measurements do not establish
  surveyed RO3 dimensions.
- Merchant street: the first native timber color was too pale. Its final warmer,
  darker authored color restores clearer facade contrast while preserving ivory
  plaster and clay roofs. Broad/narrow and high/low buildings remain mixed.
- Tree contact: the fuller native crown has overlapping illuminated/shaded boughs
  and a grounded trunk, with original alpha textures. All 78 retain their physical
  roots; crown detail adds no physics obstacle.
- Fountain00:35 comparison: the old square had too much empty foreground, with
  side properties outside the main walking view. Four complete side properties
  now move 10 units inward, with joined terraces, entrance contacts and curbs.
  All main road widths stay8/9/10/14/12; the existing plaza patrol is rerouted
  around the closer fronts.
- Latest user feedback: grass should blend with the stone blocks. The opaque
  silhouette was still too abrupt. Native vertex opacity now gives each lawn a
  narrow translucent edge, revealing the same rectangular private paving below.
  Planting ownership, entrances, texture phase and native image resolution stay.

The user authorizes a full city resize. The supplied local frames establish the
visible plaza excess, but cannot establish the complete RO3 footprint. Tightening
these fronts is a concrete local correction; a global percentage resize should
not be inferred from an unsurveyed map. Current city bounds remain 256×288.
Final captures and gameplay receipts must reference the newly rebaked source;
this section does not grant visual acceptance before that inspection.
