# ASTRAEON — source74 continuation active

The user resumed work on 6 October 2026 to meet the ten `RO3 Ref` images, then
identified random floor patches in the current plaza capture. Work is authorized
on `codex/world-pipeline-v3-proof`, in `/workspace/Astraeon-online`, with completed
steps pushed to the existing remote. No PR, merge or deployment is requested.

## Current saved state

Authority: `authoring/wayfarer-spatial.blend`; matching export:
`world/v3/wayfarer-spatial.json`. The layout ID remains
`wayfarer-concept-terraced-town-v49`, bounds 112×128, 120 collections, 37 ordinary
houses, 62 conifers and two broadleaf accents. Existing actor art, scale, pace,
camera defaults, gameplay and saves are retained.

Source73 finishing repairs two curb/stair crossings, rehomes 58 flower groups
into eleven house-owned clusters and grounds two complete trees on flat private
margins with .015m root embed. Nineteen closed curb loops remain. Architecture,
original-alpha foliage and original 1536² floor lighting were refreshed.

Source74 removes 645.841m² of duplicate backing underneath the actual plaza and
four approaches. All 639 flat paving surfaces follow closed private zones, with
continuous world-space irregular public stone and rectangular private paving.
Stairs and fountain steps retain their geometry/materials. Native geometry is
corrected directly; there are no runtime replacement pads. Floor shadows have
been rebaked at 1536², eight sun/four contact samples with original cutout alpha.
Page, loader and service-worker versions are 80.

## Verification and remaining work

Current evidence: `docs/review/wayfarer-v74/` and
`docs/review/wayfarer-v72/resumed/`. All 96 Node checks, four public schemas and
saved Blender/export parity pass. Seventeen destinations and ten patrols pass.
The independent floor check verifies coverage, heights, 35,359 UV corners and
public/private ownership, preserving all architecture/plants/actors/services.
The stale-bake line in parity.log follows its intentional test caster move;
the unmodified saved source has a source-matched ground bake.

Final native browser captures and reference comparisons, ordinary services,
field transition/save reload, offline cache migration and isolated sound-on
performance are in progress. The first source74 capture timed out under
concurrent schema/parity load; retry runs the browser alone. Do not reduce
resolution, source art or performance thresholds to declare a pass. Cloud
SwiftShader does not establish physical-GPU performance or user Golden approval.

Keep the localhost8011 server alive (PID1277 in this session). Use one browser
at a time. Capture at 1280×800 with 1280×666 scene, ratio 1, comparison zoom 160,
yaw 25°, pitch 46°. Default camera stays 15° fov, 46° pitch, yaw 0, zoom 125.

## Safe continuation

Do not rerun one-shot native author scripts on their completed versions. The
source73 planting and source74 floor scripts are guarded. Offline Shapely 2.1.2
is in `/tmp/astraeon-curb-geometry`; set `PYTHONPATH` for planners/checkers. It
cannot be imported by Blender's different Python ABI; plan outside Blender,
then apply with its native companion.

Floor verification: `tools/check-ro3-public-floor-v74.py --before` requires the
pre74 export (current temporary copy `/tmp/astraeon-floor73-before/wayfarer-spatial.json`).
The committed plan and report remain in the source74 evidence directory.

For fresh floor shadows, prepare original alpha via `prepare-shadow-alpha.py`,
then set `ASTRAEON_SHADOW_ALPHA_CACHE` when running `bake-ground-shadows-v54.py`
inside Blender. Repeat architecture/foliage bakes only after their geometry or
lighting changes. Preserve sun, cutout alpha and original resolution/sample counts.

The inherited pause is [historical evidence](docs/review/wayfarer-v72/PAUSED_HANDOFF.md),
not the current authorization. Previous Warrior leg/art acceptance remains open
and is separate from this town pass.
