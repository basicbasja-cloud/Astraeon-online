# Base skill tree completion report — 7 October 2026

Branch: `backbone/skill-tree-0.0.1`.
Starting parent HEAD: `bc967fb00bb4b7bbc5652c5c65d48857ae016b1c`.
Runtime/test checkpoint: `0179fabf87f6795a0bbb0ca944fbb4453c1c5ab9`.
Final HEAD is the subsequent documentation commit, recorded with final status
and the last eight commits in the completion message. A committed report cannot
embed its own final commit hash.

The branch was created after fetching, switching to `backbone-design`, pulling
with `--ff-only`, and confirming a clean working tree. This task implements the
**Base-class Skill Tree minimum only**. Patch 0.0.1 is not complete.

## Files added

- `skill-definitions.js`
- `skill-tree.js`
- `skill-runtime.js`
- `tests/skill-tree.test.cjs`
- `tests/skill_tree_browser.py`
- `docs/CORE_SPINE_SKILL_TREE.md`
- `docs/CORE_SPINE_SKILL_TREE_REPORT.md`

## Files modified

- `character-state.js`: private learned ranks and paid ledger, atomic learning,
  debug refund and automatic passive integration.
- `player-state.js`: readonly persistent adapters, current-class selection,
  eight active slots and compatible Node/runtime bridges.
- `save-state.js`: additive version 4 normalization and learned passive capacities.
- `game.js`: existing four buttons consume assigned slots; explicit returning-save
  compatibility and opt-in developer operations.
- `boot.js`, `index.html`, `sw.js`: ordered skill module loading and cache 85.
- `tools/progression.html`, `tools/progression-harness.js`: plain developer controls.
- `tests/motion.test.cjs`, `tests/save-progression.test.cjs`, `tests/stats.test.cjs`:
  load new shared dependencies; original assertions remain intact.
- `tests/cache_resume.py`: existing offline/world migration regression also checks
  real learned/passive/paid/loadout/Node state and precaches the three new modules.
- `README.md`, `ARCHITECTURE.md`, `docs/CORE_SPINE_PROGRESSION.md`: extension links,
  current cache version, run commands and compatibility boundaries.

## Architecture and behavior

Frozen SkillDefinitions represent IDs, string class IDs, names/keys, active/passive
type, five ranks, per-rank Job gates/costs, ranked prerequisites, loadout eligibility,
runtime/Node references, tags and future metadata. Frozen trees contain skill IDs
and prerequisite edges. Each of Swordsman and Mage references its four existing
authored actives and adds two small passives. The algorithms are independent of
legacy numeric class indices; the adapter maps Warrior 0 to Swordsman and Mage 12.
No visual class rename or Advanced Class implementation is introduced.

Pure tree transitions validate state, identity, class, rank cap, Job gate,
prerequisite ranks and available points before generating a new state. The
character computes derived output before committing. Rejection does not spend
points or change ranks. Immutable snapshots prevent ordinary gameplay code from
overwriting the authoritative fields.

Persistent `learnedSkills` stores ID/rank pairs. `skillPointSpending` stores costs
actually paid, separate from the existing unspent Skill Point balance. Learning
updates rank, deducts that same pool and records payment atomically. Debug reset
refunds the paid ledger and clears ranks/slots. Repeated reset refunds zero.
Imported valid ranks without payment evidence have zero refundable cost; newly
paid rank-ups refund only their actual new expenditure. Total tree cost 59 exceeds
the natural Base Job cap award of 49. All balance values are provisional data.

Learned passives automatically contribute deterministic modifiers through the
existing stat calculator. Swordsman receives configured ATK and percentage HP;
Mage receives MATK, SP and cast modifier data. No passive occupies a slot. Gear,
companion, runtime effects and learned passives coexist without load-time resource
inflation. Switching the existing training class makes other-class skills/passives
dormant while retaining ranks and payment evidence.

An active can be learned, eligible to use, and explicitly assigned independently.
The eight-slot persistent model validates slot bounds, current-class active learning
and duplicate assignment. Learning does not auto equip. Basic Attack and Potion
remain separate. The existing first four skill buttons now execute slots 1–4.
The pure runtime bridge references the existing action definitions, incorporates
rank damage tuning and preserves one compatible authored Node. The Node module,
combat Timeline, art, effects and payload definitions remain unchanged.

Save version remains 4 because optional additive fields have valid defaults.
Absent learning migrates to empty maps, without retrospective rewards. The existing
schema preserves progression, primary stats, resource offsets, inventory, gear,
quests, claims, discoveries, position, currency, selected Nodes and historical
fields. Historical `loadout` data remains separate and retained. Invalid ranks,
IDs, dependency chains and paid ledger entries are safely normalized without new
points. Migration is deterministic and idempotent across repeated save cycles.

Returning saves predating the new slots get explicit `legacySkillControls=true`:
their authored fixed buttons and Nodes continue working at original runtime rank
without free learned ranks or assignments. New Swordsman/Mage characters opt out
and start empty. Debug reset removes this shortcut. Other prototype classes keep
their original gameplay but receive no new tree.

## Developer tooling

