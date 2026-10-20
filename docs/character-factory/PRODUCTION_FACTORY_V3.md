# Astraeon Production Factory V3

## Purpose and progression

Factory V3 turns the useful V2 authoring, framing, packing, validation, and runtime work into a repeatable pipeline for illustrated 2D characters. A rigged 3D character supplies pose, timing, perspective, weapon placement, depth, and consistent eight-direction guides; it is not final game art.

The first Swordsman vertical slice has passed the technical pipeline through a development preview: new source motions, provenance, retargeting, cleanup, sampling, 192 eight-direction guide records, six structural passes, generated painted candidates, runtime packages, and browser playback. The owner rejected the map used for that browser preview. New full-frame Idle, Walk, and BasicAttack masters now have registered body, head/hair, outfit, sword, cape, and effect cutouts that reconstruct to their sources exactly. Visual approval, the requested-map preview, replacement-safe hidden surfaces, and the remaining actions are still outstanding. Factory V3 is **not complete**.

Current branch: `character/production-factory-v3`, based on `50583de` (`Add character factory V3 foundation and rig proof`). See [the status and handoff](PRODUCTION_FACTORY_V3_STATUS.md) and [the generated motion evidence](evidence/production-factory-v3-motion.json).

## What V3 keeps and rejects from V2

V3 evolves the V2 engineering foundation. It retains the proven orthographic framing, 320×320 guide canvas, stable root near `(160,264)`, eight real directions, modular sprite definition and atlas conventions, packers, validators, identity reference, depth/occlusion concepts, and actual runtime integration. The 60-bone canonical rig is derived from the existing Swordsman authoring setup and is copied into a V3 action-free source scene.

The owner rejected the look of the old V2 motion bank. V3 does not reuse its curves, frame timing, or fallback animations as production motion. The source rig manifest records 17 removed V2 actions and zero remaining actions. Old V2 work remains a technical reference and regression baseline only.

## Motion source policy and current selection

The source hierarchy is free MoCap Online candidates, legally usable Rokoko sources, CMU, Mixamo, then other compatible free mocap or animation sources. The registry marks the MoCap Online sampler, T.C. Sword, and Mixamo candidates `BLOCKED_ACCESS_REQUIRED`; using those specific candidates would require an owner-provided download and license evidence. Two tracked free Rokoko candidates remain `NOT_ATTEMPTED_TIER_2`. The user directed the search toward another free source and later approved Mesh2Motion as an option, so the current Idle and Walk candidates use Mesh2Motion's public human animation bundle. Its initial `Sword_Attack` candidate is now rejected after pose-guide comparison; no replacement has been selected.

The bundle is pinned to Mesh2Motion repository commit `653a9698f5f315523072f1c3ff3496100401317b`. Its official repository states CC0 1.0 for the models, rigs, Blender files, and animations. The selected source is `human-base-animations.glb`, a 66-bone, Z-up, -Y-forward human rig at 24 FPS, SHA-256 `406eb0a8dc4ab366e623b79b6e3005a4951392e1bda78ae39c1099d31147733c`. Source URL, license evidence, acquisition record, and hash are in [LICENSE_EVIDENCE.md](../../authoring/characters/factory-v3/motions/LICENSE_EVIDENCE.md) and [the CC0 evidence](../../authoring/characters/factory-v3/motions/legal-evidence/mesh2motion-cc0-license.md). The source file is locally cached under the ignored `motions/raw/` directory; the pinned URL and hash allow a verified re-download.

| V3 action | Selected source action | Decision |
|---|---|---|
| Idle | `Idle_Sword` | Sword-ready stance reads at 160px; breathing and weight shift are subtle, so it remains a candidate. |
| Walk | `Walk` | Side views show step changes; the front view reads more subtly. Keep as a candidate pending visual approval. |
| BasicAttack | `Sword_Attack` | Rejected after direct frame-by-frame guide comparison: the sword is pushed forward and held through frame indices 4–8, so the gesture reads as a thrust. A replacement source and guide are required. |

