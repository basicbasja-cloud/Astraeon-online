# Inventory Capacity / Weight — verified foundation handoff

This implements only this foundation. **Patch 0.0.1 and Core Spine are not complete.**
See [contracts and limitations](CORE_SPINE_INVENTORY_CAPACITY.md).

## Git identity and resume point

| Field | Value |
| --- | --- |
| Branch | `backbone/inventory-capacity-weight-0.0.1` |
| Starting parent branch | `backbone/monster-box-0.0.1` |
| Authoritative starting parent HEAD | `1e32ce4e17ae516b504a65e7a0a03db634ac62d4` |
| Runtime/test checkpoint | `0e4b20f565cdd5cbac9c001bec1295e68f18cca8` |
| Final HEAD | Documentation successor: resolve `git rev-parse HEAD` on the branch; exact final/push SHA is recorded in the final response and external FINAL_HANDOFF.md |

Step 0 fetched remote, switched/pulled ff-only, confirmed clean and created the
required branch. No stale SHA reset, unrelated merge, history rewrite or PR.
Runtime is stabilized and verification passed; no remaining implementation/test
failure. Final report commit and ordinary branch push complete this handoff.

## Architecture / integration report

| Requested field | Implemented contract |
| --- | --- |
| Capacity architecture | Pure derived authority over existing canonical ownership; Item State remains publisher |
| Capacity policy | Immutable validated bounded global policy; explicit technical unlimited mode |
| Slot-limit model | 100 provisional slots; safe integer limits |
| Weight-limit model | 1000 provisional weight; finite integer milliweight |
| Stack slot semantics | One positive definition stack; zero omitted; no fragments; maxStack distinct |
| ItemInstance slot semantics | One per owned canonical instance, stable serial |
| Equipped-item semantics | References to owned instance; counted once; equip/unequip zero delta |
| Item weight semantics | quantity × unit weight plus each instance once; all existing authored zeros retained |
| Numeric precision model | scale 1000, safe integer arithmetic, three decimals with scaled 1e-7 representation tolerance; tiny positive zero-rounding rejected |
| Capacity snapshot | Immutable slots/weight/remaining/over-limit flags; no mutation/cached counters |
| Candidate transaction model | Pure exact stack/instance debits and item rewards; no serial allocation |
| Net source/output calculation | Final ownership after sources removed and outputs merged; final source stack can free slot |
| Exact package preflight | Reusable Player/ItemState canAcceptItemPackage; canonical rules and final capacity agree |
| Maximum-envelope preflight | Full requested Box batch, conservative per-definition maxima and proven maximum instance count |
| Over-limit representation | Ownership loads intact; snapshot marks exceeded dimensions |
| Over-limit transaction policy | Per dimension after <= max(before, limit); no-worse/reducing allowed |
| Encumbrance penalty policy | No movement, Combat, stamina, skill or travel penalty |
| Monster Loot integration | Exact complete package preflight before item/currency/progression/quest publication; same cached live claim retry |
| Monster Box integration | Source debit + maximum envelope before RNG; exact check before canonical commit |
| Anti-roll-shopping preservation | Non-rolling prepare, duplicate/stale/foreign protection, hidden same-runtime late outcome retained; conservative rejection consumes no RNG |
| Action Item integration | Canonical consumption derives reduced capacity; cooldown/effect contracts unchanged |
| Merchant integration | Fitting purchase succeeds; capacity rejection charges no gold; reducing sale works over-limit |
| Crafting integration | Ingredient debit plus output preflight; rejection preserves ingredients and serial |
| Equipment integration | Existing equip/Stats/Combat path unchanged; no double count |
| Save/reload behavior | Existing ownership/serial persist; derived capacity recalculates; no ticket/reward replay |
| Returning-save compatibility | Over-limit items/gear not deleted or truncated; 20 cycles stable |
| Save version policy | 5 retained; pre-v5 migrations/future guard unchanged |
| Developer tooling | Isolated weighted capacity sandbox + exact dev=1 transient policy/evidence; normal grants respect capacity |

### Provisional/non-final data

