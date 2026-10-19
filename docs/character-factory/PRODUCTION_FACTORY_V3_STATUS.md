# Production Factory V3 status and handoff

**Branch:** `character/production-factory-v3`

**Base:** `50583de` (`Add character factory V3 foundation and rig proof`)

**Target:** Male Swordsman

**Current state:** `TECHNICAL_PASS / INTERNAL_VISUAL_CANDIDATE / OWNER_APPROVAL_PENDING`

**Art/runtime admission:** `DEV_ONLY / NOT_APPROVED`

The first three-action vertical slice now runs through source intake, retargeting, guide rendering, structural QA, paint handoff, runtime packaging, and the actual Astraeon development preview. The latest clean forced headless build used Blender 5.2.2, cache key `1b940eadbbbd308a`, and paint handoff `93df90a93cbddbef28a65319`. The selected motions are new Mesh2Motion clips, not V2 curves. The attack is now a readable fantasy sword sweep with recovery, replacing the awkward forward-bent attack. The technical route is in place; the package is not final game art and has not been owner-approved.

## COMPLETE

- Built the 60-bone canonical V3 Swordsman rig with a stable root and zero remaining V2 actions.
- Rebuilt and headlessly checked the rig with Blender 5.2.2; the [eight-direction rig smoke QA](../../authoring/characters/factory-v3/review/rig-smoke-f6fe30023e77/qa.json) passes all six structural passes.
- Selected Mesh2Motion `Idle_Sword`, `Walk`, and `Sword_Attack` from a pinned CC0 source. Recorded exact source hash, license evidence, skeleton, and action provenance. No account is needed for this source.
- The MoCap Online sampler/T.C. Sword and Mixamo candidate records are `BLOCKED_ACCESS_REQUIRED`; the tracked free Rokoko candidates are `NOT_ATTEMPTED_TIER_2`. The user allowed a free alternate source and approved Mesh2Motion, so no login or credential was needed for the current set.
- Implemented hash-checked BVH/FBX/GLB/BLEND intake, source profiles, GLB action selection, retargeting, cleanup, semantic sampling, caching, structural QA, and a provider-neutral paint handoff.
- Retargeted and reviewed the three selected clips. The chosen attack is an energetic low sweep with controlled recovery. Rejected Quaternius/CMU picks and Mesh2Motion `Sword_Regular_A/B/C` have reasons recorded in the candidate registry.
- Rendered 192 guide records: eight sampled frames per action across eight real directions, with RGB, silhouette, depth, normal, body segmentation, and weapon mask. Structural QA passes.
- Created the manual paint job [`93df90a93cbddbef28a65319`](../../authoring/characters/factory-v3/paint-jobs/93df90a93cbddbef28a65319/job.json) and the internal procedural runtime candidate.
- Runtime schema and atlas validation pass. The V3-only development route loaded the package, played BasicAttack, followed its contact event timing, and returned to Idle without page or console errors.
- Reviewed the [Idle](evidence/v3-game-scale-idle.png), [Walk](evidence/v3-game-scale-walk.png), and [BasicAttack](evidence/v3-game-scale-basicattack.png) eight-direction sheets at 160px game scale.

## PARTIAL

- **Motion quality:** Idle reads human but has subtle breathing/weight shift; Walk reads as a human gait; BasicAttack reads as a stylized fantasy sword sweep. All three remain `CANDIDATE` until the owner accepts their look.
- **Paint:** deterministic palette treatment and a complete artist handoff exist. They are review aids; final illustrated paint-over has not been produced.
- **Modular output:** six runtime slots exist. Current geometry combines BodyOutfit and HeadHair; Outfit and Headgear have no independent source mesh. Cape and sword are separate. Empty slots do not yet prove hidden-surface or equipment-swap quality.
- **Action coverage:** Run, Hit, Death, Dash, Guard, and SkillAction are static placeholders. This first slice covers only the required Idle, Walk, and BasicAttack.
- **Production readiness:** the runtime package remains `DEV_ONLY`, tagged as placeholder/not-final-art, and not admitted.

## BLOCKED

The current Mesh2Motion build is not blocked on source access. Production admission is blocked on external art/review inputs:

