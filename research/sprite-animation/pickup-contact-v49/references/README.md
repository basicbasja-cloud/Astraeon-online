# External motion research, acquired and inspected 2026-10-15

The motion references below come from other creators/games. Astraeon v39/v47 neutral art supplies **appearance only**; prior own attacks/slashes are excluded as positive motion examples. Rejected native v50 attempts are negative controls, not external evidence.

## What was actually acquired

| Source | Actual evidence in this case | Use and limits |
|---|---|---|
| [Kay Lousberg / KayKit Character Animations](https://kaylousberg.com/game-assets/character-animations) | General and Simulation GLBs, CC0 notice, pinned public mirror;136 actual mesh captures with source times and23 evaluated source bones | Pickup N/SW, idle, two hit variants, floor sit down N/SW, seated idle and stand-up. Different character/camera; not exact anatomy for our drawings. |
| Ragnarok / Gravity artwork through [ragassets](https://github.com/adsonpleal/ragassets) community renderer | Eight downloaded APNGs,24 decoded exposures: pickup/idle/hit/sit × N/SW. Retrieval URLs, SHA and APNG clocks retained; originals kept in local research cache, annotated boards here. | Actual game raster observations. Three exposures are not three unique full-body poses. Preview100ms timing does not establish official game pacing or all client variants. Not artwork for production reuse. |
| [Clint Bellanger — Isometric Hero and Heroine / Flare](https://opengameart.org/content/isometric-hero-and-heroine) | Creator archive acquired and hashed.96 fixed-cell analytical crops across8rows: stance4, block2, hit/die6, cloth body plus head1. | Independent silhouette/part alignment examples. Old archive timing unavailable; no invented FPS. Row names deliberately unassigned without old exporter metadata. |

**256 captured/decoded/cropped exposures**, including repeats, are indexed in `external-observations.json`; this is an acquisition count, not256 independent poses or a quality/accuracy score. General contains15 actual clips; Simulation contains14. Creator marketing totals are not the acquired counts. No UAL2/Mixamo/video acquisition is claimed in this new case.

KayKit mirror is pinned to `af08a62d3669370ec4636ae6314b38cdcd5dd759`; see `kaykit-retrieval.json`. Model, action, camera, evaluated time, raster SHA and bone coordinates are in `kaykit-captures.json` / `kaykit-sit-captures.json`. The source files are external skinned mannequins; no own Astraeon rig is rendered and relabeled as an external reference. Captures use local Blender4.3.2,256×384 and fixed orthographic N/SW cameras defined in the scripts.

Kay Lousberg's [CC0 notice](KayKit-CC0-License.txt) accompanies the GLBs and derived captures. Flare boards are adapted excerpts of **Isometric Hero and Heroine, Clint Bellanger, [CC BY3.0](https://creativecommons.org/licenses/by/3.0/)**. Changes: cloth/head composite at unchanged source coordinates, fixed-cell crop, nearest-neighbor enlargement, dark analytical background and labels. We use no leather textures or weapons, so their additional credited sources are not included. See `flare-retrieval.json` / `flare-capture.json`. Ragnarok artwork remains owned by Gravity; community service provenance is not a redistribution or production-art license.

## Findings that change the work

1. KayKit PickUp keeps foot/toe bone origins nearly fixed (~0.000406m maximum sampled range), while head/torso and reach change. RO pickup likewise holds visible shoe placement during a bent pose. This supports fixing our floor drift while preserving the requested deep bend. KayKit's milder bend does not require replacing our acting with its exact pose.
2. Source bone origins do not identify shoe contact surfaces. v49 is accepted by independent actual raster measurements, not by the KayKit or earlier own-rig foot numbers.
3. KayKit Idle_A has almost stationary foot origins. Its source curve is nearly symmetric. Sampling16times can yield8distinct rendered target states; do not manufacture a unique-pose count by renaming duplicate images.
4. Hit_A includes about0.049m fore/aft foot motion; its projection shifts about2.47px at this camera. v50 explicitly adapts the clip to an in-place light reaction instead of claiming an exact retarget. Hit_B has a left step (~0.248m displacement and0.059m lift). A both-feet-planted gate would reject that legitimate stepping action for the wrong reason.
5. Sit_Floor_Down changes foot orientation/location and transfers support toward the pelvis. Do not lock both shoe silhouettes through the whole action or normalize the shorter seated body to standing height. Sit-down and stand-up have independent clips; reversing frames is not proof of correct stand-up mechanics. Current seated references are acquired; no finished Astraeon seated drawing is claimed.
6. RO and Flare demonstrate full-body pose banks with separately registered head/equipment layers. A flattened research sprite and an ORA are not automatically a replaceable complete-head/body bank.

Boards: `kaykit-PickUp-{N,SW}-analysis.png`, `kaykit-Idle_A-N-analysis.png`, `kaykit-Hit_{A-N,B-SW}-analysis.png`, `kaykit-Sit_Floor_{Down-N,Down-SW,StandUp-N}-analysis.png`, `ro-swordsman-*-analysis.png`, `flare-*-analysis.png`. Observations apply only to these acquired versions, rows and timestamps.

## Technical sources read during this investigation

- [Spine weights](https://en.esotericsoftware.com/spine-weights), [meshes](https://en.esotericsoftware.com/spine-meshes), [skins](https://en.esotericsoftware.com/spine-skins): use a shared rest-space deformation/appearance contract; small-motion reuse does not recover unseen painted surfaces. These inform our original implementation; no Spine runtime is copied or required.
- [Kovar et al., Footskate Cleanup](https://research.cs.wisc.edu/graphics/Gallery/FootskateSolver/footskate.html) and [project/paper](https://research.cs.wisc.edu/graphics/Gallery/kovar.vol/Cleanup/): contact intervals and changing support matter. Our visible-window tool is not an implementation or validation of the full physical solver.
- [Ragnarok ACT](https://ragnarokresearchlab.github.io/file-formats/act/) and [animation systems](https://ragnarokresearchlab.github.io/rendering/animation-systems/): part offsets and action/direction/timing conventions; community documentation, not an official game capture.
- [Godot4.4 AnimatedSprite2D](https://docs.godotengine.org/en/4.4/classes/class_animatedsprite2d.html): preserve a single frame/progress clock independently of sprite rendering and appearance. Our player is standalone, not a tested Godot integration.
- [Quaternius Universal Animation Library2](https://quaternius.com/packs/universalanimationlibrary2.html): creator page located/read; no new asset from that page acquired in v49. Previous corpus acquisitions remain separately documented.

Public reads and local rendering only. No paid provider/API, credits, credentials, model training or third-party upload. Native image-tool billing is unknown; do not describe host generation as verified free.