Slot limit **100**, weight limit **1000**, all 15 production ItemDefinitions retain
explicit **0 / unconfigured** weight. No item/economy/drop/monster/recipe/price
balance changes. Isolated sandbox weights: herb .1, ore .2, shard .1, Potion .3,
Ration .2, Astral Blade .4, others zero. Tiny test profiles vary for exact/reject/
over-limit proof. No STR/class/bag progression, final penalties or final UI.

## Deterministic verification

`python tools/run-node-checks.py --node D:\Node\node.exe`

**1155 pass / 0 fail, 20 files**: 1010 prior checks retained + **145 new** checks.
All prior Node assertions are unchanged; 12 existing test files receive only the
required capacity import. Source audit preserves all 30 old Node/browser/cache
suites and 26 core/authored modules. New checks cover malformed policy/weights,
immutable snapshots, fractional boundaries/overflow, stack/instance/equipped
accounting, pure net transactions, maxStack, atomic serial safety, over-limit
recovery, Box pre-RNG envelope/bulk, Loot same-claim no-reroll retry, EXP/quest
atomicity, merchant/craft/pickup, Action Item/Stats/Combat, v1–5 migration/future
guard and 20 load cycles.

Review fixed malformed null debit/reward arrays and positive subprecision weights
in implementation, retaining assertions. No old assertions weakened or bypassed.

## Browser acceptance and local smoke

Disposable **Swordsman and Mage**, local Chrome, ordinary field gameplay plus
isolated deterministic fixtures. Full sequence completed without failed suite.
Final focused Capacity run after precision/sandbox changes also passed 63 groups;
counts below count each suite once, not repeat runs.

| Suite | Pass groups | Fail |
| --- | --- | --- |
| `inventory_capacity_browser.py` | 63 | 0 |
| `monster_box_browser.py` | 33 | 0 |
| `monster_lifecycle_browser.py` | 30 | 0 |
| `monster_loot_browser.py` | 26 | 0 |
| `action_item_browser.py` | 30 | 0 |
| `inventory_browser.py` | 15 | 0 |
| `action_loadout_browser.py` | 17 | 0 |
| `combat_browser.py` | 21 | 0 |
| `skill_tree_browser.py` | 11 | 0 |
| `progression_browser.py` | 7 | 0 |
| **Total functional groups** | **253** | **0** |

**190 previous browser groups retained**, **63 new focused groups**. All nine
previous functional browser files and cache test are unchanged. Runtime/console/
page/HTTP error gates passed. New suite's high-level UI Bag opening, merchant/
crafting, learned skill and Basic Attack encounters, exactly-once per-life Loot,
second life, actual player death/respawn, town/field travel, save/reload, normal
URL mutation absence, gear → Stats → Combat and Action Item smoke passed for both
classes. Weighted fixtures verify exact/over slots/weight, rejected ownership/
serial, equip invariance, pre-RNG Box rejection, exact Box instance/stack weight,
net craft, purchase charge safety, over-limit sell/recovery and saved capacity.
No visual/art/animation acceptance is claimed. Full boss encounter was not a
new browser itinerary; Dungeon package safety is covered by the shared atomic
package contract and source review, not a claim of new boss acceptance.

### Cache/world/audit

- `python tests/cache_resume.py`: `astraeon-static-v93`, **150 cached responses**,
  old cache removed, offline saved character/town reload, source/ground digests,
  returning world-position recovery and no errors passed.
- `python tools/validate-world-v3.py`: Terrain, Navigation, TownObject and
  AnimationManifest schemas passed.
- `git diff --check`: passed; source audit confirms no protected changes.
- Boot/page/cache is **93**, capacity loaded before Item State. Unchanged Loot
  v90 and Box v92 explicit cache URLs remain actually precached for old tests;
  scripts execute once via current boot URLs.

## Known limitations / overflow / timing

1. Full-inventory Loot rejects the complete composite package. The unchanged live
   entitlement can retry after freeing capacity, but production has no pending-
   loot retry UI. Respawn, retirement, travel or reload may expire it. No false
   success, reroll, ground overflow, mailbox or durable retention is introduced.
2. Box envelopes intentionally overestimate mutually exclusive per-definition
   rewards/weights. Capacity can reject despite a particular outcome fitting.
   This preserves pre-RNG anti-shopping, including reload.
