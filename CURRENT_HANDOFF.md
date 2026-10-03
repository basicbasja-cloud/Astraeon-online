# ASTRAEON local handoff - 2026-10-03

## Checkpoint

- Branch: `codex/world-pipeline-v3-proof`; remote: `https://github.com/basicbasja-cloud/Astraeon-online.git`.
- Starting HEAD: `f3dd31635719c8fa2fad4796169445071f89c2f8`. This local continuation has not been pushed or deployed. Read the current local commit with `git log -1 --format=%H`.
- Cache version: **43**. Default town camera: **classic Ragnarok reference**.
- Golden Wayfarer acceptance and the mandatory later productionization phase remain open. This checkpoint does not release City 2 production.

## Authoritative source

`authoring/wayfarer-spatial.blend` matches `world/v3/wayfarer-spatial.json` (101 object records). Existing services, stairs, gameplay and transitions remain in the current source. Original weak architecture is retained as hidden reference geometry. Do not rebuild this scene from historical builder scripts.

The town uses vendored Three.js with illustrated upright world quads in the same depth buffer. Canvas assembles actor textures and renders UI/effects; other zones retain their established renderer. Source meshes, walkable contacts, solids, service anchors and portals feed existing navigation and simulation.

## Implemented concept pass

- Hall: nave, aisles, unequal towers, bell lantern, pointed windows, rose compass, portal, blue slate and gold roof detailing.
- Connected public paving, grass courts, garden/canal edges, larger winged fountain monument, balconies, awnings and facade details.
- Eight individually composed district buildings, three market stalls, raised curtain walls, ten watchtowers, banners, outward-facing rocky banks and original painted rock material.
- Eight planted civic trees, five flower courts, fifteen street lamps, six benches and twelve shrub groups.
- Fixed the Residential review waypoint; Hall terrace approach is at the actual 0.455 contact height. Moved the southwest lodge after a playtest found it obscuring the Artisan.
- Final overview caught lamps in the canals and bridge geometry left at the obsolete western gate. Lamps now stand on the banks; deck, parapets and piers match the existing southern contact surface. Final normal-input crossing passed.
- Compatible static materials batch together. Direct perspective rendering uses antialiasing. Legacy software caching keeps its pixel-grid raster policy; animated water and transparent shadow receivers composite each frame, preserving direct-render colors and depth.

## Camera

`world-view.js` defaults to 15-degree vertical FOV, 50-degree downward pitch, yaw 0, zoom 125 and centered follow. Reference: roBrowserLegacy Camera, Camera preferences and Renderer source, linked in `research/wayfarer-applied.md`. This is community evidence rather than an independent Gravity-client audit.

Wheel zoom steps 15 within 65-325. Right-drag rotates, Shift-right-drag tilts, Ctrl-right-drag zooms; double-right-click resets the corresponding parameter. Tilt is bounded at 89 degrees to avoid an upright-sprite projection singularity. Map-unit scale and smoothing are adapted to this game. Rays, input, sprite direction and visible picking share the current orientation. Earlier camera profiles remain explicit URL comparisons.

## Warrior animation

`world/v3/warrior-painted-locomotion.json` registers walk/run/sprint: 8 directions x 8 chronological complete-body frames each. Runtime atlases are `assets/warrior-{walk,run,sprint}-v4.webp`. No procedural legs or additional flight bob are added to these frames. Movement simulation remains separate.

Sources and reproducible registration are in `authoring/characters/painted-v4/README.md`. A seven-direction sprint source needed a separate SW strip. Temporary complete run-pose repairs were subsequently replaced by full new NW strips for all modes and a full W sprint strip. Both intermediate and final provenance are preserved. Existing eight-direction reactions, fall transition, attacks and skills remain.

## Research

`research/ragnarok-community-repositories.txt` inventories 58 entries from the public community catalog. `research/wayfarer-applied.md` records inspected client, renderer, file-format, authoring and server references, Gravity's RO3 announcements and Tree of Savior, Albion and CrossCode comparisons. The inventory is broader than the directly inspected source subset; do not claim every repository or the proprietary RO3 engine was audited.

## Verified evidence

- 67 Node tests pass; public scene/animation schemas pass.
- Saved source/export parity and shared parent transform checks pass after the final authored edit.
- Normal-input camera test checks defaults, independent physical perspective equivalence, orbit, tilt, zoom, resets and rotated ground navigation.
- Complete town playtest: 8 stair/gate cases, all 8 districts in desktop/portrait/landscape/tablet viewports, all 8 services, walk/run/sprint in 8 headings, turns, attacks, hit/death/respawn in 8 directions, field transition and save reload; no runtime/resource errors.
- Final service replay after furniture passes. Legacy cache/direct comparisons pass at arrival, after pan, odd portrait dimensions and landscape, including identical actor depth masks.
- Representative evidence is in `docs/review/wayfarer-v43`; full local artifacts remain in `C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation`.

Hardware captures use Chrome D3D11 / Radeon 780M. Record observed renderer timings as local measurements, not universal FPS or phone certification. The complete gameplay run precedes final material/furniture-only polish; the final source has additional parity/schema/unit checks, service replay and still review.

## Windows tooling

Local preview: `http://127.0.0.1:8011`. Server is rooted at this checkout.

Official Blender 4.3.2 application hit a Windows SideBySide startup failure. The source was opened, edited, saved and exported with official bpy 4.3.0 using the matching bundled Python 3.11:

```powershell
$env:PYTHONPATH='C:\Users\Lenovo\AppData\Local\AstraeonTools\bpy43'
& 'C:\Users\Lenovo\AppData\Local\AstraeonTools\blender-4.3.2-windows-x64\4.3\python\bin\python.exe' tools/run-bpy-task.py authoring/wayfarer-spatial.blend tools/check-blender-export-v3.py
```

Original clone source backup: `C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation/wayfarer-f3dd316.blend`. The saved current source is authoritative; targeted `reauthor/refine` scripts document this pass.

## Remaining quality work

Golden visual approval is pending. Prioritize additional architectural sculpting and district character, civilian variety, rear/action consistency for other classes, richer skill visuals and real phone performance. Keep comparing the playable views to the supplied concept. Do not equate test passes with concept fidelity or call the local simulation a completed MMO. After accepted Wayfarer, complete the required reusable tools/kits and city-template productionization before full City 2 work.