The earlier Quaternius and CMU selections were rejected after game-scale review. Mesh2Motion `Sword_Regular_A` folded too far forward, `_B` stayed too low, and `_C` failed rotation-spike QA. Candidate decisions and evidence are tracked in [candidates.json](../../authoring/characters/factory-v3/motions/candidates.json). A Mixamo FBX profile remains available for a future supplied source; the current build does not depend on Mixamo or an account.

Every imported motion has a provider, source URL and title, file hash, source format and skeleton, FPS and duration, license evidence, commercial-use and retarget permissions, modification status, and production status. Authenticated providers are never handled by storing credentials in the repo: if a chosen free source needs an interactive login, pause that acquisition and request owner assistance. Once an asset is acquired and its evidence is recorded, normal builds run from the local hash-checked file without logging into a provider.

## Canonical rig and retargeting

The V3 canonical rig has 60 bones, stable root, hand and accessory sockets, and zero V2 actions. The Mesh2Motion profile maps source bones onto the canonical motion set:

| Canonical | Mesh2Motion source | Canonical | Mesh2Motion source |
|---|---|---|---|
| `root` | `root` | `Hips` | `pelvis` |
| `Spine` | `spine_01` | `Chest` | `spine_03` (fallback `spine_02`) |
| `Neck` | `neck_01` | `Head` | `head` |
| `Clavicle.L / .R` | `clavicle_l / clavicle_r` | `UpperArm.L / .R` | `upperarm_l / upperarm_r` |
| `Forearm.L / .R` | `lowerarm_l / lowerarm_r` | `Hand.L / .R` | `hand_l / hand_r` |
| `Thigh.L / .R` | `thigh_l / thigh_r` | `Shin.L / .R` | `calf_l / calf_r` |
| `Foot.L / .R` | `foot_l / foot_r` | `Toe.L / .R` | `ball_l / ball_r` |

GLB import uses Blender's glTF importer and selects the action from the imported GLB action/slot. Retargeting copies mapped bone rotations onto the canonical rig, estimates height from head and toe bones, preserves the in-place root policy, and strips imported source objects/actions after baking. Cleanup validates finite transforms, required mappings, stable root, floor/contact windows, and rotation spikes. Selected clips pass these checks; rendered root horizontal excursion is zero and floor correction was not needed (maximum lift `0`).

The current Mesh2Motion stylization keeps source time (`1.0×`) and applies restrained rotation emphasis: Hips `1.02×`, Spine `1.04×`, Chest `1.05×`, upper arms `1.02×`, thighs `1.02×`, other bones `1.0×`. This preserves human joint movement while giving the fantasy strike a little more readable torso and arm action. Visual judgment remains a separate owner gate from numeric QA.

## Sampling, events, and visual review

The source runs at 24 FPS. The first painted pilot used eight poses per action and showed the loop pop and stutter the owner identified; those images are no longer accepted as smoothness evidence. A replacement 16-frame sampling plan is recorded in `motions/retargeted/16frame-candidate/`: Idle and Walk cover `[0,1)` without duplicating the endpoint, and BasicAttack is sampled once with its semantic phases intact. The full-master artwork and cutouts must be repainted at that 16-frame timing before a new sprite package is built.

| Action | Duration | Loop | Events and semantic phases |
|---|---:|---|---|
| Idle | 2100 ms | Yes | Completion at phase `1.0` / 2100 ms. |
| Walk | 1668 ms | Yes | Left footstep phase `0.0` / 0 ms; right footstep phase `0.5` / 834 ms; completion at 1668 ms. |
| BasicAttack | 1966 ms | No | Anticipation start phase `.12` / 236 ms; wind-up `.28`; provisional maximum-extension marker `.50` / 983 ms; follow-through `.63`; recovery starts `.84` / 1651 ms; completion at 1966 ms. The `.50` marker is not a validated hit because this motion is rejected. |

