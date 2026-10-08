# Patch 0.0.1 Monster Box Item / Opening foundation

This extends canonical Item ownership after Monster Lifecycle. It implements only
the Box foundation; **Patch 0.0.1 and Core Spine remain incomplete**. Content,
probabilities and quantities below are mechanical proof data, not approved game
design or economy.

## Responsibilities

| Module | Authority |
| --- | --- |
| `item-definitions.js` | Immutable stackable Box capability and content-table reference |
| `box-content-tables.js` | Separate immutable authored Box contents |
| `monster-box.js` | Pure validation, compilation, maximum package envelope and injected-RNG resolution |
| `monster-box-runtime.js` | Owned non-rolling authorization, commit-time RNG and private failed-outcome retention |
| `item-state.js` | Existing canonical ownership; contained source debit and complete reward publication |
| `player-state.js` | Private Item/Character attachment and high-level opening APIs |
| `game.js` | Existing Bag single-open adapter, context invalidation, save and bounded result presentation |
| `tools/monster-box.html` + harness | Isolated developer inspection and deterministic single/bulk actions |

Monster Drop Table answers what a death awards. Box Content Table answers what an
already-owned Box contains. They have separate registries, definitions, RNG
events and execution authority. Opening uses no monster, spawn, life, death or
Loot claim identity. Lifecycle continues to call existing Loot without knowing
anything about opening.

## Canonical Box definition and ownership

`monster-box-proof` is the only new Box definition. Its immutable capability is
`kind: 'monsterBox'`, `stackable: true`,
`openable: {boxContentTableId: 'box-proof-basic'}`. It uses the existing canonical
`itemInventory.stacks` quantity, with no per-Box instance, RNG state, claim,
timestamp or secondary inventory. Its technical maxStack is the existing safe
integer ceiling; weight zero is unconfigured proof data, not a final weight rule.

It has no Action Item effect/cooldown, learned rank, Skill Point cost or HP/SP
semantics. It cannot occupy learned slots 1–8. Basic Attack, learnedSkill,
actionItem and inventory/openableItem remain separate action sources.

## Box Content grammar and validation

A table has `id`, nonempty ordered `entries`, and optional JSON `metadata`.
Each entry has unique `id`, known `itemId`, positive safe integer `minQuantity`
and `maxQuantity`, `rollMode`, optional `weight` and optional JSON `metadata`.

Supported modes are deliberately small:

- `guaranteed`: awarded once per opened Box, with no choice weight.
- `weighted`: one entry selected from all positive-weight entries per Box;
  weight is a finite nonnegative relative weight. A weighted set requires a
  finite positive total. Zero-weight entries never select.

One table may combine guaranteed entries and one weighted choice set. Independent
chance rolls, multiple weighted groups, conditions, currency and scripting are
unsupported and reject. A future grammar extension belongs to this separate
contract, not Monster Drop Table reuse.

Validation rejects unknown tables/items, mismatched referenced table ID,
empty/malformed tables, duplicate identities, unsupported keys/modes, NaN,
Infinity, negative/zero-invalid quantities, fractions, min > max, bad weights,
zero/overflow total weight and non-JSON metadata. JSON is plain acyclic data with
finite numbers; functions, Dates and cycles reject. Compilation checks Box
capability, immutable data and absence of Action Item effects. Direct source-Box
self-reference rejects. Another openable reward can remain owned, but never
automatically opens. Production proof has no recursive chain.

Failures are immutable structured `{ok:false, code, blockedReason, path}` where
applicable. There is no silent authored-data repair. All authored validation and
whole-batch eligibility happen before production entropy or ownership mutation.
Technical guards are 256 table entries, JSON nesting 64 and 10,000 Boxes per
request. They bound processing; they are not inventory capacity or a final UI
bulk maximum. The existing reward planner also bounds equipment units at 10,000.

## Pure deterministic resolution

`AstraeonMonsterBox.resolve(table, count, rng, {catalog})` accepts only an injected
`rng.next()`. Every draw must be finite in `[0,1)`; errors or exhausted/invalid
providers reject the whole candidate. No `Math.random`, clock, player, inventory,
currency, serial allocator or storage exists inside the resolver.

Stable RNG order for each Box is:

1. One choice draw when positive weighted entries exist, using authored order
   and `needle < cumulativeWeight` boundaries.
