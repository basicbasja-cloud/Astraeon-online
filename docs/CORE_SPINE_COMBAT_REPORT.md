# Staged Combat Resolution foundation — verified handoff

Date: 2026-10-07. This implements only the staged Combat Resolution foundation
and the two requested compatibility hardenings. Patch 0.0.1/Core Spine is not
complete. No final combat balance or visual acceptance is claimed.

## Git checkpoints

- Branch: `backbone/combat-resolution-0.0.1`
- Starting parent branch: `backbone/skill-tree-0.0.1`
- Starting parent HEAD: `09cf2f00e76f2095358699048b957b8e25126358`
- Runtime/test checkpoint: `6a06ef5d1d9bd6b9413910084f6900a25479e110`
- Final HEAD: the documentation successor containing this report, resolved by
  `git log -1 --format=%H -- docs/CORE_SPINE_COMBAT_REPORT.md`; the concrete hash
  is included in the final chat handoff. Only documentation differs from the
  runtime/test checkpoint.

The parent was fetched, fast-forward checked and clean before branch creation.
No reset to the expected checkpoint, unrelated branch merge, force push or PR.

## Files added

`combat-resolution-config.js`, `combat-resolution.js`, `combat-runtime.js`,
`tests/combat-resolution.test.cjs`, `tests/compatibility-hardening.test.cjs`,
`tests/combat_browser.py`, `tools/combat.html`, `tools/combat-harness.js`,
`docs/CORE_SPINE_COMBAT.md`, `docs/CORE_SPINE_COMBAT_REPORT.md`.

## Files modified

`character-state.js`, `player-state.js`, `save-state.js`, `game.js`, `boot.js`,
`index.html`, `sw.js`, `tests/cache_resume.py`, `tools/progression.html`,
`README.md`, `ARCHITECTURE.md`, `docs/CORE_SPINE_PROGRESSION.md`,
`docs/CORE_SPINE_SKILL_TREE.md`.

## Implemented architecture

The [combat contract](CORE_SPINE_COMBAT.md) documents all input fields, optional
defaults, numeric boundaries, formulas, ordering and integration limitations.
Input contains separate attacker/defender level and derived snapshots, authorized
action, mitigation/resistance state and context metadata. RNG/config are supplied
separately. Current class IDs are not part of the calculator.

Stages: validate → accuracy → perfectDodge → baseDamage → critical → defense /
penetration → resistance → parry/guard/block/shield → pending HP application →
status/on-hit output. Rich results and nested snapshots/trace/candidates are
immutable copies. Early miss/dodge paths terminate with zero damage. Invalid
input/config/RNG returns structured failure without HP/world mutation.

RNG: injected next(), with finite [0,1) validation on every consumed draw.
Sequence fixtures and a seeded test reproduce entire results. Production
Math.random appears only in the adapter provider. Configured critical accuracy
bypass preselects critical eligibility before accuracy, still checks Perfect
Dodge and applies damage only at the later critical stage. Trace exposes this
policy roll explicitly.

Accuracy consumes HIT/FLEE and a configurable level influence. Guaranteed and
ignoreFlee are action policies. Perfect Dodge consumes the derived percentage
after successful accuracy and is an independent outcome. Critical consumes
CRIT with configurable interpretation/multiplier/defense ignore. Physical damage
selects physicalATK/DEF; magical selects magicATK/MDEF. New categories can supply
other stat keys and defense rules in config.

Penetration order: percent reduction, flat subtraction, zero clamp, critical
defense ignore. Flat and ratio defense rules are configurable. Resistance is a
minimal extensible category map with configured caps; missing category is neutral.
Mitigation independently reports guard/block/parry flags, absorbed and mitigated
amounts. Positive defense floor precedes consumable mitigation; full parry or
shield may leave zero HP damage. Decimal stabilization precedes selected rounding.

HP: applyCombatResult computes a new clamped HP value, applied damage, death and
overkill without actor mutation. game.js assigns it before existing death/reward/
presentation effects. Rejected results cannot heal or damage an actor. Developer
inspection records both the pure application and actual live HP after assignment.
Status/on-hit/proc outputs are candidates only. Existing contact consumers run
after positive resolved damage; no full status system was invented.

Skill Runtime integration: learned/rank-authorized action and single compatible
Node reach buildInput without repeated rank/prerequisite/loadout validation.
Passives feed derived snapshots. Both existing physical and magical player
contacts/projectiles/field pulses route through the resolver. Existing authored
skills, Timeline, input, windups, movement, skill effects, animation, hit stop and
camera code retain their behavior. ASPD/cast helpers are available but unused by
playable timing. The inspection harness uses the same modules; only exact dev=1
enables live mutation fixtures, absent from ordinary URLs.

## Compatibility hardening

Future saves: normalize/snapshot reject saveVersion > 4. Normal loading returns
through an unsupported-save message before creation, mount, autosave and save
event listeners. Browser verification proves storage bytes unchanged after
pagehide/visibility events and reload, with no creation overwrite path.