1. Owner decision on the three candidate motions and the procedural appearance.
2. A final painted, layer-separated Swordsman set with independent BaseBody, Hair, Outfit, Weapon, Headgear, and BackAccessory output. The current source geometry cannot supply separate Outfit and Headgear surfaces; those need to be authored or supplied.

The selected motions and their evidence stay `CANDIDATE` while those inputs are pending. No V2 motion fallback is allowed.

The alternative MoCap Online and Mixamo records remain access-blocked if the owner wants to use those instead. The exact required input would be the free animation archive plus its license evidence in the motion inbox. No credentials should be sent or stored.

## OWNER REVIEW REQUIRED

Review the three 160px sheets linked above, especially [BasicAttack](evidence/v3-game-scale-basicattack.png), and the V3 preview route:

`?qa=1&world=court-legacy&renderer=canvas&swordsman=v3`

The strike is intentionally fantasy-styled and energetic rather than mocap-realistic. Choose whether the selected motion set and procedural look are acceptable for the next painted-art stage. Approval of a candidate does not approve the final painted art or production admission.

## NEXT EXACT ACTION

Owner: approve or reject the current Idle/Walk/BasicAttack set after reviewing the sheets and preview. If approved, provide or commission the layer-separated painted output and independent Outfit/Headgear surfaces; then run paint validation, hidden-surface/modular QA, and final runtime admission review. If rejected, identify which clip or pose should change; keep the other accepted clips and their provenance intact.

## Acceptance gates

| Gate | Status | Evidence / remaining work |
|---|---|---|
| A — Canonical rig | **PASS** | 60 bones; zero V2 actions remain. |
| B — New Idle/Walk/BasicAttack | **CANDIDATE** | Mesh2Motion selections; owner visual decision pending. |
| C — Provenance/license | **PASS for candidate use** | Pinned source, CC0 evidence, local hash, action and skeleton records. |
| D — Retarget and cleanup | **PASS** | Required mappings, finite transforms, stable root, no rotation spikes. |
| E — Fantasy readability | **INTERNAL VISUAL CANDIDATE** | Low sweep and recovery reviewed at game scale; owner approval pending. |
| F — Eight directions | **PASS** | 192 records, eight unmirrored views. |
| G — Structural passes | **PASS** | Six required passes align and pass structural QA. |
| H — Paint handoff | **PASS** | Deterministic manual handoff job exists; painted output is partial. |
| I — Six independent painted layers | **BLOCKED** | BodyOutfit and HeadHair are combined; source has no independent Outfit or Headgear mesh. |
| J — Runtime package | **PASS as DEV_ONLY candidate** | Schema/atlas validation passes; not production-admitted. |
| K — In-game proof | **PASS as development-only** | V3 route played selected actions with contact timing and no browser errors. |
| Owner approval | **PENDING** | Review current motion sheets and preview. |

## Validation checks

| Check | Result | Detail |
|---|---|---|
| Factory `--stage all --force` | **PASS** | Blender 5.2.2; rig rebuild, motion retarget/render, guide QA, paint handoff, and runtime validation passed. |
| Initial system Blender 4.3.2 attempt | **BLOCKED** | Rejected by the project's 5.2.0 minimum-version guard; full force rebuilds with Blender 5.2.0 and 5.2.2 passed. |
| Motion production gate | **BLOCKED by candidate status** | `passed=false` because all three selected motions remain `CANDIDATE`; this is the intended owner-approval gate, not a retarget/build failure. |
| Python suite | **PASS** | 17 tests passed. |
| Python compilation | **PASS** | Factory and Blender scripts compile. |
| Runtime package validator | **PASS** | Nine clip definitions; 82,301,760 decoded atlas bytes; no schema errors. |
| Development browser proof | **PASS** | BasicAttack playback/contact timing and return to Idle verified on the V3 route; no page or console errors. |
| Diff whitespace check | **PASS** | `git diff --check` is clean. |
| Failed checks | **None** | No check failed after using the required Blender version. |
| Skipped checks | **None** | Required technical checks were run. |

See [the implementation record](PRODUCTION_FACTORY_V3.md) and [the build evidence JSON](evidence/production-factory-v3-motion.json) for mappings, timings, exact render contract, and QA results.