2. Accepted entries visited in authored order. A ranged quantity consumes one
   draw; a fixed quantity consumes none.
3. Continue with the next Box's choice and quantity draws.

Guaranteed-only fixed tables need no entropy draws. Results contain ordered
`boxes` with index, draw purpose/value and selected item quantities, plus aggregate
`itemRewards` in first-encounter order. Same table/count/continuous RNG sequence
produces the same result. Bulk and repeated single openings have the same ordered
outcomes/reward multiset; there are no batch-specific rewards. Resolution is
deeply immutable and never allocates equipment or changes ownership.

Empty tables reject, and every valid table guarantees at least one selected or
guaranteed positive reward per Box. An empty result is not a supported Box policy
in this foundation. This differs from valid no-drop Monster Loot.

## Prepare, commit and anti-roll-shopping

Player APIs are `getMonsterBoxState`, `prepareMonsterBoxOpen`,
`commitMonsterBoxOpen`, `openMonsterBoxes`, `getMonsterBoxRuntime` and
`invalidatePreparedMonsterBoxes`. `openMonsterBoxes(id, count)` performs prepare
and commit synchronously. Count must be positive, safe integer and within owned
quantity/processing guard.

Prepare validates definition/table/count, canonical ownership, actor HP, context,
restrictions and the maximum possible reward envelope. It consumes no Box,
entropy or serial, grants nothing and exposes **no rolled contents**. Its frozen
ticket contains source, opening ID, Box/table ID, requested count, quantity before
and `authorizationOnly: true`.

An exact ticket object is owned through a private WeakMap. Runtime epoch,
canonical inventory object identity, Item State revision and compiled content
signature bind it. The revision changes for successful inventory/equipment
transactions; failed operations do not advance it. Copies, forged/foreign tickets,
modified requests, old-runtime tickets and stale inventory/equipment/context
reject before entropy. Successful commit marks the ticket consumed and advances
epoch, invalidating sibling preparations. Repeated preparation cannot reveal
candidate outcomes, and duplicate/stale commit cannot roll again.

The RNG provider belongs to the runtime owner, not an arbitrary opening request.
Production supplies the existing outer random adapter; exact dev tooling can
inject sequences for proof. The pure resolver is an inspection utility and does
not confer opening authorization.

After an authorized attempt, one private pending outcome is retained if RNG or
post-roll acceptance fails. Failure output reveals no rewards. Retrying the same
request, preparing again, changing unrelated inventory, invalidating tickets or
changing the provider cannot select a new roll in that runtime. A different
Box/count is blocked while pending. A failed RNG attempt also stays attempted.
No abandon/reroll mutation API exists. Retirement blocks further use.

## Atomic single and bulk ownership commit

`monster-box.js.envelope` calculates conservative maximum reward quantities and
maximum equipment units for the entire batch without rolling or allocating
instances. Item State checks the pure debit candidate, every possible stack
addition, existing safe serial space and reward processing bounds **before RNG**.
For mutually exclusive equipment choices it counts the maximum possible choice,
not the sum of all choices. This prevents stock overflow/serial failure from
filtering random outcomes, including after a reload.

`item-state.js.canOpenable` is the pre-roll acceptance boundary;
`commitOpenable` is the contained exact reward transaction. Both are private to
Player integration. They reuse the existing item reward planner rather than Loot
death claims. Commit locks nested canonical mutations before calling RNG, builds
a local source-debit candidate, resolves all Boxes, plans all stack/instance
rewards, calls exact package acceptance and checks existing equipment publication.
Only then does it publish one canonical inventory and advance revision.

All ordinary supported rewards publish together or leave source quantity,
stacks, equipment and persistent serial unchanged. No Box is deleted on failure.
Stack rewards aggregate by definition ID and allocate no serial. Each equipment
unit uses existing `ItemInventory.createInstance`: stable unique `item-N`, exact
serial advance, canonical definition reference and **no auto-equip**. Existing
Equipment → Stats → Combat remains the only gear modifier path. Compatibility
views derive from canonical ownership as before.

Success exposes `openedCount`, requested count, Box/table/opening identity,
quantity before/after, per-Box evidence, `aggregatedStackRewards`,
`instanceRewards`, serial before/after and authored metadata. Failure exposes
structured rejection with `openedCount:0`, `consumed:false`; presentation need
not infer rewards from inventory differences.

