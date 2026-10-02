# Golden spatial migration — acceptance remains open

Default `index.html` now plays the saved Blender-authored Wayfarer environment,
using original materials and directional illustrated actors in one Three.js
WebGL depth buffer. This is an implementation change to the existing game.
Combat, quests, inventory, saves, skills and progression retain their existing
simulation. `?renderer=canvas` and `?world=court-legacy` are migration paths.

## Concept and family evidence

- [Concept relationships and actual authored plan](../../../tools/wayfarer-layout-review.html)
  compares a clearly labelled schematic transcription of the supplied concept
  with terrain, roads and footprints from the actual source JSON. The supplied
  image remains the art authority; the schematic is not a replacement image.
- [Building families and variants](../../../tools/building-family-sheet.html)
  renders actual exported geometry, including civic, sacred, social, crafting,
  commercial, domestic and fortified architecture. The static sheet uses 1.5×
  pixel density for legibility, and is not a performance measurement.
- `tests/golden_wayfarer.py` traverses actual authored routes, opens visible
  services and captures ordinary walk/run/sprint/turn/attack input, gate travel
  and reload. It has no actor position, gait or simulation-time setters.
- Optional `--capture-scale 1` changes only still-image raster density; motion
  and performance retain the runtime device policy. QA snapshots and rendered
  frame events observe the game. Successful checks do not approve artwork.

## Architecture evidence and decision

The bounded Canvas/Three comparison uses the same existing proof scene and
spatial contract in `tools/renderer-comparison.html`. Canvas depth sorting of
split painted layers does not generalize to the revised spatial world. Three
renders actual authored terrain, roofs, arches and raised geometry, integrates
illustrated actor quads into depth, and raycasts the same navigation surfaces.
No independent character canvas is layered above the world.

The smallest suitable current implementation uses static material batches,
low/moderate geometry, authored lighting, baked shadow coverage, actor contact
shadows and inexpensive footprint navigation. No real-time shadow maps, PBR,
GI, volumetrics, external runtime CDN or mesh physics are required. The browser
consumes Blender mesh data directly through the existing native JSON contract;
glTF is not required to retain authoring fidelity.

## Continued implementation after the checkpoint

Checkpoint `5b2011c` preserves the complete spatial migration before these edits.
Six existing residential masses now have different street-facing orientations;
their centres, original meshes, details and attached service transforms remain
in the saved scene. Authored entrance paths connect them to existing lanes.
`tools/orient-wayfarer-homes.py` edits the current scene once, without rebuilding
it. The earlier bulk refinement refuses to overwrite these later saved edits.

Existing completed foliage artwork now supplies alpha-tested leaf clusters on
crossed spatial canopy planes. Original trunks, branches and invisible low-cost
shadow proxies remain in Blender. This is not a whole-tree billboard; transparent
leaf gaps transmit both scene depth and interaction rays. Market awnings retain
their original cloth geometry and are excluded from vegetation conversion.

Software WebGL reuses static scene color **and depth**, writes that depth into
the same actor framebuffer, and redraws when the camera leaves its padded region.
The software camera aligns to actual drawing-buffer pixels to avoid pan blur;
simulation and hardware camera movement retain their existing precision. Cache
color uses sRGB storage. `tests/spatial_renderer_cache.py` compares actual cached
and direct frames and actor visibility masks during arrival, ordinary traversal
and odd-sized phone viewports. Small color rasterization differences are recorded;
these checks do not certify art quality or physical-device performance.

Actual ordinary-input review after the orientation edits traversed all districts,
opened all eight services, sampled all 24 walk/run/sprint headings, attacked,
travelled through the gate and reloaded the save. `--motion-series` records actual
rendered actor crops across a gait, with observer snapshots; it does not place,
advance or pose the character. Contact sheets are visual evidence, not approval.

## Current plaza and verification

The saved plaza now includes a circulation ring, compass inlays and an original
winged celestial fountain sculpture with thin authored water arcs. These are
additions to the existing scene; earlier geometry remains available. Geometry
face lighting now uses the same Blender-authored sun direction, strength and
ambient level as the shadow volumes. Cache version 35 delivers this iteration.

`town-review.json` records the current complete ordinary-input town run: nine
arrival/district views, eight services, 24 locomotion headings, basic attacks,
gate transition and save reload, with no runtime or resource errors.
`responsive-review.json` records four viewports and the active v35 service worker.
`offline-review.json` records an offline reload and ordinary player movement in
the current spatial town, preserving the saved character.
`depth-cache-review.json` compares the current source under cached and direct
rendering. `software-performance.json` measured about 51.8 FPS in a five-second
idle arrival sample in cloud SwiftShader at 0.5 pixel ratio, with one static cache
fill and 16 dynamic draw calls. This limited sample is not a traversal benchmark
or a physical-device performance claim. Screenshots are from the actual game.
The earlier traversal video is preserved; the current recording is separate.

The public Pages request still fails at the cloud CONNECT proxy with HTTP 403.
A reachable deployment of the active branch is needed for the remaining live
review. Local checks and captured motion do not constitute final Golden approval.

## Legacy asset migration classification

| Class | Assets and purpose |
|---|---|
| Keep temporarily | Whole-building cards in the explicit Canvas/legacy comparison and unconverted zones |
| Repurpose | Original civic, inn, forge, shrine and domestic paintings as color, facade and material references |
| Replace | Whole-building cards for default Wayfarer; terrain, walls, roofs, gates, bridge, stairs, vegetation and props now have actual authored spatial geometry |

The world/native metadata, source IDs, services, portals, patrols, UVs, collision
footprints and authored walkable/elevation surfaces come from the saved scene.
The source remains editable in Blender. Export parity checks reproduce the saved
JSON and confirm a parent move propagates through geometry, UVs and metadata.

## Review limits

The concept district relationships are implemented and actual service/traversal
regressions are recorded. Golden art/animation approval remains open: compare
all district images and the family sheet against the supplied concept, inspect
movement in real play and resolve any remaining composition/animation defects.
Do not treat the earlier 46 checks or the bounded comparison as final approval.

Cloud Chromium uses SwiftShader; software FPS and reduced raster density are not
hardware/mobile certification. The primary hardware path retains up to 1.5×
pixel density. Physical-device performance and high-frame-rate animation review
remain required. Public Pages inspection is blocked by the managed network's
HTTP 403; a repository push is not evidence of a reviewed live deployment.
