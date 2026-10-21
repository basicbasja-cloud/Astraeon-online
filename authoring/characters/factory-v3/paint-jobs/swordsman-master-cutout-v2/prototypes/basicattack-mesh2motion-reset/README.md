# Mesh2Motion attack reset

Owner direction: use Mesh2Motion and pursue a top-down sword cut with convincing body weight transfer. The working source is `Sword_Regular_B`; A, C and Combo remain comparison clips. This is a fresh source-rig study. No iteration-23 painted composite is used as a deformation master.

## Current review

- [A / B / C / Combo comparison GIF](mesh2motion-four-way-comparison.gif)
- [Native B + recovery, 60 fps one-shot](overhead-B-native-guide/overhead-B-one-shot.gif)
- [Native B contact sheet](overhead-B-native-guide/overhead-B-contact.png)
- [Compact B one-shot with the post-strike hold shortened](overhead-B-compact-guide/overhead-B-one-shot.gif)
- [Compact B contact sheet](overhead-B-compact-guide/overhead-B-contact.png)
- [Native geometry audit](overhead-B-native-guide/motion-audit.json)
- [Compact geometry audit](overhead-B-compact-guide/motion-audit.json)
- [Eight real directions, synchronized one-shot GIF](eight-direction-guides/eight-directions-one-shot.gif)
- [Eight-direction capture audit](eight-direction-guides/capture-audit.json)
- [Blender scene with exactly eight fixed cameras, default CAM_SE](eight-direction-guides/source-rig-eight-view-ready.blend)
- [Source mannequin plus blade-matched trail, all eight directions](source-trail-guide/eight-directions-with-trail.gif)
- [Canonical SE source/trail one-shot](source-trail-guide/SE/source-blade-trail-one-shot.gif)
- [Cross-direction trail timing audit](source-trail-guide/eight-view-weaponlight-audit.json)
- [Raw GLB endpoint and duplicate-target audit](source-endpoint-audit.json)
- [Source hand/grip close-up, raised guard and downstroke](source-hand-grip-comparison.png)

| Clip | Source observation |
|---|---|
| A | Low-to-high cut, ending in the raised stance that B starts from |
| B | Raised guard, downward cut with a deep body drop, free hand approaches the floor |
| C | Aerial/spinning follow-up, with large intentional body rotation |
| Combo | Chains the A/B/C movements |
| Sword_Attack | Earlier forward-extension candidate; not selected for the requested overhead cut |

## Source and endpoint correction

The immutable CC0 GLB is documented in [Mesh2Motion license evidence](../../../../motions/legal-evidence/mesh2motion-cc0-license.md). SHA-256: `406eb0a8dc4ab366e623b79b6e3005a4951392e1bda78ae39c1099d31147733c`. Blender imports the source at 24 fps. Reviews use its original mannequin and skeleton, with no canonical-rig retarget.

The raw GLB has **all 198 animation channels repeating their first value at the terminal key** in A, A_Rec, B, B_Rec, Combo and Sword_Attack. Blindly playing these terminal reset keys before recovery creates a visible pop. The review trims the reset tail and selects the recovery join from matching source poses. B uses frames 0–11 and recovery 0–22; recovery frame 23 is already influenced by its terminal reset and produces a foot dip. The compact candidate retains B 0–8 and recovery 8–22, shortening the held follow-through while preserving source pose order. A four-frame pose transition joins the source segments.

The earlier experiment adding a neutral-to-raised pose blend and forcing the final pose back to the first was **rejected**: the authored transitions slid the feet across a large source-root displacement. It is retained locally only as a diagnostic. Current one-shots preserve the native raised guard, recovery and root displacement. They do not loop or force matching first/last pixels. The per-frame root track is recorded for eventual actor-motion integration.

The review sword is a 3D proxy aligned across the curled knuckles from pinky toward index. It is not the old wrist-to-palm extension proxy. The source index/middle/ring/pinky proximal curl is approximately 77 degrees at B's raised guard and recovery entry, confirming a clenched grip. The close-up shows the hand back at the selected SE downstroke. Its final glove painting and weapon geometry still need visual approval before becoming finished art.

## Camera and inspection

Each candidate has one fixed orthographic camera fitted once to the union of its complete deformed body and blade path with a 16% margin. Source renders are 1024px. There is no frame-by-frame camera following, image recentering or image scaling. The native guide has 89 captured poses; the compact guide has 60. Both are sampled from the source action at approximately 60 fps and use a single final recovery hold in their GIFs.

The audit reuses the research silhouette IoU diagnostic from `audit_sprite_candidate.py`. IoU is not an art grade; an intentional fast strike changes the silhouette. Canvas clipping, sword endpoints, segment-join steps, foot-height proxies and root positions are reported separately. Toe-height proxies still require sole/contact review; numerical registration alone does not establish natural movement.

The compact action is also captured in **all eight unmirrored directions**, 60 poses per direction, 480 1024px PNGs. All directions share one `3.547841689` orthographic scale and start at root `(512,844.8)`, mapping to the established `(160,264)` authoring root. The camera position is fixed within each view and never follows the actor. The capture audit found zero empty or edge-touching frames and less than 0.001 px initial-root error. This passes structural capture only; it is not illustrated art or a game-map acceptance result.