## Currency, progression, Loot and Action Item boundaries

Currency contents are omitted. Existing Player monster reward orchestration is
coupled to kill progression/quest adapters; Box reuses only the small canonical
item planner. It creates no parallel currency state and leaves gold unchanged.
Opening grants no Base EXP, Job EXP, Skill Points, learned ranks, quest kill
credit, kill count, death claim or respawn state.

The isolated `proof-monster-box` Monster Drop fixture awards Box x1 with a
provisional guaranteed drop. Existing Loot commits it as an ordinary stack and
does not open it. Production monster tables, death RNG and kill reward values
are unchanged. The later explicit opening is a separate RNG event. No field
monster now drops Boxes by default, and Lifecycle modules remain unchanged.

Potion/Ration contents remain ordinary canonical consumables usable by Action
Item authority. Healing cooldown does not block opening and opening neither
starts nor resets it. No Action Loadout/Combat formula changes are required.

## Bag, context and lifecycle integration

The current Bag displays owned canonical Box stacks using its existing card and
button layout. Its single `Open` action dispatches by definition capability to
the Box runtime; Potion/Ration retain the separate Action Item dispatcher. Bulk
opening is an API/dev action, with no quantity modal, reward reveal, animation,
production debug UI or new visual assets.

Alive valid actors may open through ordinary inventory menus in town, field or
dungeon. Loading/transition, missing/dead actor, retired runtime, invalid context
or authored restrictions block. There is no new combat, town-only or cooldown
rule. Shared death/respawn/travel/class invalidation and the loading entry
boundary invalidate transient authorizations without refunding or changing
committed items. Same-runtime private pending outcomes are retained across ticket
invalidation. Old offensive monster/combat behavior is unaffected.

## Save/reload and trust boundary

Save version remains **5**. Unopened quantities, committed contents, canonical
equipment instances, equipped references and nextItemSerial already fit the
existing schema. Pre-v5 migration and future >5 guards are unchanged. Repeated
normalization does not open Boxes, replay results or refund consumed quantities.
Tickets, revision counters, RNG execution and pending requests are transient.
Fresh Player/runtime recreation rejects old tickets; no automatic open occurs.

This protects local supported runtime operations, not browser storage editing,
arbitrary script access or server/network security. Canonical Item callbacks,
catalogue, RNG provider and synchronous Character/acceptance adapters are trusted.
Nested canonical mutation/opening rejects under the transaction lock. Arbitrary
external side effects inside a custom callback cannot be rolled back.

Current production has no outcome-sensitive late capacity rejection. Pre-roll
envelope acceptance prevents every supported deterministic ownership failure
before entropy, even after reload. A future custom post-roll hook can reject
while preserving one hidden outcome only in the same runtime; pending outcomes
are not persisted. Before enabling outcome-sensitive rejection across reload,
capacity must accept the complete envelope before RNG or establish a durable
pending-outcome policy. This is an explicit future integration requirement, not
a claim of persisted failed-roll protection.

## Provisional proof and developer tooling

`box-proof-basic` selects one of Herb x2–3, Potion x1 or existing Astral Blade x1
with relative weights 1/1/1. Only the first outcome needs a quantity draw. All
weights, quantities, names and the isolated Box drop probability are replaceable,
authored **NON-FINAL** fixtures. No rarity, paid box, tier, pity, keys, affix,
enhancement or final economy is introduced.

`/tools/monster-box.html` inspects definition/table validation, canonical quantity,
revision/serial, authorization, per-Box rolls, aggregate rewards and duplicate or
stale failures. It supports add one/several, fixed RNG, prepare/commit, single,
bulk, inventory mutation and isolated save/reload. Its only storage key is
`astraeon-monster-box-dev-v1`; it never touches the playable character key.
Exact `?dev=1` exposes bounded `AstraeonMonsterBoxDev` actions on disposable live
characters; normal URLs expose no Box mutation API. QA result evidence is bounded
to the latest 32 successes. Boot/page/cache **92** loads/precache the three new
modules. Historical Loot v90 precache URLs remain for the prior explicit contract.

Run commands in README and see [verified handoff](CORE_SPINE_MONSTER_BOX_REPORT.md)
for deterministic/browser/smoke results. No visual acceptance is claimed.
Recommended next Backbone task: **Inventory Capacity / Weight foundation**.
