# Patch 0.0.1 Base skill tree minimum

This extends the stable [progression/stat/save foundation](CORE_SPINE_PROGRESSION.md).
The authority is `ASTRAEON_Backbone_Release_Roadmap_EN_v0.4.md`. This is only the
Base skill tree portion of Core Spine. Patch 0.0.1 is still incomplete.

## Responsibility boundaries

| Layer | Implementation |
| --- | --- |
| Immutable SkillDefinition | `skill-definitions.js`: ID, class, name/key, active/passive, maxRank, per-rank Job requirements and costs, prerequisite ranks, loadout eligibility, runtime and compatible Node references, tags and future metadata |
| Immutable Base Skill Tree | `skill-definitions.js`: class/tree IDs, skill IDs and prerequisite edges; Swordsman and Mage only |
| Pure learning transitions | `skill-tree.js`: validation, next-rank transitions, paid-cost refund and persistent normalization |
| Private persistent character state | `character-state.js`: owns learned ranks, paid ledger and the **existing** Skill Point balance; derives before committing a transition |
| Runtime | `skill-runtime.js`: eight action slots, active usability, learned rank + authored combat action + optional existing Node |
| Gameplay adapter | `player-state.js`: readonly persistent getters, class mapping, slot assignment, Node selection and passive recalculation |
| Presentation | Existing four skill buttons use the adapter; the plain developer harness calls the same APIs |
| Node augmentation | Unmodified `skill-nodes.js`; one compatible string per authored runtime skill ID |

The tree algorithms accept string class IDs. Only the legacy adapter maps `cls=0`
(existing Warrior) to `swordsman`, and `cls=12` to `mage`. The visible class name,
character assets and animations are unchanged. Other legacy class IDs retain
their old gameplay; they have no new tree. No Advanced Job is implemented.

## Provisional content

Each supported Base class references its four existing authored active skills and
adds two small passive definitions. All have five ranks. The first active costs
`[1,2,2,2,2]`; other skills cost two points per rank. Total tree cost is 59 versus
49 naturally awarded points at Base Job cap 50, so a character cannot max its
whole tree. Debug point additions are explicitly outside normal progression.

The first active requires Job levels `[1,3,5,7,9]`. The next three use the same
curve offset by two, four and six levels. The fourth active requires first-active
rank 3. The second passive requires first-passive rank 2 and Job levels
`[3,5,7,9,11]`. These numbers are recommended defaults, frozen data for this build,
and await gameplay balance approval. There are no invented class advancement rules.

Swordsman passives contribute `+2 physicalATK/rank` and `+2% maxHP/rank`. Mage
passives contribute `+2 magicATK, +3 maxSP/rank` and `-0.02 castTimeModifier/rank`.
The existing derived calculator orders and clamps them with gear, companion,
runtime passives and temporary effects. Learned passives need no action slot.
They apply for the current class; another class's retained ranks are dormant.
The full combat use of cast/defense stats remains the next combat integration.

## Authoritative APIs

`AstraeonCharacter.create` and `AstraeonPlayer.attach` expose:

- `getSkillRank(id)`, `getLearnedSkills()`, `getPassiveSkillModifiers()`.
- `getAvailableSkills()` lists current-class definitions, ranks and authoritative
  next-rank gate results, including currently gated skills for inspection.
- `canLearnSkill(id)` previews the next rank without changing state.
- `learnSkill(id)` requires rank zero; `rankUpSkill(id)` requires an existing rank.
- `canRefundSkill(id)` inspects that skill's recorded paid amount.
- `resetSkills()` is the debug whole-tree reset; no individual refund or respec
  item/currency economy is introduced. All retained class ranks reset together.

Rejected operations return `{ok:false,code,...detail}`. Codes include
`INVALID_STATE`, `UNKNOWN_SKILL`, `WRONG_CLASS`, `ALREADY_LEARNED`, `NOT_LEARNED`,
`MAX_RANK`, `JOB_LEVEL`, `PREREQUISITE`, `SKILL_POINTS` and `INVALID_DEFINITION`.
Learn validates the full rank/ledger state, current class, next rank's Job gate,
prerequisite ranks and configured nonnegative integer cost before deducting.
The new derived snapshot is calculated before publishing points or ranks.
Calculator errors throw while retaining the previous character state.

The player adapter additionally exposes `getSkillTree()`, `getClassId()`,
`canUseSkill(id)`, `isSkillAssigned(id)`, `getActionLoadout()`,
`assignSkill(zeroBasedSlot,idOrNull)`, `compileAction(zeroBasedSlot,combo=1)` and
`setSkillNode(id,nodeOrNull)`. Assignment validates integer slot 0–7, learned
current-class active status and duplicate slots. Basic Attack and Potion stay
separate from these eight slots.