Use `eight-direction-guides/<direction>/` as the authoritative future paint input. The earlier single-camera native/compact studies use a different approximate SE angle and framing; their pictures cannot be interchanged with the registered eight-view captures. The packaged `.blend` opens at frame 0, 60 fps, with exactly `CAM_S`, `CAM_SW`, `CAM_W`, `CAM_NW`, `CAM_N`, `CAM_NE`, `CAM_E`, `CAM_SE`; none has camera animation. Default view is `CAM_SE`. Per-direction manifests contain the exact projected hands, feet, sword endpoints and source-world sword positions.

Generated PNGs are packaged by clearing RGB only where alpha is exactly zero and losslessly recompressing. `png-normalization-proof.json` verifies every visible RGB pixel and every alpha value remain identical. The immutable GLB is unchanged. The compact baked Blender scene is compressed for handoff.

## WeaponLight source guide

All eight canonical views have independent transparent `WeaponLight` frames derived from their own projected grip/tip path, with one shared source-world emission schedule: first emission 11, fastest blade movement 15, last emission 18, last fade 22. Smooth subintervals follow the captured blade positions with an original plum-gray/lavender-silver/ivory gradient. The trail is thick through the actual sweep and previews behind the mannequin, leaving its face and sword visible. Every effect frame stays in bounds. This is a **source-weapon guide**, not an effect approved over the differently posed painted drafts.

## New paint study

- [Four-key-pose guide](paint-pilot/four-keypose-guide.png)
- [First full-frame paint study](paint-pilot/four-keypose-paint-v1.png)
- [Independent fresh-design study](paint-pilot/four-keypose-paint-v2-raw.png)
- [Exact prompts and provenance](paint-pilot/provenance.json)
- [Opaque-white single-frame registration/style probe](paint-pilot/single-raised-guard-white.png)
- [Its exact prompt and provenance](paint-pilot/single-raised-guard-provenance.json)
- [Adjacent painted poses versus guide anchors](paint-sequence/guide-anchor-overlay-contact.png)
- [Adjacent painted/source comparison GIF](paint-sequence/guide-vs-painted-one-shot-review.gif)

The illustrated studies read the raised strike and low follow-through more clearly than the earlier stick-guide experiments. They remain **NOT APPROVED**: the generator changes framing, hand placement and blade foreshortening between cells, and leaves colored matte fringes. A four-pose sheet is not a continuous animation. These images are not used for runtime art, whole-body warping, or a supposedly completed cutout set.

The opaque-white probe removes the colored-matte problem and explicit numeric pose targets improve sword placement. Adjacent-frame batches still move the boots and change body framing relative to the guide. `paint-sequence/` uses technical white-matte cutout and one whole-cell scale only; it does not warp, move, or resize individual figures to conceal this mismatch. The pink crosses in its diagnostic mark the guide pelvis, sword hand and toe anchors. The sequence remains a registration experiment until the full animated comparison is consistent. Planned batches are not completed frames; see `cutout-review-audit.json` for the actual count.

Actual result: **16 painted frames from four batches, out of 32 planned**. The paint/source comparison exposes toe and body registration errors and a large cape-shape change at a batch boundary. Frames 8 and 9 also touch their cell edges. The remaining four planned batches were not generated from this failing approach. Do not claim a completed 32-frame repaint or create production equipment layers or a trail over it. The source motion and eight-view guide captures are complete review artifacts; illustrated production remains blocked by pose registration and temporal continuity.

## Reproduce

```sh
blender -b --python tools/character_factory_v3/render_mesh2motion_source_review.py -- --output /tmp/m2m-source --samples 0
blender -b --python tools/character_factory_v3/build_mesh2motion_overhead.py -- --output /tmp/m2m-B-native
blender -b --python tools/character_factory_v3/build_mesh2motion_overhead.py -- --compact --output /tmp/m2m-B-compact
python3 tools/character_factory_v3/audit_motion_guide.py /tmp/m2m-B-compact
blender -b --python tools/character_factory_v3/render_mesh2motion_directions.py -- --scene /tmp/m2m-B-compact/overhead-B-source-rig.blend --output /tmp/m2m-B-eight-views
blender -b --python tools/character_factory_v3/package_mesh2motion_cameras.py -- --guide /tmp/m2m-B-compact --views /tmp/m2m-B-eight-views
python3 tools/character_factory_v3/build_mesh2motion_weaponlight.py /tmp/m2m-B-eight-views/SE --output /tmp/m2m-B-SE-trail
```

The complete eight-view captures and the compressed eight-camera `.blend` are included for handoff; exploratory single-camera scene variants stay local and can be rebuilt. The source bundle stays immutable. Remaining production work is a registered continuous high-detail repaint, true same-frame HeadHair/body/outfit/cape/weapon cutouts, WeaponLight matched to the accepted painted sword, painted coverage of all directions, and a preview on the owner's actual map.

## Current owner action split — 2026-10-21

Mesh2Motion is the preferred primary source. The old four-direction B art is **SkillOverhead**, with a separately registered copy in `skill-overhead-registered/`. `basic-attack-simple/` is the new simpler native-rig Sword_Attack compact re-evaluation (historical rejection remains retained). Both are layered review assets, not runtime-admitted artwork.

Rebuild both from retained sheets and explicit annotations:

```bash
python tools/character_factory_v3/layered_action_factory.py --action all
python tools/character_factory_v3/package_layered_factory_review.py --output /workspace/outputs
```

The source/role/state contract is `authoring/characters/factory-v3/configs/layered_action_catalog.json`. See each action README for registration, source sampling, FX timing and remaining review limits.
