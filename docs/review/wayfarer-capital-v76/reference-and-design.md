# Architecture and inhabited blocks — revision 76

The user rejected revision 75's repeated house silhouettes and nearly identical
civic roofs. Geometry, navigation and culling checks do **not** establish the
RO3 visual baseline. This revision addresses that rejection in the saved native
city; it does not establish final user visual acceptance.

Update7 October 2026: the user supplied 52 decoded gameplay frames in
`RO3 Ref/Prontera_RO3_Beta_Reference`. These are now the primary direct RO3
visual reference. See `prontera-beta-review.md` for observed features and explicit
limits; the earlier references and6 October research remain supporting material.

References previously inspected: the original concept image and all RO3 architectural,
plaza, gate and neighborhood screenshots (04:08:00 through 04:08:45). RO3 is the
hard target for scale, façade depth, materials and occupied streets. The concept
supplies Wayfarer's timber/clay and blue/gold/ivory civic theme, not its blueprint.

Research on 6 October 2026:

- [Official RO1 Prontera guide](https://ragnarokonline.gungho.jp/gameguide/worldmap/prontera.html)
  and its [official map](https://ragnarokonline.gungho.jp/gameguide/worldmap/rune-midgarts/imgaes/town/prontera.jpg):
  central trading square, institutions, homes and planted spaces arranged within
  a connected capital. The map informs hierarchy and variety, not copied plots.
- [Colmar tourist office: architectural heritage](https://www.tourisme-colmar.com/en/visit/presentation/architectural-heritage):
  distinct merchants' houses, public institutions, rooflines and projecting
  galleries coexist within a consistent historic vocabulary. Interpretation:
  vary whole masses and frontage uses while sharing construction materials.
- [Blizzard's official Stormwind tour](https://news.blizzard.com/en-us/article/20142731/welcome-to-stormwind-a-guided-tour):
  capital districts have different functions and identifiable landmarks.
  Interpretation: Council, Archive and Exchange need different silhouettes.

Concrete changes:

- Consolidate 14 safe pairs of narrow plots into larger buildings: 158 total
  residential/commercial assemblies, retaining all 37 original buildings.
- Author nine building families with differing massing: front gable, hipped
  merchant house, cross-gable, mansard guild house, projecting oriel, low craft
  lodge, twin gables, covered gallery villa and broad merchant hall.
- Use the nearby building graph when assigning types to reduce adjacent repeats.
  Roof hue alone is not considered architectural diversity.
- Replace all three added civic buildings: hipped Council palazzo and clock
  pavilion; Archive reading nave, low wings and a single stair tower; horizontal
  clay-roofed Exchange with a covered colonnade and compact belfry.
- Fit the Exchange inside the actual block between the market spine and circuit.
  The previous28×18 footprint crossed the planned district street. Its new
  19×13.5 footprint at192.5,126 keeps the entire public street clear; doors,
  windows and columns are authored at native size rather than scaled as a group.
- Keep 8–10-unit public streets, the ceremonial axes, continuous block curbs,
  two inward-facing gathering courts and ten plaza-facing entries.
- Reuse texture/material vocabulary and pack editable components by material.
  All models remain native Blender geometry with actual collision cores.

The existing runtime layout ID remains valid because public streets, portals,
safe spawn and travel anchors have not moved. Architecture revision 76 and
source hashes identify the new geometry independently. New shadows and native
gameplay captures are required before assessing the resulting appearance.

The local pre-bake checks also caught stale child transforms in newly packed
supports. Component packing now evaluates the dependency graph before reading
world matrices. Eighty-one affected new parts were recovered using their exact
placement transform, preserving faces/UVs; inherited assemblies were untouched.
The independent geometry check rejects visible parts outside their owner frame.