Learning never auto assigns. A learned active is eligible/usable by its current
class, but an actual button action requires explicit slot assignment, enough SP,
no current action and its existing cooldown. Slots retain IDs when changing the
legacy training class; incompatible assignments become dormant. Reset clears
all slots. Runtime cooldowns, targeting and animation state are never saved as
learned progression.

`compileAction` references `combat.js` payloads, adds `learnedRank` and applies the
configured `+10% damage/rank above rank 1`, then retains the existing compatible
Node result. Guard/heal actions retain their existing effect payloads; tuning
their rank effects is future content work. No arbitrary node graph exists.

## Persistence and migration

Save version stays **4**: this is an additive extension with defaults, not a
replacement schema. The browser save key remains `astraeon-iso-v1`.

```js
learnedSkills: { 'rising-edge': 3 },        // ID -> rank, no copied definitions
skillPointSpending: { 'rising-edge': 5 },   // ID -> points actually paid
actionLoadout: ['rising-edge', null, null, null, null, null, null, null],
legacySkillControls: false
```

The paid ledger is not another balance. Learning deducts the character's existing
`skillPoints`, records the exact cost, and updates the rank in one transition.
Debug reset returns only recorded costs. Repeating reset refunds zero. Imported
valid ranks without payment evidence remain learned with a zero paid ledger;
ranking them records only the new cost. They cannot mint retrospective refunds.

Migration adds empty learned/paid maps to saves without them, without awarding
points or retroactive learned skills. Invalid IDs/ranks and broken prerequisite
chains are discarded; invalid or excessive ledger entries default to zero.
These repairs grant no points. Valid existing progression, primary stats,
resource offsets, inventory, equipment, quest, claims, discoveries, selected
Nodes, position, currency and historical fields survive. Unknown historical
`loadout` fields are retained separately; they are not interpreted as new slots.
The existing resource compatibility calculation includes learned passives during
normalization, so repeated saves do not bake them into resource offsets.

Saves predating `actionLoadout` receive empty eight-slot data and explicit
`legacySkillControls=true`. This compatibility path keeps their authored four
buttons available at original runtime rank, with original Nodes, without making
them learned or assigned. This is deliberately a returning-save exception.
New Swordsman/Mage characters opt out and start with empty learned skills and
empty slots. Debug reset opts out of the old shortcut. Other prototype classes
retain their old fixed actions; their Base trees are outside this task.

Migration is pure, deterministic and idempotent; it grants neither EXP nor
levels nor points. The existing progression's debug level lowering semantics
are unchanged. Lowering Job Level does not unlearn or disable valid learned
skills; Job gates constrain the next learning operation.

## Developer tools and current integration limits

Serve the checkout and open `http://127.0.0.1:8011/tools/progression.html`.
The harness uses the existing isolated `astraeon-progression-dev-v1` save key.
It displays definitions, ranks, prerequisite gates, passive modifier output,
all eight slots and the compiled selected slot. Controls select class, add
points, learn/rank/reset, assign/clear, choose a compatible Node, and save/reload.
No learning formula is implemented in the presentation.

`/?qa=1&dev=1` enables these operations on a disposable playable character through
`AstraeonProgressionDev`. Live assignment, Node mutation and debug reset are
restricted to town or an existing safe camp with no active Timeline action.
Ordinary URLs expose no developer mutation API.

The repository originally had **four fixed skill buttons, not eight implemented
Action Slots**. This task adds the eight-slot model/API and bridges its first
four slots to the existing buttons without changing layout or styling. Slots
5–8 are inspectable/assignable/compilable in developer tooling; final controls,
items, weapon swaps, presets and in-combat full-slot cooldown changes remain
separate Action Loadout work. In-combat configuration is currently rejected,
so this task introduces no cooldown bypass via slot changes. The player's pure
adapter has no clock/combat access; the live game enforces this safe boundary.
New characters' learning/assignment is developer-only until the owner approves
production presentation. This work adds no final Skill UI or visual acceptance.

## Verification

```powershell
python tools/run-node-checks.py
python tests/skill_tree_browser.py --url http://127.0.0.1:8011
python tests/progression_browser.py --url http://127.0.0.1:8011
python tests/cache_resume.py --output cache-review
```

Python Playwright and a local Chrome/Chromium executable are required for browser
checks. Set `ASTRAEON_BROWSER` as documented in README. Node runs independently
of browser automation. The skill browser test uses disposable contexts, ordinary
creation/input for both classes, shared developer mutations, live ranked Node
execution, save/reload, returning-save compatibility and the isolated harness.
Cache checks also preserve learned ranks, paid costs, passive state and assigned
Nodes while offline. Boot/page/SW use version **86** and precache all skill modules
along with the [staged Combat Resolution extension](CORE_SPINE_COMBAT.md).
