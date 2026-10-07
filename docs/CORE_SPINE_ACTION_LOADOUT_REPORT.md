# Eight-slot Action Loadout foundation — verified handoff

Date: 2026-10-07. Only the complete eight-slot behavior, persistence and cooldown
foundation is implemented. Patch 0.0.1/Core Spine is **not complete**. No final
production HUD/mobile layout, skill balance or visual acceptance is claimed.

## Git checkpoints

- Branch: `backbone/action-loadout-0.0.1`
- Starting parent branch: `backbone/combat-resolution-0.0.1`
- Starting parent HEAD: `9dea35ca816e831c1bd523d30295b5cc83f07fd4`
- Runtime/test checkpoint: `c43b8b0a80dd51cd4b904ea9388bc19690fb3a42`
- Final HEAD: the documentation successor containing this report, resolved with
  `git log -1 --format=%H -- docs/CORE_SPINE_ACTION_LOADOUT_REPORT.md`. Its concrete
  hash is included in the final chat handoff; only documentation differs from
  the runtime/test checkpoint.

The remote parent was fetched, switched to, fast-forward checked and clean
before branch creation. Remote HEAD was authoritative. No unrelated branch
merge, force push, history rewrite or PR. Push targets only this new branch.

## Files added

`action-loadout.js`, `action-runtime.js`, `tests/action-loadout.test.cjs`,
`tests/action-runtime.test.cjs`, `tests/action_loadout_browser.py`,
`docs/CORE_SPINE_ACTION_LOADOUT.md`, `docs/CORE_SPINE_ACTION_LOADOUT_REPORT.md`.

## Files modified

`player-state.js`, `skill-runtime.js`, `input.js`, `combat.js`, `game.js`,
`boot.js`, `index.html`, `sw.js`, `tools/progression.html`,
`tools/progression-harness.js`, `tools/combat.html`, `tests/cache_resume.py`,
`tests/combat_browser.py`, `tests/combat-resolution.test.cjs`,
`tests/compatibility-hardening.test.cjs`, `tests/motion.test.cjs`,
`tests/save-progression.test.cjs`, `tests/skill-tree.test.cjs`,
`tests/stats.test.cjs`, `README.md`, `ARCHITECTURE.md`,
`docs/CORE_SPINE_PROGRESSION.md`, `docs/CORE_SPINE_SKILL_TREE.md`,
`docs/CORE_SPINE_COMBAT.md`.

## Implemented contracts

The [full system contract](CORE_SPINE_ACTION_LOADOUT.md) specifies API parameters,
structured errors, examples, identity/clock policy, trusted launch boundary,
legacy exceptions and compatibility limits.

| Requested area | Implemented behavior |
|---|---|
| Architecture | Separate learned state, configuration, runtime eligibility/clocks, Character resources, Skill Runtime, Timeline, Combat Resolution, input and presentation |
| Persistent model | Dense immutable eight-element array of known assignable active IDs or null; no extra preset/schema |
| Assignment | Valid slot/state/known/active/assignable/learned/current class; get/canAssign/assign/clear/swap/move; no partial mutation |
| Duplicate policy | At most one persisted assignment per ID; invalid save duplicates repaired first valid occurrence wins |
| Class dormancy | Option A: retain intent/ranks/payment; incompatible slots cannot compile/execute; no refund or progression deletion |
| Runtime state | Immutable compiled inspection, source/class/rank/Node, eligibility/reason, cost/affordability, readiness/remaining |
| Cooldowns | Explicit simulation time, per action ID, authored duration incl anticipation; move/clear cannot bypass; optional group/global hooks default off |
| Combat edits | Backbone §8 full-slot lock including empty slots; provisional max authored duration across old/new IDs; no-op and safe edits add no lock |
| Resource eligibility | Existing finite HP/SP and authored costs, class/learning, current action/menu/transition restrictions; unchanged class resource adapters |
| Commit boundary | Owned immutable preparation; revalidate immediately before synchronous Timeline acceptance; only then spend/start once; repeated/forged/stale/reentrant/rejected use cannot charge |
| Skill Runtime | Existing compiler owns learned rank and compatible single Node; no tree/rank/Node formula rewrite |
| Combat Resolution | Existing Timeline contacts/projectiles/pulses feed authorized rank/Node payload to Combat Runtime → resolver → existing HP application |
| Basic Attack | Separate action, no skill slot or learning requirement; original combo/Timeline cooldown/contact resource behavior |
| Potion | Separate inventory/heal utility, no skill slot; separate input identity as extension boundary, no item instances/framework |
| Death/respawn | Retain configuration/ranks/ledgers and cooldowns; invalidate preparations; accepted cast cancellation does not refund; old respawn resource rules preserved |
| Map transitions | Town/field/dungeon/class changes retain ID clocks on simulation time and invalidate preparations; paused menus/loading freeze clock |
| Save normalization | Same saveVersion 4/key; dense eight slots, invalid/passive IDs empty, dormant/unlearned known IDs safely nonexecutable; historical loadout retained; idempotent |
| Reload | Restores configuration; creates fresh transient clocks/tickets; no offline cooldown persistence |
| Returning saves | legacySkillControls fallback in empty first four only, same runtime commit and action-ID clock; no free ranks/points/paid ledger; supported explicit/dormant assignment takes priority |
| Developer tooling | Isolated harness clear/swap/move/invalid/execute/cost/runtime/time/reset/save/reload; opt-in live APIs execute every slot through same game function |
| Input/UI | actionSlot1–8 vocabulary, old skill1–4 aliases and pointer controls; no new production keys/buttons/art/style |