3. Existing authored zero weights mean ordinary production weight is currently
   zero; weighted enforcement is proved with isolated data. Final weights/limits
   require owner balance decisions.
4. Trusted synchronous policy/catalog/reward callbacks remain a local-authority
   boundary; arbitrary external side effects are not universally rollbackable.
   No server security claim.
5. No Storage/overflow/gear-sale UI or encumbrance penalties. Current canonical
   removals/sales can improve over-limit ownership. Transient dungeon completion
   can retry its same fixed package; existing reload/travel run retirement stays.
6. Unchanged Loot browser Mage recorded one bounded Basic Attack retarget and an
   offscreen waypoint timeout followed by its existing keyboard approach fallback
   (player HP 174, field zone 2, no active action/menu/navigation). The suite then
   passed every original reward/death assertion with no runtime/HTTP errors.
   Capacity-focused initial/full runs had no timing observations. Evidence is
   retained separately; no Combat/AI formula or old assertion was changed.

Potential merge conflicts: canonical `item-state.js`, Player option adapter,
`game.js` QA/death/dungeon glue and cache/import version lists. Coordinate those
paths with other Backbone branches; do not merge World/Character work here.

Files intentionally untouched: authoring, RO3 Ref, assets/world/Blender, renderer,
lighting/geometry/sprites/atlases/animation/VFX/camera/style and visual evidence;
Progression/Stats/Skill/Combat/Action Item/Loadout/Save/Loot/Box/Lifecycle core,
authored item weights/prices/recipes/tables and historical reports.

## Files

Added:

- `docs/CORE_SPINE_INVENTORY_CAPACITY.md`
- `docs/CORE_SPINE_INVENTORY_CAPACITY_REPORT.md`
- `inventory-capacity.js`
- `tests/inventory-capacity.test.cjs`
- `tests/inventory_capacity_browser.py`
- `tools/inventory-capacity-harness.js`
- `tools/inventory-capacity.html`

Modified:

- `ARCHITECTURE.md`
- `README.md`
- `boot.js`
- `docs/CORE_SPINE_ITEMS.md`
- `docs/CORE_SPINE_MONSTER_BOX.md`
- `docs/CORE_SPINE_MONSTER_LIFECYCLE.md`
- `docs/CORE_SPINE_MONSTER_LOOT.md`
- `game.js`
- `index.html`
- `item-inventory.js`
- `item-state.js`
- `player-state.js`
- `sw.js`
- `tests/action-item.test.cjs`
- `tests/action-loadout.test.cjs`
- `tests/action-runtime.test.cjs`
- `tests/combat-resolution.test.cjs`
- `tests/compatibility-hardening.test.cjs`
- `tests/item-inventory-equipment.test.cjs`
- `tests/monster-box.test.cjs`
- `tests/monster-lifecycle.test.cjs`
- `tests/monster-loot.test.cjs`
- `tests/motion.test.cjs`
- `tests/save-progression.test.cjs`
- `tests/skill-tree.test.cjs`
- `tools/combat.html`
- `tools/inventory.html`
- `tools/monster-box.html`
- `tools/monster-lifecycle.html`
- `tools/monster-loot.html`
- `tools/progression.html`

## Evidence / exact final Git state

External evidence: `D:\Astraeon\backbone-verification\inventory-capacity`:
`node-runtime-final/report.json`, `final-browser/runner.json`, each suite's
`report.json`/log, `browser-runtime-final/report.json`, `world-validation.log`,
`final-source-audit.json`, retained-assertion audit and `FINAL_HANDOFF.md`.
Repository state alone is sufficient to resume: checkout this branch, read this
report/contract and run README commands. No session-only implementation remains.

After the final documentation successor and push:

```powershell
git status --short        # expected empty
git rev-parse HEAD        # exact final documentation HEAD
git log --oneline -12
```

Recommended next Backbone task: **Equipment Slot Closure foundation**, with
owner-authored slot/content decisions; Quest and Storage remain separate tasks.
This handoff does not declare Patch 0.0.1 or Core Spine complete.
