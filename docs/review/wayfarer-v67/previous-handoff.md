# ASTRAEON continuation checkpoint — 2026-10-05

## Workspace and authority

The user explicitly resumed from the October 4 handoff on branch
`codex/world-pipeline-v3-proof`. Current cloud checkout: `/workspace/Astraeon-online`.
Origin: `https://github.com/basicbasja-cloud/Astraeon-online.git`.
Parent checkpoint: `1b0fca4355c7380f2e44e132edb90dc298d702ec`.
The commit containing this document is the continuation checkpoint; obtain its ID
from Git history. Development is active; the prior pause/shutdown instruction is
superseded by the user's continuation. No shutdown or new deployment was requested.

**Town acceptance=false. Locomotion acceptance=false. Cosmetics implemented=false.**
Technical checks do not override the user's rejection of town presentation or
painted body movement. This is a bounded town architecture and render-clarity pass.

Review: `docs/review/wayfarer-v65/README.md` and `summary.json`. The complete prior
handoff, reference research, geometry history, animation diagnosis and held-art
restrictions are preserved in `docs/review/wayfarer-v65/previous-handoff.md`.
The original pause metadata/raw gait ZIP manifests remain in
`docs/review/pause-2026-10-04/`; no held character art was installed.

## Reference requirements and latest steering

- Approved `concept art.png` controls original identity, macro layout, districts,
  architecture and Hall hierarchy above water. Keep the Hall massive relative to
  people; preserve playable terraces and waterfalls.
- All ten local `RO3 Ref/` images were inspected. They control the presentation
  comparison: deep roof/facade forms, painterly values, daylight/contact shade,
  functional density and person-relative travel. No proprietary assets were copied.
  Their low image resolution is not an output-resolution target.
- Town work precedes full-body animation replacement. Broader building depth,
  Hall composition, density/life and painterly finish remain below acceptance.
- The user asked why the ordinary gameplay screenshot looked low resolution.
  `world/v3/renderer.js` forced software WebGL to pixel ratio 0.5, stretching a
  half-size world behind the sharp DOM HUD. Runtime revision66 removes that
  reduction: software uses native CSS pixels; hardware follows device density
  up to 1.5×, with a minimum of 1×. Pixel ratio is no longer secretly lowered for
  software performance. Existing sprite art still limits anatomy/detail.

## Exact saved state

Native source: `authoring/wayfarer-spatial.blend`.
Export: `world/v3/wayfarer-spatial.json`.
Layout: `wayfarer-concept-terraced-town-v49`, 119 objects.
Saved architecture/frontage source pass: **65**; grounded flora remains **64**.
Boot, index and service-worker cache/precache versions: **66**, consistently aligned.

- Corner bake65: 385,113 corners / 9,865 meshes / 16.3 seconds.
- Ground bake65: 1024², 615,909 land / 327,474 shadowed pixels / 88.1 seconds.
- Ground atlas: historical `assets/wayfarer-ground-shadow-v54.png` filename retained.
- Export includes valid ground-shadow metadata for geometry digest
  `20d2c9cd129bb7ec0b1b953e99f5fb30bb93744868e68ddd5a5c043cc8b5efb2`.
- Original foliage alpha participates in native casts; no stale bake was restored.
- Lighting sun .72 / cool ambient .36 / cast vector (.62, -.40) retained.

Do not reconstruct the town by rerunning historical builders. Source save,
export and lighting mutations must be sequential. Do not overlap them with
browser review or isolated performance. Geometry edits invalidate both bakes.

## Source65 architecture

`tools/author-frontage-families-v65.py` operates on the saved flora64 town.
It replaces twelve existing frontage window envelopes and competing small
windows/dormers with larger openings, splayed reveals, recessed glazing,
mullions/transoms and projecting sills. Residential shutters remain
frontage detail. One cross gable per lot meets a real cut in the original curved
roof, preserving the surviving roof planes' UV mapping and baseline shape.
Related home/merchant/workshop limewash and warm clay/cool slate colors create
family variation using the existing original atlases.

New meshes are children of existing placement roots with overhead roles.
The comparison against source64 preserves all terrain/walkable floor data,
navigation, spawn/review routes, service/presentation/portal anchors, civilian
patrol routes and every solid's geometry. See `native-preservation.json`.
Visible triangles: 231,062 versus source64's 232,620; materials 61 versus 53.
This is eight more material batches, not a measured performance improvement.
Roof baselines are stored on source meshes for repeatable replacement.
Re-running this authoring script requires fresh corner and ground bakes.

## Verification and evidence