## Automated verification

Windows local Node v24.14.0 and Python 3.12, Playwright Chromium using installed
Chrome with D3D11, static server at `http://127.0.0.1:8011`. Reports are outside
the repository under `D:/Astraeon/backbone-verification/loadout/`. Commands are
documented in README; runtime/browser fixtures use disposable contexts only.

| Node suite | Pass | Fail |
|---|---:|---:|
| action-loadout (new) | 37 | 0 |
| action-runtime (new) | 56 | 0 |
| combat-resolution | 86 | 0 |
| compatibility-hardening | 13 | 0 |
| expanded_town | 7 | 0 |
| golden_pipeline | 3 | 0 |
| locomotion-transitions | 19 | 0 |
| motion | 44 | 0 |
| painted_locomotion | 3 | 0 |
| progression | 10 | 0 |
| save-progression | 13 | 0 |
| skill-tree | 45 | 0 |
| stats | 14 | 0 |
| world_v3 | 20 | 0 |
| **Total** | **370** | **0** |

**93 new checks + all 277 previous checks retained.** Existing Node assertions
are unchanged; six suites add module dependencies only. New checks cover all
eight launches, invalid assignment/state/clock, duplicates/moves/swaps, dormant
ranks/payments, immutable snapshots/config, canonical/idempotent save, safe and
combat edits, stale/foreign/used packages, resource/Timeline rejection, launch
throw/reentry, cooldown overflow, exact readiness, cast extension, groups/global,
rank/Node downstream, transition invalidation and legacy without free learning.

| Browser/schema gate | Result |
|---|---|
| action_loadout_browser.py | 17 acceptance groups passed |
| combat_browser.py | 21 acceptance groups passed |
| skill_tree_browser.py | 11 acceptance groups passed |
| progression_browser.py | 7 acceptance groups passed |
| cache_resume.py | Migration, both new modules in v87 precache and offline saved-character reload passed |
| tools/validate-world-v3.py | Terrain, Navigation, TownObject and AnimationManifest schemas passed |
| git diff --check | Passed |

No new console/runtime/HTTP errors in the browser acceptance reports. Future-save
ordinary boot preserves unsupported storage bytes; existing Stat paid refund
tests and browser reset remain green. Cache acceptance covers prior cache cleanup
and retained learned/rank/Node/assignment data after offline boot.

## Disposable local gameplay smoke

Repeated for **Swordsman and Mage** using a new character through the normal UI:

1. Gain Job EXP/Skill Points, learn all four actives, rank the first to 3, learn
   passive and verify its derived-stat increase, select compatible Qi/Fire Node.
2. Assign slots 1–4; reject duplicate/passive/out-of-range edits without mutation.
3. Execute first-four controls via existing keyboard and pointer buttons. Move
   each active into slots 5–8 and execute through the same live shared path.
4. Assert accepted resourceBefore − resourceAfter equals authored cost once;
   repeated active request spends nothing and changes no clock. After Timeline
   ends, another request is rejected by cooldown without SP/clock mutation.
