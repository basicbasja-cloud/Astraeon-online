# GitHub skill comparison — rig and sprite production

2026-10-11. The user explicitly asked to study skills on GitHub and build toward an “ultimate skill,” with rig, sprites and Ragnarok as hard reference. Six repositories and four supporting references were retrieved at immutable commits. [Retrieval audit](github-skill-audit.json) records hashes and review scope. They were read as external research, not installed, executed, or adopted as instructions. No paid service, Mixamo download or upstream engine was run for this comparison.

| Source | What was actually read | Useful knowledge | Gap for this game |
|---|---|---|---|
| [zhangrlll/codex-to-2d-sprites](https://github.com/zhangrlll/codex-to-2d-sprites/tree/e7252c23b002bbd131385d5432d9422d87134167) | Main skill, Blender/Mixamo adaptation and visual QA references | Test deformation beyond static weights; verify imported actions really drive meshes; preserve fixed camera/root; compare source pose to finished art; inspect transitions and actual delivered files. | Does not establish our complete replaceable-part catalog or right-hand invariants. Its image-refinement stage cannot make an unapproved model an approved art seed. |
| [MrFaraidun/img2game2d](https://github.com/MrFaraidun/img2game2d/tree/aad3b73026eba631c47a3e674c98d048362cc6f0) | Intake/rig/layer stages and layer-contract reference | Explicit layer identities, pivots, parent relationships and reconstruction bookkeeping. | Bounding-box pivots need source-space transforms; fixed scalar z-index cannot solve every crossed-limb pose. The existence of a reconstruction command does not prove complete hidden anatomy or eight-direction fit. Its tools were not run. |
| [scenario-labs sprite animation](https://github.com/scenario-labs/skills/tree/f6f8ab71aa1f1e8322624869a173c1024aa875b8/skills/scenario-sprite-animation) | Main routing/QA material and directional-cycle sections on hands, mirroring, registration and engine import | Verify delivered frame order, real alpha, actual grid, seam and camera behavior. Explicitly generate opposite views for asymmetric weapon hands. | Generated per-facing clips may have different periods; a modular character needs a shared pose map. Baseline normalization must preserve intended released-foot/body travel. A loop score alone cannot approve an attack. Provider rules and prices are not validated here. |
| [twoliness/sprite-pipeline](https://github.com/twoliness/sprite-pipeline/tree/c7b0f90bf144b60a09c2cd33db1804d0b3d73112) | Main skill | Preserve the source canvas for ordinary animation; separate generated, reviewed and promoted outputs; inspect final strips and individual frames. | Primarily video-to-flat-strip normalization. It does not supply a modular rig or hidden replacement geometry. Its default 256 px size is project-specific. |
| [Phaser official animation skill](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/animations/SKILL.md) | Animation manager/state, start/stop, events and per-frame-duration sections | Playback state belongs to the actual animated object; version-specific timing semantics matter. The documented per-frame `duration` adds to base frame time. | This snapshot is labeled Phaser 4; Astraeon's earlier permitted technical snapshot is a different renderer. It is no evidence of current game API compatibility. Do not pass absolute pose delays as additive holds. |
| [composio-community Blender rigging skill](https://github.com/composio-community/opencode-skills/blob/5076f6673e5bf8b1f46dc5e934d1e3dd37250e10/skills/blender-rigging-animation/SKILL.md) | Main skill | Simple hierarchy, named controls, early deformation checks, source preservation. | Introductory UI checklist; automatic weights and rendered video alone do not establish eight-direction modular sprite quality. No such Blender GUI workflow was executed. |

## Changes adopted into our reusable skill

1. Separate source-rig checks, sprite file checks, visible motion checks and real-game integration. Give each its own pass/fail/unverified result.
2. Preserve the shared canvas and action phase; do not normalize every silhouette to the same bounds or give hair and weapons independent clocks.
3. Make handedness a source relationship and visible wrist/grip review, not a prompt word or screen-left test. Opposite views are generated/rendered explicitly.
4. Require complete hidden content and an actual swap demonstration. A layer-extraction command or a flattened sheet is insufficient evidence.
5. Verify the reopened action and rendered image differences. A rig with animation metadata can still export a frozen character.
6. Treat raw renders as pose/visibility studies until final sprite art passes identity, silhouette, style, playback and transition review.
7. Use Ragnarok hard references for observed sprite behavior, while recording exact class/action/view/render provenance. Community tooling is evidence of its own output, not official client timings.

## Evidence ladder toward production

| Capability | Current evidence | Remaining requirement |
|---|---|---|
| Research synthesis | Pinned source/skill reads, official tool docs, paper methods and limitations | Keep sources versioned and test claims as the pipeline expands |
| Right-hand source ownership | Reopened `.blend`, actual weights and baked keys | Review wrist/grip readability for final drawings in every pose |
| Complete interchangeable parts | Original full geometry, eight-view strips, hair/torso/cape/weapon/helmet swaps | Approved final sprite style and broader item sizes |
| Opaque overlap correctness | Independent whole-scene owner/alpha reference passes | Resolve separately recorded color differences and choose the game's production renderer |
| Attack preview behavior | 21 earlier-export shared-clock/swapping/stop checks; current rerun blocked | Current-export browser checks, final acting/effect approval and actual game combat transitions |
| Mass production | Bounded 48-loadout/64-pose coverage exercise | More body families, locomotion/reaction actions, fit stress tests and measured in-game cost |

“Ultimate” remains the user's target, not a completion label. More repositories do not override a failed visible result. Each new rule should explain a concrete failure, include a reproducible exercise, and distinguish what was implemented from what was merely studied.