Stat refunds: additive statPointSpending stores actual paid Stat expenditure,
separate from Skill Point spending. Allocation and reset are atomic; reset
zeros expenditure and cannot refund again. Save/reload preserves it. Tests cover
higher/lower tuned costs and allocations under mixed cost versions. Missing
v4/earlier ledgers migrate using historical initial=1/cost=1, never current tuned
cost. Invalid explicit ledgers and unallocated states receive no credit. Save
version remains 4, with no production respec UI or economy. Local saves are not
authenticated against manual editing.

## Provisional coefficients and non-final decisions

Accuracy base 1, HIT/FLEE scale .005, level influence 0, clamp [.05,1]; Perfect
Dodge/CRIT percentage scale .01 and maximum chance 1; critical multiplier 1.5,
defense ignore .3, bypass off; flat DEF/MDEF scale 1, optional ratio rule;
resistance clamp [-.6,.8]; guard/block .7 and parry 1; minimum 1, floor rounding,
six-decimal stabilization; timing reference ASPD 100, interval floor .01 and
cast floor 0. Compatibility enemies use the neutral stat fixture from config.
Default action penetration is zero.

These are executable fixture defaults, not final HIT/FLEE curves, DEF/MDEF curves,
crit/penetration/resistance/guard balance, ASPD/cast formulas, class/skill tuning,
PvP/GvG/boss modifiers or level penalties. All new numerical combat tuning lives
in combat-resolution-config.js; the owner can change values without rewriting
the algorithms. No new production skills, classes, monsters or Advanced Jobs.

## Automated verification

| Node suite | Pass | Fail |
|---|---:|---:|
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
| **Total individual Node checks** | **277** | **0** |

99 new deterministic checks, retaining all 178 previous checks. Coverage includes
malformed/overflow data, all stages, RNG invalid/exhausted/throwing/seeded streams,
config changes, immutability, HP clamps, future categories, timing helpers,
authorized rank/Node/passive bridges, future saves and actual refund accounting.

| Browser / schema command | Verified result |
|---|---|
| tests/combat_browser.py | 21 acceptance groups, zero page/console/HTTP errors |
| tests/skill_tree_browser.py | 11 acceptance groups, existing returning-save/harness behavior retained |
| tests/progression_browser.py | 7 acceptance groups, existing EXP/stats/legacy/world save behavior retained |
| tests/cache_resume.py | v86 migration, 120 precached requests, saved character/skills/Nodes/Stat ledger retained offline |
| tools/validate-world-v3.py | Terrain, Navigation, TownObject and AnimationManifest schemas pass |

Node command: tools/run-node-checks.py. Browser tests used disposable headless
Chrome contexts, Playwright and the documented localhost static server on 8011.
Bundled Python was used because the shell's python command is a Store alias;
test dependencies/reports were kept outside the checkout. Evidence root:
`D:\Astraeon\backbone-verification\combat`, with node/, combat-browser/,
skill-browser/, progression-browser/ and cache/ reports.

Local smoke covers actual creation and ordinary combat for Swordsman and Mage,
learning/ranked active execution, passives, compatible Nodes, physical/magical
resolver input, deterministic miss/Perfect Dodge/crit/defense, real enemy HP
assignment, kill rewards/Base/Job EXP/quest credit, incoming damage/player death/
town respawn, save reload parity for inventory/gear/quests/world/progression/
skills/Stat ledger, legacy returning saves and ordinary URL developer isolation.
Browser smoke retries corrected assumptions in the new automation (held skills
and surviving nearby enemies after kills). The final run uses ordinary skill
input retries and a disposable saved fixture beside an existing field spawn.
The new harness now supplies the existing favicon, eliminating its initial 404.
No error was suppressed and no production monster was added for tests.

## Limitations, merge risk and next work

Incoming enemy orchestration keeps existing timed guard/plate behavior; it does
not yet consume the new defender stat pipeline. Existing burn/ignite/chain/delayed
Node proc calculations keep their compatibility paths, though numeric HP
application is safe. Enemy DEF/FLEE/resistance sheets remain neutral fixtures.
Candidate dispatch, shield consumption, full status effects and server authority
remain future work. Timing helpers do not change animation timings. Four current
skill buttons still execute only the first four of eight persisted slots.

Potential conflicts: game.js, character/player/save state, boot/page/SW versions,
tests/cache_resume.py, shared developer harness and system documentation. Parallel
visual branches may touch the same orchestration/cache files even though this
branch changes no visual content.

Intentionally untouched: authoring/**, RO3 Ref/**, assets/**, world/**, Blender,
renderers, geometry, lighting, character sprites/atlases, motion, animation, VFX,
camera, style.css, visual-review evidence, combat.js, skill-nodes.js,
skill-definitions.js, progression-config.js, progression.js and stats.js. The
historical visual CURRENT_HANDOFF/REQUESTS_AND_STATUS/MASTER_PLAN files remain
unchanged. No final combat UI, balance, advancement or network/server authority.

Recommended next Backbone task: complete eight-slot Action Loadout behavior and
its persistence/cooldown contracts, using this resolver and existing Skill Runtime;
then plan contained incoming combat/status adapters with owner-approved balance.
Production UI and numerical tuning remain owner decisions.

Final working tree must be clean. Actual `git status --short` and
`git log --oneline -10` are included in the final chat handoff after the
documentation commit and push to the requested branch.