An earlier audit incorrectly described source frames 24–33 as a lateral sword sweep and moved contact to phase `.63`. Direct comparison of the actual SE guide contradicts that call: frame indices 4–8 hold a forward extension and read as a thrust. The `.63` contact claim is withdrawn. The timeline now uses `.50` only as a provisional maximum-extension marker while the attack source is rejected; no motion curves, sampled poses, or frame durations were changed. The source and guide remain historical review evidence until a suitable replacement is selected.

The existing eight-frame timing and motion evidence remain historical pilot records. The replacement per-frame timings, event indices, and phases are in the 16-frame candidate plan. Eight-direction 160px sheets provide the visual review scale:

- [Idle sheet](evidence/v3-game-scale-idle.png)
- [Walk sheet](evidence/v3-game-scale-walk.png)
- [BasicAttack sheet](evidence/v3-game-scale-basicattack.png)

Current human-read review: Idle reads as a sword-ready human but its breathing remains subtle; Walk shows step changes more clearly from side views than the front. BasicAttack is rejected because its long forward extension reads as a thrust, not the requested lateral fantasy cut. The separate SE effect-only trial uses a broad plum-gray to lavender-silver to warm-ivory gradient; it follows the timing of the rejected guide and does not fix the body or sword gesture. The eight-frame painted previews are retained as an explicitly rejected smoothness pilot in the [handoff](PRODUCTION_FACTORY_V3_STATUS.md).

## Camera and structural guides

`CAM_FantasySprite` is orthographic at 320×320 with root pixel `(160,264)`, stable common character height, and no mirroring. All eight views derive from the same sampled action state:

| Direction | Yaw |
|---|---:|
| S | 0° |
| SW | -45° |
| W | -90° |
| NW | -135° |
| N | -180° |
| NE | -225° |
| E | -270° |
| SE | +45° |

Each of the 192 guide records contains aligned RGB, silhouette, depth, normal, body-segmentation, and weapon-mask passes. Manifested camera, crop, root, frame, direction, and image hashes are validated. Structural guide QA passes all six passes and eight directions; contact sheets are retained as compact review evidence.

## Paint-over stage and modular output

The paint stage is provider-neutral. `PaintProvider` defines `prepare`, `paint`, `refine`, and `validate`; the manual provider builds an artist handoff keyed by guide and identity hashes. Two ImageGen paint iterations contain eight-direction Idle, Walk, and BasicAttack sheets. Iteration 2 uses exact sharper fantasy-art prompts and is retained as a separate review candidate: [paint job `imagegen-swordsman-v2`](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-v2/selection.md). Its importer applies alpha cleanup, connected-component filtering, one shared scale across 192 cells, guide-root alignment, and a dilated guide-silhouette mask. The earlier v1 requests remain alongside their outputs for comparison.

The owner selected a master-frame cutout flow for modular art. Keep the V3 motion frames and timing, paint one whole-character master for each view/frame, then cut labelled parts from that same master. `cutout_master_sheet.py` enforces complete frame labeling and exact recomposition; `review_layered_sheets.py --preserve-cutout-registration` builds visual reviews without changing source pixels. The current pilot has eight frames per action and reconstructs with `0` mismatches, but the owner identified its loop seam, sparse poses, and both attack trail designs as defects. Sixteen-frame replacement timing plans and Idle, Walk, and BasicAttack pose guides are ready in [paint-job v2](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/README.md); matching painted masters and cutouts are still required. The first `WeaponSlash` vector pilot is rejected because it crosses the character and does not track the sword. Use a separate `WeaponLight` sheet, registered to each attack frame and facing, following the layer synchronization pattern in the Goro client renderer. `import_layered_sheets.py` accepts `WeaponLight/basicattack.png` and leaves it transparent when no reviewed source exists; it ignores the rejected legacy `WeaponSlash` input. The aligned flat-color masks supply labels only—the cutouts take their original art pixels from each full master. `refine_headhair_labels.py` adds nearby visible face pixels to the hair label seed; its heuristic mask still needs inspection, and `Headgear` remains empty. GIFs and layer breakdowns are review material, not approval. Hidden base surfaces still need painting before outfit, hair, cape, or weapon swaps. The previous independent-layer ImageGen experiment is retained as rejected continuity evidence in [its paint job](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-layered-v2/README.md); all three current actions are documented in [the master-cutout handoff](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/README.md).