`/tools/progression.html` reuses its isolated developer save key and displays tree
definitions, ranks, prerequisites, gate results, passive modifiers, eight slots,
compiled runtime and persistent data. It supports point additions, Job level,
learn, rank-up, debug reset/refund, assignment/clearing, compatible Node selection,
save and reload through shared APIs.

`/?qa=1&dev=1` exposes the same operations on a disposable playable character.
Live slot/Node changes and debug reset require town or a safe camp with no active
Timeline action. The ordinary URL exposes no developer mutation API. No final
Skill Tree UI, HUD layout, icons or styling was designed.

## Verification results

| Check | Result |
| --- | --- |
| New deterministic skill checks | 45 passed |
| Existing progression checks | 10 passed |
| Existing stat/modifier checks | 14 passed |
| Existing save/progression checks | 13 passed |
| Existing motion/combat/save/navigation checks | 44 passed |
| Existing expanded town checks | 7 passed |
| Existing Golden pipeline checks | 3 passed |
| Existing locomotion transitions | 19 passed |
| Existing painted locomotion | 3 passed |
| Existing world v3 checks | 20 passed |
| Total Node suite | **178 passed, 0 failed** |
| New skill_tree_browser.py | **11 acceptance groups passed**, zero runtime/HTTP errors |
| Existing progression_browser.py | **7 acceptance groups passed**, zero runtime/HTTP errors |
| Existing cache_resume.py | Passed: cache 85, 117 precached requests, offline learned/paid/slot/Node persistence and both existing town-position migrations |
| Public world v3 schemas | Passed: Terrain, Navigation, TownObject and AnimationManifest, using tools/validate-world-v3.py |

The deterministic tests cover learn/rank/max gates, both classes, scarce balance,
invalid IDs/prototype names, invalid values/state, atomic rejections, exact spend,
refund/repeated reset, imported unpaid ranks, refund overflow, always-active
passives, exact derived-pipeline parity, class dormancy, all eight slots, no auto
assignment, Node compatibility, preserved original action data, twenty save/load
cycles, version 3/4 migration/idempotency, historical data retention, readonly
state, resource-effect persistence boundaries and failed derived calculation.

Local smoke ran disposable Chrome contexts against the documented static server
at `127.0.0.1:8011`. Both classes booted, gained Base/Job levels and Skill Points,
learned valid actives, rejected Job/prerequisite gates, reached rank 3, activated
passives without assignment, explicitly assigned an active, retained its compatible
Node and executed it with ordinary keyboard input through the existing Timeline.
Configuration during an active action rejected. Save/reload retained ranks, paid
costs, balance, derived output, slots, Nodes, inventory, gear, quest and world state.
Reset/reload refunded paid points once. Returning Mage saves retained original
Node execution without free learning. The harness and normal-URL isolation passed.
The existing progression browser test separately covered ordinary movement,
town/field travel, combat, loot, both EXP tracks and quest credit.

Evidence is outside the checkout under `D:\Astraeon\backbone-verification\skills`
in `node`, `browser`, `progression-browser` and `cache`, including JSON reports
and disposable screenshots. This Windows host's `python` shortcut is not a runtime;
checks use bundled Codex Python, Node 24, Chrome and external verification libraries.
The additional schema check initially lacked `jsonschema`; it was installed only
in the external verification directory and the unchanged validator then passed.
No build/package dependency was added to the runtime repository. No test acceptance
threshold was weakened. These results make no visual/device-performance claim.

## Known limitations and next task

- The old game had four fixed buttons, not a complete eight-slot Action Loadout.
  The new model/API supports all eight; gameplay controls currently bridge four.
  Production learning/assignment UI and controls for slots 5–8 await owner design.
- New character skill learning is currently available through developer tooling.
  Returning saves intentionally keep their documented prototype compatibility.
- In-combat loadout changes are rejected. Full-slot cooldown changes, action item/
  weapon/scroll variants and presets belong to subsequent Action Loadout work.
- Coefficients are provisional. Guard/heal rank effect tuning and actual combat use
  of derived cast/defense stats remain future work; the staged combat pipeline is
  still incomplete. No class advancement, respec economy or online authority exists.
- Invalid external save data is repaired without refunds. This local simulation
  cannot authenticate a manually edited paid ledger; server authority is future work.

Potential merge conflicts are in `game.js`, `player-state.js`, `character-state.js`,
`save-state.js`, boot/page/SW versions, shared harness, dependency lists and system
docs. Parallel visual work may edit the same orchestration/cache lines. No branches
were merged, reset or rewritten; no PR was requested or created.

Intentionally untouched: `authoring/**`, `RO3 Ref/**`, `assets/**`, `world/**`, all
renderer/Blender/geometry/lighting data, character animation/sprite atlases, VFX,
`combat.js`, `skill-nodes.js`, `style.css`, visual-review evidence, and historical
visual handoff/status/master-plan documents. The EXP/stat coefficients and their
stable progression rules also remain unchanged.

Recommended next Backbone task: implement the staged 0.0.1 combat-resolution
interfaces and consume the existing derived stats, with deterministic tests.
Follow with complete eight-slot Action Loadout behavior/persistence; leave all
production UI/visual decisions with the owner. This report does not declare
Patch 0.0.1 complete.
