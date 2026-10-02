# ASTRAEON cloud-task handoff — 2026-10-02

## Checkpoint and execution boundary

- Active branch: `codex/world-pipeline-v3-proof`.
- Remote: `https://github.com/basicbasja-cloud/Astraeon-online.git`.
- Previous committed HEAD: `bf1b49b0792092e31caf222e3f694ad8e2d20b8c`.
- This handoff is included in the new checkpoint commit. Read its SHA with
  `git log -1 --format=%H`; the SHA cannot be embedded in its own commit.
- The user explicitly stopped implementation to transfer tasks. No new
  implementation, asset generation, source regeneration or review run was
  started after that instruction. Existing work and recordings are preserved.
- **Golden Wayfarer Master Plan remains unfinished. This is not project
  completion or Golden approval.** Resume from this saved state in the new task.

## Latest implementation state

Default gameplay uses the actual saved Blender spatial town in a lightweight
Three.js scene. Illustrated directional actors participate in that same scene
and depth buffer. Canvas/whole-building sprites remain explicit migration
fallbacks, not the target environment. Existing simulation, quests, combat,
inventory, saves and progression are retained. Cache version is now **36**.

The authoritative environment is `authoring/wayfarer-spatial.blend`; its current
matching export is `world/v3/wayfarer-spatial.json`. Native object IDs, geometry,
navigation, elevations, services, passages, portals and lighting originate in
the saved scene. Do not re-create the town from historical builder scripts.

The concept hierarchy is gate → avenue → fountain plaza → Consortium Hall,
with distinct market, inn, forge, shrine and residential districts. Existing
street-facing residential rotations, gardens and approach paths are preserved;
homes do not all face one direction. Spatial foliage and software color/depth
caching already exist. Actor artwork remains 2D painterly directional sprites.

## Completed in this cloud task

Earlier checkpoints already preserve the spatial migration (`5b2011c`),
street-facing homes and foliage/depth caching (`1327194`), authored fountain,
plaza and lighting (`c7d40c5`), and required deferred productionization amendment
(`bf1b49b`). Do not repeat these phases or the bounded renderer comparison.

Work newly preserved by this checkpoint:

- Targeted edits to the existing Blender scene: open stone forge/hearth,
  chimney connection and wall tools; maritime inn sign; shrine entrance trim,
  rose glass and bell. Original source meshes remain, with conflicting older
  details retained as hidden references. No building family was regenerated.
- Shrine stairs/landing and portal approach aligned to the original entrance.
  Seven hidden lightweight walkable contact surfaces now use the actual tops
  of the four Hall and three Shrine treads. Earlier continuous stair ramps
  remain source references, excluded from runtime walkability. Portal height
  agrees with its tread. Source/export parity was checked after the final edit.
- Truly upright actor quads: their top/bottom share world XY, retaining the
  original screen image while avoiding heads leaning into walls behind them.
- Death contact-shadow fade follows the illustrated body fade.
- Directional action offsets now follow both projected heading axes.
- Cache v36 and QA additions: real-input spatial traversal, eight-direction
  sparring hit/death/respawn, stair/nav checks and upright-quad assertions.
- Master Plan and architecture notes updated to describe the current state.
- Raw review files, videos, Blender backups and original attachments archived
  unchanged for transfer, with byte hashes and ZIP integrity verification.

## Partially completed and known problems

1. **Warrior death/fall transition remains unfinished.** The current reaction
   atlas has one hit and one collapsed death pose per direction. Runtime
   switches immediately to the collapsed pose, then fades it; there are no
   authored intermediate fall frames. The corrected shadow fade does not solve
   that visual pop. Hit recoil and all other core states still require visual
   acceptance at gameplay scale, including elevation and occlusion.
2. Eight-direction real sparring capture completed with 558 rendered actor
   frames, hit/death states and normal respawn in every direction. The complete
   new eight-direction sequence has not yet received frame-by-frame visual
   review. Functional results are not animation approval.
3. Spatial thresholds were exercised under ordinary input. The case named
   `hall-landing` stopped on the top tread at Z=.44, short of the terrace at
   Z=.45. The repository spatial QA target was subsequently moved farther onto
   the terrace (Y=15.3), but that revised case has not been rerun. Review feet
   and body transitions both up and down the actual treads in all gaits.
4. Town geometry now has spatial structure and distinct families, but some
   materials/frontages/clutter still read as simple blockout compared with the
   approved concept. Continue concept/layout comparison and actual playable
   review of district identity, road composition, grounding, density,
   occlusion, palette and controlled building variation.
5. Current v36 traversal performance, responsive/offline regression and
   physical-device performance are not certified. Historical v35 cloud idle
   sample was about 51.8 FPS for five seconds at SwiftShader pixel ratio .5;
   that is neither a v36 traversal benchmark nor mobile/hardware acceptance.
6. Live Pages inspection remained blocked by managed CONNECT proxy HTTP 403
   at `https://basicbasja-cloud.github.io/Astraeon-online/`. Do not bypass the
   network policy. Pushing this branch does not merge main or demonstrate a
   reviewed Pages deployment. A reachable deployment is still needed for live
   review. No unresolved gameplay failure was observed in the completed v36
   service/reaction runs, but broader acceptance remains open.

All three pillars remain required: concept-true Wayfarer, excellent Blender
spatial authorship with lightweight execution, and correct 2D character
animation. Production kits and the city-authoring template are mandatory
**after** Golden acceptance and **before** City 2. Do not prematurely extract
unstable Wayfarer solutions or begin City 2 now.

## Test status at the stop boundary