For internal motion review, a deterministic raster treatment builds one shared 96-color palette from all 192 guide poses, applies a 38% palette-quantization blend, a mild warm grade, low-contrast smoothing, and warm normal-derived edges. This is explicitly a **procedural review candidate**, not the final illustrated art or a substitute for the manual paint stage.

The runtime definition exposes six logical slots: BaseBody, Hair, Outfit, Weapon, Headgear, and BackAccessory. Current source meshes only support BodyOutfit combined, HeadHair combined, Sword, and a separately segmented Cape. The procedural package defaults BackAccessory to a transparent part while retaining the cape as an optional alternate. The painted candidate is a single fused Body/Hair/Outfit/Weapon composite with transparent remaining slots; it is not independently customizable. The package does not invent independent Outfit or Headgear pixels. Hidden-surface correctness for equipment changes is not production-qualified. Independent painted layers and their under-surfaces must be supplied or created before modular production approval.

## Runtime integration and current QA

The procedural review package is `assets/characters/swordsman-male-v3/sprite.json`: 160×160 frames, runtime root `(80,132)`, reference height 88px, eight unmirrored directions, nine clip definitions (three selected clips and six static placeholders), schema pass, and 82,301,760 decoded atlas bytes. The separate painted candidates are `assets/characters/swordsman-male-v3-painted/sprite.json` and `assets/characters/swordsman-male-v3-painted-v2/sprite.json`; both use the same cell/root contract, three painted clips plus six pending placeholders, schema pass, and 20,763,712 decoded atlas bytes each. All are `DEV_ONLY`; none is approved or production-admitted.

The historical review route is `?qa=1&swordsman=v3-painted-v2` and used the default streamed Wayfarer Capital map. It loaded iteration 2 in the character creator and Swordsman player renderer and played Idle/Walk/BasicAttack without V2 motion fallback. The owner later identified Wayfarer Capital as the wrong map for acceptance. Keep that browser run as technical evidence only; it does not satisfy the requested-map review. The BasicAttack contact marker was at 983ms. The route is development-only and the fused painted composite does not provide equipment swaps or final game admission.

Latest generated evidence reports: canonical rig and source hash pass; required retarget mappings, finite transforms, root stability, and no rotation spikes pass; 192 frame/direction records and six structural passes pass; runtime schema and package validation pass; paint handoff exists. The BasicAttack production gate is blocked because its motion source is rejected after visual review; numeric QA cannot approve visual quality. Final painted output, six independent layers, an attack replacement, and owner approval are incomplete.

The 2026-10-20 high-resolution frame-499 pose-fit pilot was also rejected. All four guides fail the `0.78–1.12×` limb-segment preflight; the whole-body warp would stretch the painted torso `1.691–1.737×` to match the mannequin, compress a forearm to `0.509×`, and fold 29 triangles across frames 480, 493, 499, and 511. The comparison and decision are recorded in [iteration 23's pose-fit report](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-23/experiments/rig-highres-master-001/README.md). The next master must be painted in the exact Blender pose before same-frame cutouts; canvas registration is not a substitute for pose fit.

## Commands

```sh
python tools/character_factory_v3/run.py --character swordsman_male_v3 --stage preflight
python tools/character_factory_v3/run.py --character swordsman_male_v3 --stage all --blender /path/to/blender-5.2
python tools/character_factory_v3/register_motion.py --source animation.fbx --record animation.provenance.json
python tools/character_factory_v3/sample_motion.py --action Walk --clip-report walk-review.json --output walk-samples.json
python -m unittest discover -s tests/character_factory_v3 -v
node tools/character_factory_v3/validate_runtime_package.cjs
```

The pipeline verifies selected source hashes before retargeting and does not silently switch candidates or fall back to V2. `Run`, `Hit`, `Death`, `Dash`, `Guard`, and `SkillAction` remain static review placeholders; they are outside the first required three-action slice and require separately sourced, reviewed motion before production use.
