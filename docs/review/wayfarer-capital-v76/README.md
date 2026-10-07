# Wayfarer — architecture revision 76

Resumed on 7 October 2026 UTC using the user's 52 decoded Prontera RO3 beta
frames. See `prontera-beta-reference-manifest.json` and `prontera-beta-review.md`
for reference provenance, observations and required comparisons. The city checkpoint is pushed as `d7f9f15`. The model-switch audit restored its
exact source; see `checkpoint-audit/README.md`. Visual acceptance remains open.

The user rejected the repeated houses and civic roofs of revision 75. This pass
authors distinct building silhouettes and rebalances selected occupied plots
within the same original royal capital. RO3 remains the hard visual target.

- 158 residential/commercial buildings: 37 originals plus121 new buildings
  spanning nine massing families. Fourteen pairs of narrow plots become larger
  merchant halls, twin-gabled buildings and covered-gallery villas.
- Council palazzo/clock pavilion, Archive nave/reading galleries/stair tower,
  and Exchange long market hall/colonnade/belfry replace three similar civic roofs.
- Public street widths, continuous block curbs, two inward-facing gathering
  courts, ten plaza-facing entrances, eight services and both field destinations
  stay in the reviewed city plan.
- Materials and component construction are shared; complete silhouettes vary.
  Native component groups remain editable and collision cores remain separate.

Authority: `authoring/wayfarer-spatial.blend`; matching export:
`world/v3/wayfarer-spatial.json`. The existing street-layout ID remains valid;
export field `architectureRevision:76` identifies this geometry revision.

[Reference research and design](reference-and-design.md) records the specific
RO3 observations and official Prontera, Colmar and Stormwind sources.
`blueprint.png` uses the actual exported roof footprints. It is a planning map,
not a gameplay screenshot.

Evidence being produced:

| File | Purpose |
| --- | --- |
| `architecture-plan.json`, `plan.json`, `native-plan.json` | Explicit building mix and safe paired-plot consolidation |
| `baseline-geometry.json` | Rejected revision 75 resource baseline, identified by source digest |
| `architecture-check.json` | Actual geometry heights/roof profiles, true door planes, street clearance and resource size |
| `assembly-and-floor-parity.json`, `density-review.json` | Preserved original assemblies, UVs, floor unions, curb/tree contacts and visible gaps |
| `traversal.json` | Complete destination and resident-route clearance |
| `architecture-bake.log`, `foliage-bake.log`, `ground-bake.log` | Fresh lighting from the new native geometry |
| `native-parity.log`, `node-final/report.json`, `schemas.log` | Saved Blender/export parity and existing regression checks |
| `streets/`, `plaza-courts/`, `civic/` | Actual native-resolution gameplay images; per-view hashes, camera settings, errors and culling comparisons |
| `services/`, `cache/`, `performance.json` | Ordinary input, field/save flow, offline reload and unchanged performance gates |

Structural passes establish implementation integrity, not final RO3 visual
acceptance. Actual images require review. Physical-device performance and the
broader Golden acceptance remain separate from this architecture correction.

The public schema caught unsupported `guild` family metadata on the three civic
additions before browser review. `civic-family-repair.json` proves that changing
those native collection properties to the existing `civic` type leaves geometry,
materials and lighting identical. The earlier rejection is retained in
`diagnostics/schema-before-civic-family.log`; subsequent final evidence uses the
corrected source hash.

`prontera-comparison.html` places supplied timestamped frames beside native
gameplay captures. Missing images remain explicitly pending. `beta-default`
uses the910×512 viewport with unchanged gameplay controls; `beta-camera-study`
uses closer zoom with the same pitch. Neither is automatic artistic approval.

Direct beta comparison also changes public stone UV scale from8 to3.2 and adds
84 planted strips within existing neighborhood block edges. Private paving,
streets,158 door approaches and the original shadow atlas remain intact. See
`beta-edge-check.json` and `prontera-beta-review.md`. The before images retain
their own554df2f source hash in `diagnostics/before-beta-edges/`.