These are the most recent completed checks; no new implementation checks were
started for handoff:

| Check | Result / limit |
|---|---|
| `node tests/motion.test.cjs` | 44/44 passing |
| `node tests/world_v3.test.cjs` | 17/17 passing, including final stair/portal checks |
| `node tests/golden_pipeline.test.cjs` | 3/3 passing |
| `python tools/validate-world-v3.py` | Native schemas passing |
| Saved Blender export parity | Passing after final tread/source changes |
| JS syntax and edited Python compile | Passing |
| v36 eight services + travel/reload | Passing; no runtime/resource errors |
| v36 cached/direct shared depth | Passing arrival, pan and two odd phone sizes; new upright-quad assertions were added afterward and have not been rerun |
| Actual tread/gate/canopy review | Ten captured cases; no runtime/resource errors; terrace limitation above |
| Actual eight-direction hit/death/respawn | All eight completed; no runtime/resource errors; visual acceptance pending |
| Full updated browser smoke, v36 offline/responsive, traversal benchmark | Not rerun; prior v35 evidence is historical |

No known unresolved failing automated check is claimed. Earlier temporary
frontage scripts stopped when an NPC silhouette covered the final floor click;
the review harness now uses ordinary keyboard movement for a nearby final route
point. No position, HP, facing or simulation-time setter is used. Earlier failed
captures remain archived. Counts, including the historical 46 checks, must never
be treated as final approval.

## Exact next implementation step in the new task

First inspect `docs/review/spatial/v36/astraeon-eight-reactions-report.json` and
extract the corresponding raw reaction archives. Review the actual eight
direction frame sequences/video, then **author and integrate a real 2D
manifest-driven Warrior fall transition between standing and the existing
collapsed death artwork**, preserving the original reaction sources and the
directional character pipeline. No image-generation or asset job is pending.
Validate it through the existing ordinary sparring flow in the actual spatial
town. Continue the unfinished Golden loop afterward; do not start another proof
or rebuild the town. Also rerun the revised terrace case and new upright-quad
assertions before interpreting those additions as verified.

## Commands for the next task

Run from the repository root. **These commands are documented for continuation;
they were not used to regenerate anything during handoff.**

```sh
cd /workspace/Astraeon-online
# Export the current saved scene only; do not rerun a historical town builder.
blender -b authoring/wayfarer-spatial.blend --python tools/export-world-v3.py
blender -b authoring/wayfarer-spatial.blend --python tools/check-blender-export-v3.py
python tools/validate-world-v3.py
node tests/motion.test.cjs
node tests/world_v3.test.cjs
node tests/golden_pipeline.test.cjs

# Run the local browser build in a separate terminal.
python3 -m http.server 8011

# Existing QA phases use ordinary input and read-only observations.
PLAYWRIGHT_BROWSERS_PATH=/tmp/astraeon-playwright python tests/golden_wayfarer.py --url http://127.0.0.1:8011 --phase reactions --output /tmp/astraeon-next-reactions --video
PLAYWRIGHT_BROWSERS_PATH=/tmp/astraeon-playwright python tests/golden_wayfarer.py --url http://127.0.0.1:8011 --phase spatial --output /tmp/astraeon-next-spatial
PLAYWRIGHT_BROWSERS_PATH=/tmp/astraeon-playwright python tests/spatial_renderer_cache.py --url http://127.0.0.1:8011 --output /tmp/astraeon-next-depth
```

Current cloud has Blender 4.3.2, Node 24, Python Playwright, system Chromium
(`/usr/bin/chromium`), Pillow/numpy and ffmpeg. A new task must check its own
tool/dependency availability; ephemeral paths/processes do not transfer through
Git. Check browser scripts' launch options before installing a duplicate browser.

Do **not** rerun `tools/author-wayfarer-spatial.py`,
`tools/rebuild-wayfarer-golden.py`, bulk `tools/refine-wayfarer-spatial.py`, or
`tools/orient-wayfarer-homes.py` to obtain an export. The targeted
`tools/refine-wayfarer-frontages.py` changes are already applied to the saved
scene; it is preserved for provenance, not a prerequisite to export.

## Files to inspect first

1. This handoff, `MASTER_PLAN.md`, and the current sections of `ARCHITECTURE.md`.
2. `docs/review/spatial/v36/README.md`, reports, archives and
   `preservation-manifest.json`; older `docs/review/spatial/README.md` retains
   earlier iteration history and limits.
3. `authoring/wayfarer-spatial.blend`, `world/v3/wayfarer-spatial.json`,
   `tools/refine-wayfarer-frontages.py` and `tools/export-world-v3.py`.
4. `world/v3/renderer.js`, `directional-art.js`, `sprite-motion.js`,
   `warrior-rig.js`, `world/v3/locomotion.js`,
   `world/v3/warrior-animation.json`, and
   `authoring/characters/warrior-reactions-v3.png`.
5. `tests/golden_wayfarer.py`, `tests/spatial_renderer_cache.py`,
   `tests/world_v3.test.cjs`, and `tests/browser_smoke.py`.
6. `tools/wayfarer-layout-review.html` and
   `tools/building-family-sheet.html` for actual concept-role and family review.

The approved concept images remain visual authority. Attachment ZIP preserves
the original uploaded text/research; research is guidance, while user master
implementation prompts and steering amendments are requests/constraints.
Existing source art/materials/animation/export/test files remain in their
original paths. Ignored `.blend1` backups are additionally archived; caches
and backups were not deleted. No reset, revert, discard, cleanup or destructive
regeneration was performed.
