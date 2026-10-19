# Astraeon Production Factory V3

## Purpose

Factory V3 is an offline authoring pipeline for illustrated 2D Astraeon sprites. Blender supplies anatomy, motion, perspective, timing, grip, depth, and stable directional guides. Its 3D output is never treated as final game art. The runtime remains the existing 2D modular sprite renderer.

The first target is the male Swordsman. V3 requires new, externally sourced Idle, Walk, and BasicAttack motions across S, SW, W, NW, N, NE, E, and SE. V2 action curves are excluded from every V3 production path.

## Branch and source audit

V3 starts from `character/production-factory-v2` at `a2e84a92b102f3cd91cc291a3425b8d6fdc0b8bb`. The V2 branch was fetched and its current head matched the checkpoint before the V3 branch was created.

V2 work retained:

- The Swordsman `painted-factory-02` source rig: 60 bones, separate cape/weapon/head-hair/body-outfit source groups, hand holdout, and equipment anchors.
- The orthographic 320×320 camera, `(160,264)` root, 176-pixel source reference height, fixed scale, eight named directions, and no mirroring.
- The V2 full-canvas modular sprite definition, metadata validators, lossless padded atlas packer, renderer, and development-only review pattern.
- Depth ordering and complete hidden surfaces as authoring inputs. Runtime still receives ordinary 2D atlases.
- The V2 identity authority at `authoring/characters/gait-rig-v50/approved-warrior-seed.png`, whose digest is pinned in the V3 identity lock.

V2 action curves and action timing were inspected only as technical evidence and then excluded. The saved V3 rig copy is expected to contain zero actions. The V2 motion source was Quaternius Universal Animation Library Standard 1/2; this bank is rejected for V3 and cannot be a fallback. The V2 swordsman visual candidates remain `DEV_ONLY / NOT_APPROVED`.

The V2 source groups combine `BodyOutfit` and `HeadHair`. The V3 paint handoff maps those guides into six logical runtime layers (`BaseBody`, `Hair`, `Outfit`, `Weapon`, `Headgear`, `BackAccessory`) and requires the artist to create separate, complete body and costume surfaces. V3 does not claim that the source mesh already provides those six painted layers.

## Canonical humanoid rig

`authoring/characters/factory-v3/rigs/astraeon_humanoid_male_v1.json` pins the source rig, 60 bone names, Z-up metric coordinates, root, core torso, neck/head, bilateral arms/hands/fingers, legs/feet, cape chain, and non-deforming foot/knee/sword controls. `.R` and `.L` are anatomical sides, independent of screen direction.

Weapon attaches to `Hand.R`; the shield/offhand anchor is `Hand.L`; headgear uses `Head`; back accessories use `Chest`; cape uses `Cape0`. These are semantic socket mappings to existing bones, not a runtime skeleton. The source's `CTRL_Sword` remains an authoring control. The V3 Blender copy removes every V2 action and action binding before it is saved.

## Motion acquisition and license policy

Source priority is MoCap Online, Rokoko, CMU Motion Capture Database, Mixamo, then other compatible free libraries. New Quaternius libraries are an evaluated low-priority fallback only. Every imported motion needs its own provider, title, source URL, acquisition date, original filename, SHA-256, original skeleton, source FPS, license evidence, retarget/modification status, and production approval state. Unknown or incomplete records block production.

The first acquisition candidates are MoCap Online's free Motion Sampler for Idle/Walk comparison and free T.C. Sword sample for BasicAttack comparison. Their official pages identify FBX as a supported format, but provider-delivered files and their checkout/license receipts are pending. Candidate selection is not visual acceptance. Compare previews at source scale and game scale, recording foot contact, weight transfer, silhouette, torso mechanics, weapon coordination, retarget cleanliness, and Astraeon fit.

The Standard License page permits modification only to prepare an integrated user creative work and restricts redistribution of source assets. It separately requires prior written permission to use MoCap Online assets in AI applications. V3 therefore defaults to a manual paint-over handoff. Do not upload a MoCap Online motion, render, or derivative guide to an AI provider until written permission is recorded in the motion provenance.

No credentials are stored. If acquisition requires owner checkout or login, the owner downloads the FBX pack and uploads its original archive and receipt into `authoring/characters/factory-v3/motions/inbox/`.

The `register_motion.py` intake tool verifies the uploaded file hash against a completed provenance record, copies the provider file byte-for-byte into the local raw-motion store, and records the path in `candidates.json`. It never approves a license or selects a motion. Raw provider files and checkout receipts are gitignored because source redistribution may be restricted and receipts may contain personal information. Preserve non-sensitive license terms and provenance with the project.

`sample_motion.py` separates source FPS from sprite frame count and writes explicit durations and semantic event times. A BasicAttack sample requires reviewed anticipation, wind-up, contact, follow-through, and recovery phase markers. It refuses to invent these phases.

## Deterministic motion pipeline

```text
immutable provider source + receipt
  → import and skeleton audit
  → configured retarget to canonical rig
  → root/floor/contact cleanup
  → semantic phase annotations
  → RPG stylization and timing edits
  → meaningful frame sampling with explicit durations
  → eight-direction Blender guide renders
  → structural QA and comparison artifacts
  → manual/approved-provider paint-over handoff
  → six-layer painted strips
  → existing V2 packer/schema/runtime
```

Raw source files are read-only inputs. Cleanup and stylization write new actions and provenance. Source FPS is recorded separately from final sprite frames and their per-frame durations. Combat actions support anticipation, wind-up, contact, follow-through, and recovery phases. Semantic events such as `footstep`, `attackStart`, `contact`, `recoveryStart`, `castRelease`, `itemUse`, and `animationComplete` live in clip metadata, not fixed historical frame numbers.

