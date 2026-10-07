# ASTRAEON — capital architecture revision 76

Resumed on 7 October 2026 UTC after the user added
`RO3 Ref/Prontera_RO3_Beta_Reference` and requested its use. Remote reference
commits 797e7a4/e546c30 were fast-forwarded without discarding local work. The
52 decoded 910×512 frames and four contact sheets now take priority for direct
RO3 gameplay comparisons. Their README limits global-map inference.

Architecture and foliage bakes completed before the pause. The interrupted
ground bake is complete. Native civic-family metadata was corrected after
schema validation caught the unsupported `guild` value. Geometry and all lighting
were proved identical across that correction. Source
`ad5956f55b4a4d1fb00c665754f5bc28f13b001a7f1456bf0e6c3e01894155dc`
is under final review after the direct beta comparison: public stone UV scale3.2,
private paving unchanged,84 planted block-edge pieces. All158 actual door paths
and unchanged source fields pass the independent beta-edge check; final gameplay evidence remains pending. Current architecture
changes are local and uncommitted. Do not claim the hard RO3 baseline from
geometry checks alone. No PR, merge or deployment is requested.

## Active design

One original geometric regional capital, with the original concept's timber,
clay, blue/gold and ivory theme. RO3 remains the hard visual target. Official
Prontera, Colmar tourist-office heritage and Blizzard's Stormwind tour inform
urban hierarchy and building variety; their blueprints are not copied.

Architecture revision 76 replaces the 135 repeated additions with 121 buildings
across nine massing families. Fourteen safe pairs of narrow plots become larger
merchant halls, twin-gabled buildings and covered-gallery villas. Total 158
residential/commercial buildings, including all 37 preserved originals. The
Council becomes a hipped palazzo/clock pavilion, the Archive a reading nave,
low galleries and single stair tower, and the Exchange a long clay-roofed market
hall, covered colonnade and compact belfry. Original Hall and shrine remain.

Keep the 8–10-unit public streets, 14/12-unit ceremonial axes, continuous owned
block curbs, two inward-facing gathering courts and ten plaza-facing entries.
All original services, field destinations, actors and gameplay pace remain.
The existing layout ID remains valid because streets and travel anchors do not
move. Export field `architectureRevision:76` identifies the mesh revision.

Authority: `authoring/wayfarer-spatial.blend`; export:
`world/v3/wayfarer-spatial.json`. Active evidence/plans:
`docs/review/wayfarer-capital-v76/`. Revision 75 root plans are compatibility
aliases. Its images/reports are historical, identified by their own hashes.

Last pushed checkpoint35d7f91 fixes actual plaza door directions in revision 75.
That city was visually rejected for repeated houses/civic roofs; its source hash
is `a4933847937f633ef9a27751c9ca306f3684f1b41f24b42409e8e5d382397850`.
Current revision 76 native changes are local. Geometry, assembly, density and
traversal checks passed before lighting. Architecture and foliage bakes finished;
the ground bake was interrupted by the pause and completed after the new reference arrived. Final parity, tests, browser
captures, gameplay, cache and performance verification remain pending. Do not treat the earlier 96 checks or 0 culling-pixel
results as visual acceptance of revision 76.

## Current verification

`tools/review-capital-architecture-v76.py` runs the serial review. Native
finishing corrects lodge loft/door clearance, grounded gallery posts/counters,
window-box brackets, cross-gable supports and civic roof cornices before fresh
architecture, foliage and4096² ground bakes. Saved native/export parity,
independent original-assembly/floor/door checks, full route/patrol checks, existing
Node tests and public schemas follow. Then native gameplay street/court/plaza/
civic captures, ordinary service/neighborhood walking, field/save flow, cache83
and isolated native-resolution performance are required.

Final reports and actual images must exist and be inspected before declaring
those stages verified. RO3/Golden visual acceptance remains open. The cloud
uses SwiftShader with no physical GPU; measure and report performance without
weakening existing FPS, frame-time or moving-frame requirements.

## Safe continuation

Do not rerun the one-shot author on the already edited city. Native backup:
`/tmp/astraeon-before-architecture-v76.blend` and matching JSON. The explicit
planner and architecture kit are in `tools/*architecture*v76.py`; both finishing
companions are guarded. New material/role batches preserve component selection
groups; original assemblies remain untouched and collision cores are separate.

Offline Shapely2.1.2 is at `/tmp/astraeon-curb-geometry`; set `PYTHONPATH` for
planners/checkers. Its ABI differs from Blender's Python: derive floor geometry
outside Blender. Checkers support `ASTRAEON_CAPITAL_REVIEW_DIR` for revision 76.
Use original cutout alpha via `ASTRAEON_SHADOW_ALPHA_CACHE`; lighting must follow
geometry changes. Native atlas remains `assets/wayfarer-ground-shadow-v75.png`
under cache83; offline content hashes verify the new source and atlas.

Use one browser at a time. Cloud browser execution needs the network sandbox
capability for Chromium local sockets. Server127.0.0.1:8011 logs to
`/tmp/astraeon-capital-server.log`. Captures use explicit fixture saves for visual
inspection only; ordinary service/neighborhood validation uses real input.
`ASTRAEON_ARCH_REVIEW_FROM` resumes a named serial-review stage. Capture manifests
record immutable source hashes, camera, resolution, runtime errors and culling.

For pushes use `git -c http.postBuffer=157286400 push origin
codex/world-pipeline-v3-proof`; the default chunked upload previously timed out.
No force push is authorized or necessary.

Review stages can be bounded with `ASTRAEON_ARCH_REVIEW_TO`. The current run
stops after `beta-default` for visual inspection before scheduling the remaining
views and ordinary gameplay checks. Source-specific earlier images are in
`diagnostics/before-beta-edges/`; no earlier test result certifies the new source.