The review README and summary record scoped outcomes, including partial replay
evidence and failures. The isolated native-resolution cloud SwiftShader check
failed the performance gate: 1.74 FPS / p95 and maximum 883.3 ms, drawing buffer
1280×666 at ratio1, runtime errors[]. Only 11 moving pairs were sampled, too few
for continuity certification. The >55 FPS / p95<25 ms / max<80 ms assertions were
not loosened and native resolution was retained. Physical devices are unverified.
Revision66 cache migration and offline saved-character reload passed (92 requests).
The 13 civic/shrine/Hall/gate cases completed before a too-close market waypoint
failed. Corrected native-resolution replay completed all four market flights plus
field transition/save reload, then failed final telemetry sampled from an inactive
field renderer. The helper now samples the town before departure. These partial
logs are preserved and are not described as full-script passes.
Eight ordinary-input service checks completed across the initial seven-service
replay and a focused Luna shrine retry. The initial long shrine approach timed
out while still moving; its partial report is retained. The focused retry passed,
including the native town drawing buffer (1280×666, ratio1), actual field transition
and saved-character reload. Runtime/resource errors are empty. See
`services-report.json` and `shrine-retry.json`.
95 individual Node checks, public schemas and saved Blender/export parity passed.
The parity check also verifies Hall parent transform propagation and deliberately
invalidates the bake after an unsaved Hall move; its stale-bake diagnostic is expected.
All checks must use Blender `--python-exit-code 1` to expose Python failures.

The managed Node24 default runner reported only file wrappers. Use
`tools/run-node-checks.py`, which runs six independent files with isolation disabled
and records all 95 registered tests. Do not report six wrappers as 95 assertions.
Browser QA now supports Linux SwiftShader and Windows D3D11.
Market replay bases are beyond the first tread by more than arrival tolerance;
previous overly close bases stopped on a tread and falsely failed descent.
Expanded-town travel timeouts use authored route length and a bounded allowance
for observed RAF intervals longer than the existing 250 ms simulation-delta cap.
Gameplay speed/clock and performance assertions were not changed.

Still architecture reviews at zoom160/yaw25 used capture ratio1.5 and do not
establish FPS. `arrival-native.png` is ordinary gameplay with no capture override
following the resolution fix. Isolated sound-on software timings cannot certify
hardware desktop or phone performance. Never lower resolution or loosen performance
assertions solely to make a report pass.

## Locomotion and next work

No production character art, animation state, speed, save key or progression
contract changed. The Warrior still has incorrect leg alternation/body registration,
weapon continuity and some squat/hopping poses. Mage/Ranger still reuse their
walk atlases for all speeds. Runtime root continuity does not validate painted
contacts or anatomy. All v50/v51/v52/v53/v63 studies remain held/unapproved.
Read the full diagnosis and shared-source-root pipeline in the archived handoff
and `research/character-locomotion-and-cosmetics.md` before any character work.

Continue town structure and composition against concept/RO3 first. Inspect actual
native-resolution gameplay and normal-speed motion. Deeper roof/façade family
forms, Hall hierarchy/framing and functional density remain open; avoid substituting
noisy texture detail for architecture. Then build coherent full-body action strips
with one shared source root/scale and measured painted contacts, inspect every
heading/mode/transition, and integrate only after approval. Cosmetics wait for
stable original body animation; ownership/payment systems remain unimplemented.

Preserve users' existing saves/progression and unrelated files/apps. No subagents
were authorized or used. The prior handoff explicitly authorizes pushing repo
changes; no new thread or PR was requested.

## Tools and restart

No npm/build/install step is required. Current loopback preview:
`http://127.0.0.1:8011/`. Recreate after environment restart:

```sh
python3 -m http.server 8011 --bind 127.0.0.1
python3 tools/run-node-checks.py
python3 tools/validate-world-v3.py
blender -b authoring/wayfarer-spatial.blend --python-exit-code 1 --python tools/check-blender-export-v3.py
python3 tests/golden_wayfarer.py --phase spatial --output /tmp/astraeon-spatial65
python3 tests/golden_wayfarer.py --phase services --output /tmp/astraeon-services65
python3 tests/cache_resume.py --output /tmp/astraeon-cache66
python3 tests/movement_performance.py --output /tmp/astraeon-performance66.json
```

Cloud Python3.12 / Node24 / Chromium151 `/usr/bin/chromium` / Blender4.3.2.
Playwright, jsonschema and PIL are available. Network/loopback browser calls need
network permission in this managed environment. Linux uses SwiftShader with
`--no-sandbox --enable-gpu --use-angle=swiftshader --enable-unsafe-swiftshader`;
Windows uses D3D11 through `ASTRAEON_BROWSER`. The agent-browser CLI is unavailable;
existing Python Playwright tools perform review. Original Windows bpy fallback
and alpha preparation/bake commands are preserved in the archived handoff.
