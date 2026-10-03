# ASTRAEON local handoff — 2026-10-04

## Checkpoint

- Branch `codex/world-pipeline-v3-proof`; remote `https://github.com/basicbasja-cloud/Astraeon-online.git`.
- Continuation starts at `f3dd31635719c8fa2fad4796169445071f89c2f8`; intermediate v43 checkpoint is `31a429305a55da49abab20d139ae7d489d934f07`. Read the latest commit with `git log -1 --format=%H`.
- Runtime/cache version **47**, layout `wayfarer-painterly-civic-town-v47`.
- Golden visual approval remains pending. The concept supplies identity/composition rather than an exact diagram. City 2 remains gated by Golden acceptance and the master plan's mandatory productionization phase.

## Authoritative source

`authoring/wayfarer-spatial.blend` matches `world/v3/wayfarer-spatial.json`: 117 object records, source about 58 MiB. Geometry, contacts, individually owned lots, services, portals, patrols and UVs remain in the saved scene. Hidden older geometry is retained as reference.

Do not rebuild this scene from historical builders or rerun numbered migrations on the current source. The v44–v47 tools record sequential, mostly one-time edits; some deliberately shift placements. Open the saved current source, make a targeted edit, save and export. Character registration through `tools/register-warrior-run-v44.py` is reproducible.

## Implemented continuation

- Four times the previous land area, 112 × 128 world bounds, connected civic spine/district loops, twelve individually assembled frontage lots. Full-width streets and closing patrol legs clear physical building geometry.
- Projecting upper storeys, window bays, dormers, curved roof profiles, arched doors, balconies and commercial awnings. Hall: broad faceted dome, unequal towers, deep entrance, blue/gold identity and arched forecourt loggias.
- Irregular central court, gently bent lanes, grouped irregular planted beds, new lanterns, controlled road flowers and layered river-bank strata. Cottage parent ownership and the forge-frontage tree were corrected after gameplay inspection.
- Cohesive painterly palette, broad restrained variation, quieter water, upward floor lighting and warm light/cool shade. A 2048 static cast/contact atlas projects onto one highest-floor receiver per half-unit cell.
- Feathered exposed paving verges and shallow shoreline ribbon, with no collision or interaction ownership. Up to four obstructing building owners fade smoothly to 16% transparency while retaining collision and cast shadows.
- Larger illustrated actors, sprite mipmaps disabled, shared preuploaded GPU atlases. Canvas remains for actions/falls and other zones.
- Original 64-frame/eight-direction run replacement. All 192 movement frames have measured boot soles and support/flight metadata. Registration rejects higher sword/cape tips; aerial source poses are not forcibly planted. Visible support locks use bounded whole-body translation, not procedural limb overlays.
- Movement views immediately face actual travel; aiming retains smooth world rotation. Audio prepares before first movement, removing the observed first-step device-initialization hitch.
- Exact collision/elevation behind an 8-unit broad phase; bounds-derived A* budgets and 1-unit large-town spacing restore long cross-town paths.

## Camera and research

The town uses the RO community 15-degree lens, yaw 0, zoom 125 and centered follow. Pitch is **46 degrees**, deliberately shallower than the community reference's 50 after user steering. Wheel steps 15 within 65–325; right-drag rotates, Shift tilts, Ctrl zooms, with corresponding double-right-click resets. Tilt stops at 89 to avoid a projection singularity. Picking, rays, directions and input share the orientation.

`research/ragnarok-community-repositories.txt` inventories 58 catalog entries. `research/wayfarer-applied.md` distinguishes directly inspected community clients/formats/editors/servers, official RO3 announcements, published trailer screenshots and Tree of Savior/Albion/CrossCode comparisons. RO3 imagery informs mood and broad shape/material/shadow grouping; the 600 × 338 published town frame cannot establish native texture dimensions. The official developer diary's video returned YouTube error 153 and was not claimed as watched. No reference-game pixels ship here.

## Verification and evidence

Final reports and representative captures are in `docs/review/wayfarer-v47`; consult that README for completed results. Checks cover Node tests, public schemas, saved-source parity, normal-input camera controls, district/stair/gate traversal, all services, 24 gait cases with rendered sole telemetry, eight hit/death/respawn directions and sound-on frame timing.

Raw captures and earlier working views remain under `C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation`. Fixed-view tools use disposable saves for art comparison; gameplay tests use ordinary input, read-only snapshots and native route queries. Simulation-foot checks alone did not detect the rear-view registration issue. Local timing uses Chrome D3D11 / Radeon 780M; it is not universal or phone certification. Tests do not grant Golden art approval.

## Windows tooling

Serve the checkout at `http://127.0.0.1:8011` with `python -m http.server 8011 --bind 127.0.0.1`. No build/npm step is required. Set `ASTRAEON_BROWSER` to local Chrome for Python Playwright.

The Blender 4.3.2 app hit a Windows SideBySide startup failure. Official bpy 4.3.0 works with matching bundled Python 3.11:

```powershell
$env:PYTHONPATH='C:\Users\Lenovo\AppData\Local\AstraeonTools\bpy43'
& 'C:\Users\Lenovo\AppData\Local\AstraeonTools\blender-4.3.2-windows-x64\4.3\python\bin\python.exe' tools/run-bpy-task.py authoring/wayfarer-spatial.blend tools/check-blender-export-v3.py
```

Original source backup: `C:/Users/Lenovo/AppData/Local/Temp/astraeon-local-preparation/wayfarer-f3dd316.blend`.

## Remaining product scope

Human Golden review, other-class locomotion consistency, civilian variety, richer skill art and real-phone performance remain broader production work. The game is a local simulation without live multiplayer/server authority/account sync. After accepted Wayfarer, complete reusable tools/kits and city-template productionization before full City 2 work.