The cache key combines source-file hash, rig hash, retarget map, cleanup/stylization settings, camera contract, placeholder-prop hash, Blender script hash, and frame-sampling settings. No output from another key may enter the same build directory.

## Rendering and paint-over

Each selected source action renders the same evaluated animation state through each of the eight real camera yaws. The renderer is headless and uses the V2 orthographic camera, 320×320 canvas, and stable root. It must not mirror or independently resize a direction.

The guide set includes RGB, silhouette, depth, normal, body/group segmentation, and weapon mask. Pass manifests pin dimensions, camera, crop, root, frame, and content hashes. V2 source groupings inform masks but do not replace artist-owned 2D layer decomposition.

The current Blender renderer produces an eight-direction **rest-pose rig smoke set**. It uses CPU Cycles in headless Blender and verifies the camera and pass contract. That set is intentionally rejected by the paint provider as a production paint guide. The provider only accepts a complete animation manifest containing each required action, sampled frame, and direction.

`PaintProvider` exposes `prepare`, `paint`, `refine`, and `validate`. Built-in providers are manual handoff and disabled/no-op; external APIs or local models can be added without changing the renderer or runtime packer. A job packages identity reference, guide passes, palette and silhouette locks, neighboring accepted frames when available, semantic phases, event metadata, and QA findings. It preserves one Swordsman identity across frames, directions, actions, and equipment.

Ragnarok is not copied. It may only inform broad modular organization. No V3 AI paint-over is run while the selected MoCap license requires prior written permission for AI use.

## Modular output and runtime

Painted output keeps the six V2 logical layers: BaseBody, Hair, Outfit, Weapon, Headgear, and BackAccessory. Empty optional slots are explicit. Each image is a full-canvas layer with complete concealed surfaces so removing a cape, sword, or helmet does not reveal holes. The authoring depth map is not a runtime dependency.

The planned V3 package stage will call the existing `tools/pack-modular-sprites.py`, `assets/characters/schemas/sprite-definition.schema.json`, `tools/validate-modular-metadata.cjs`, and `modular-sprites.js`. These runtime pieces are retained; V3 has not yet produced a painted package to run through them. V3 does not add runtime 3D, Blender, or AI generation. A candidate remains `DEV_ONLY` and is exposed only through a development preview.

## QA and human review

Motion gates check source/license status, retarget bone coverage, finite transforms, stable root, ground contacts, grip stability, loop closure, and event timing. Render gates check eight-direction coverage/order, image dimensions, transparent alpha, root and scale stability, pass registration, pass presence, and in-frame bounds. Painted gates include silhouette, palette, limb count, hand/weapon consistency, and registration comparisons. Package gates run the V2 schema, atlas, pixel, and runtime validators.

Numeric QA is a filter, not visual approval. Review outputs include direction contact sheets, game-scale previews, animated and slow previews, guide/paint comparisons, and modular equipment comparisons. No tool can claim owner approval.

## Research donor review

The donor `research/modular-sprites-full-body-2026-10-11` was reviewed at `db59cc922ed1760243ffed9f07a81b891516db27`; it was not merged wholesale.

- **Adopted:** content receipts, exact frame registration, separate body/head/layer ownership, explicit `UNKNOWN`/blocked states, visible failure evidence, and human-readable comparison artifacts.
- **Adapted:** silhouette continuity and color checks into V3 validators that verify every direction and report worst adjacent-frame changes, rather than accepting only a clip mean.
- **Rejected:** treating an alpha-mask IoU alone as proof of good motion, inferring hidden anatomy from a view that cannot show it, or treating a clean source guide as final art.
- **Superseded:** donor-era procedural/painted motion experiments and any old attack bank are not V3 motion sources. V3 uses a provenance-gated new external library and the V2 runtime contract.

The donor's `img2game2d` package is Apache-2.0 with local patches. V3 adopts validation ideas and writes its own narrow tools rather than importing the patched package.

## CLI

```sh
python tools/character_factory_v3/run.py --character swordsman_male_v3 --stage preflight
python tools/character_factory_v3/run.py --character swordsman_male_v3 --stage rig --blender /path/to/blender-5.2
python tools/character_factory_v3/run.py --character swordsman_male_v3 --stage rig-review --blender /path/to/blender-5.2
python tools/character_factory_v3/run.py --character swordsman_male_v3 --stage all --blender /path/to/blender-5.2
python tools/character_factory_v3/register_motion.py --source sampler.zip --record sampler.provenance.json
python tools/character_factory_v3/sample_motion.py --action Walk --clip-report walk-review.json --output walk-samples.json
```

`all` builds the action-free V3 rig and static review set, writes a deterministic blocked paint-job record, and exits with status 2 until the required external motions have been acquired, reviewed, retargeted, and assigned `APPROVED_FOR_PRODUCTION` provenance. It never falls back to V2 actions. `preflight` also returns status 2 while the motion gate is blocked. A rig-review pass report and both full-size and 160×160 contact sheets are written under `authoring/characters/factory-v3/review/`.

## Current limits

At this checkpoint, the V2 rig/camera contracts are audited, the action-free V3 rig and static pass proof are built, and MoCap Online candidate files are pending owner download. No V3 motion has been selected, retargeted, or visually accepted. The source-specific FBX bone map is intentionally unfilled until an acquired skeleton can be inspected. Animated eight-direction guides, a production paint job, painted modular layers, runtime package, and in-game proof remain incomplete. See `PRODUCTION_FACTORY_V3_STATUS.md` for gate status.