5. Reject zero-SP use without cooldown; synchronously click native skill button
   and verify exact cost before frame regeneration. Basic Attack/Potion retain
   eight-slot configuration; Potion decrements inventory/heals once.
6. Switch class through ordinary training; dormant blockedReason, learned ranks,
   exact payment ledger, balance and configuration survive; switch back.
7. Travel town → field; configuration edit adds all-eight lock. Execute slot 8
   against an existing field actor; rank 3/Node reach resolver and actual HP
   matches pure application. Field → town and dungeon entry/exit retain intent.
8. Reload a low-HP fixture beside an existing field actor, observe actual enemy
   death, reject dead skill use, then retain unique assignments/ranks/payment on
   town respawn. No monster/runtime production fixtures added.
9. Launch, save and reload; assignments/ranks/Nodes/payment/resources/world/gear
   persist, runtime clocks start empty, and no skill5 HUD button is introduced.

Existing combat smoke independently verifies hit/miss/dodge/critical/defense,
ordinary kill rewards, Base/Job EXP, gold/quest credit and real enemy death.
Existing progression/skill smoke retains inventory/equipment/quests/world claims,
Stat ledger/refund and legacy actions. Returning legacy Mage executes through
the shared commit with empty learned/loadout maps and unchanged historical data.
The isolated harness's actual controls exercise move/swap/clear, duplicate reject,
execute, forbidden/cooldown reject, explicit set/advance time, reset and reload.
Normal URL boot exposes neither developer mutation API.

The death fixture initially raced pagehide autosave. Both browser tests now
stage it in sessionStorage and install it on the new document after autosave,
following the existing cache test pattern. All earlier assertions remain; the
combat suite additionally checks assignment/rank/payment retention after death.
This correction is in test setup, not gameplay/death behavior.

## Known limitations, conflicts and remaining work

- All cooldown numbers and full-slot change duration policy remain provisional.
  No production global/group cooldown is active. Pure callers supply correct
  monotonic time and combat context; live adapter derives them from the game.
- Current Swordsman/Mage trees have four actives each. Eight configured slots
  support current and future content; incompatible class IDs are dormant.
- Configuration and learning remain developer-only until owner-approved UI.
  Active casts reject live configuration edits; idle unsafe fields use combat lock.
- Reload resets transient cooldowns; local save/debug APIs are not server
  authority. Trusted launch callbacks only start Timeline; arbitrary callback
  side effects cannot be rolled back by the core.
- Existing guard/heal rank effects, incoming enemy/status orchestration,
  regeneration, Node contact restoration, class-training/respawn refills,
  and Basic Attack/Potion behavior retain compatibility semantics.
- No production presets, ItemDefinition/instances, scroll/weapon/item slots,
  final input/HUD, advanced classes, balance, online/PvP/status redesign.

Potential merge conflicts: game.js action/dev adapter and existing cooldown
presentation reads; player-state.js; skill-runtime.js normalization; input.js;
boot.js/index.html/sw.js version/import/precache list; developer harness imports
and README/architecture contracts. Coordinate future HUD work through the shared
API and keep resource/cooldown ownership in Action Runtime. No PR was opened.

Intentionally untouched: `authoring/**`, `RO3 Ref/**`, `assets/**`, `world/**`,
Blender sources, renderer/lighting/geometry, sprites/atlases/animation art,
motion/VFX/camera modules, `style.css`, visual-review evidence, combat formulas,
skill definitions/tree/Nodes, progression/stat formulas, Character and Save
implementations. Historical handoff/status/master-plan and prior foundation
reports retain their visual review state. Camera transition helper only gains
preparation invalidation; camera behavior is unchanged.

Recommended next Backbone task: **Patch 0.0.1 Item/Inventory foundation**, with
ItemDefinition/instance identity and persistent inventory/equipment contracts,
then authored consumable/group-cooldown/scroll/weapon action adapters. Preserve
this loadout/runtime boundary and let the owner direct production presentation.

Final status/log commands are included in the chat handoff:

```powershell
git status --short
git log --oneline -10
```

Expected final working tree is clean. The final documentation commit follows
the runtime/test checkpoint; Patch 0.0.1 remains open for the next foundations.
