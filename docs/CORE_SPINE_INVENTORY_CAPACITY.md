# Inventory Capacity / Weight foundation

This implements only the Patch 0.0.1 capacity foundation. Core Spine and Patch
0.0.1 remain incomplete. Values below are mechanical proof configuration, not
approved inventory balance.

## Authority and policy

`inventory-capacity.js` is a pure derived read/preflight module.
`item-state.js` remains the live ownership publisher. ItemInventory builds pure
canonical candidates; capacity neither owns items nor publishes inventory.
No current-weight, slot, overweight or capacity-profile fields are persisted.

The immutable default policy is bounded **100 slots / 1000 weight**, with
`overLimitPolicy: 'no-worse'`. These conservative provisional global limits
preserve ordinary prototype play. They are independent of Stats carryWeight,
class, STR and equipment bonuses. Technical unlimited mode is explicit:
`mode: 'unlimited', slotLimit: null, weightLimit: null`; it is never an implicit
large sentinel. The normal game uses bounded mode.

Policy validation rejects missing/unknown fields, non-finite/negative limits,
fractional/unsafe slot limits, unsupported precision and malformed JSON metadata.
Metadata is plain acyclic JSON, finite numbers, maximum depth 64. Validation and
snapshots return immutable copies without freezing callers' mutable input.

## Slot and weight semantics

| Canonical ownership | Slots | Weight |
| --- | --- | --- |
| Positive definition-ID stack | One per definition, independent of quantity | quantity × authored unit weight |
| Zero stack | Zero; normalization removes it | Zero |
| Owned non-stack ItemInstance | One per instance | definition unit weight |
| Equipped ItemInstance | Already included once as owned inventory | Already included once |
| Quarantined unknown/invalid historical item | No active ownership slot | No active weight |

There are no stack fragments. maxStack is a separate canonical limit; exceeding
it rejects instead of creating hidden stacks. Equip/unequip changes references,
not ownership, and has zero capacity delta. An invalid active inventory rejects;
capacity never silently repairs it.

All 15 existing authored definitions retain explicit zero/unconfigured weight,
including the proof Box. No realistic or final weights are invented. Nonzero
weights in the isolated harness/tests demonstrate enforcement only.

Arithmetic uses **integer milliweight units (scale 1000)**. Authored weights and
weight limits support at most three decimals. A scaled rounding tolerance of
`1e-7` accommodates Number representation noise, not authored extra precision;
positive values that would round to zero reject. Multiplication and accumulation
must remain nonnegative safe integers. INVALID_WEIGHT / WEIGHT_OVERFLOW fail
closed; no NaN/Infinity snapshot or repeated load drift is accepted.

## Read model and pure transactions

Player/ItemState APIs:

- `getInventoryCapacityState()` derives immutable stack/instance/occupied slots,
  weight units/totalWeight, limits, clamped remaining capacity and over-limit flags.
- `getCarriedWeight()` delegates to that authority.
- `canAcceptItemPackage({stackDebits, instanceDebits, itemRewards})` simulates
  final ownership without mutation, serial allocation, RNG or presentation.
- `grantItemPackage(itemRewards)` publishes one capacity-checked canonical package.

The pure module also exposes `validatePolicy`, `snapshot`, `evaluate`,
`evaluateOwnership` and `envelope`. Source debits happen before outputs in the
simulation. Debits validate ownership; equipped instances cannot be removed.
Rewards validate definitions, integer quantities, maxStack, finite weight,
processing bounds and serial feasibility. Exact results contain `before`,
`after`, slot/weight `delta`, over-limit flags and structured `code` /
`blockedReason`, plus `dimension` on capacity rejection.

Removing a final Box/ingredient stack can free its slot for an output. Removing
only part keeps its slot. Adding to an existing stack uses no new slot; added
weight still counts. Simulated final ownership agrees with actual canonical
publication. Failure allocates no ItemInstance, advances no serial and changes
no ownership/revision/currency/resources.

Useful codes include INVALID_CAPACITY_POLICY, INVALID_INVENTORY, INVALID_PACKAGE,
INVALID_WEIGHT, WEIGHT_OVERFLOW, SLOT_LIMIT_EXCEEDED, WEIGHT_LIMIT_EXCEEDED,
OVER_LIMIT_WORSENED, STACK_OVERFLOW, SERIAL_EXHAUSTED and REWARD_SIZE_LIMIT.
maxStack failure is distinct from capacity failure.

## Returning and over-limit ownership

Over-limit ownership loads normally and is not truncated, destroyed, sold or
repaired. Capacity reports the state explicitly. Each bounded dimension accepts
only `after <= max(before, limit)`. Therefore an already exceeded dimension may
decrease or remain unchanged; it cannot worsen. A previously fitting dimension
must remain within its limit. Slot and weight dimensions are tested independently.

Consumption, sale, permitted removals and zero-delta equip remain possible.
Zero-weight additions to an existing stack can be no worse even when over slots.
There are **no movement, Combat, stamina, Skill or travel penalties**. Ownership
recovery does not require an alternate capacity counter or manual free-slot API.

## Exact packages and maximum envelopes

Monster Loot, purchases and crafting have fixed outcomes and use exact preflight.
Loot still owns death/life claims and cached immutable resolution. Capacity rejects
the complete composite reward before items, gold, Base/Job EXP or quest credit
publish. It never rerolls or grants a fitting subset. The same live entitlement
can retry its original package after space is freed; duplicate success rejects.
The existing life/runtime retirement boundary still applies: respawn, travel or
reload can expire an uncommitted entitlement. There is no production pending-loot
UI, ground overflow, mailbox or durable recovery. A blocked kill has a structured
failure and visible notice, not a false reward success.

Monster Box uses the existing **maximum envelope before RNG**, including the
requested batch and source Box debit. Prepare checks the envelope without entropy;
commit checks it again before rolling and then validates the exact package before
publication. Final source-stack removal can free a slot. Stack maxima and weight
maxima across possible choices are conservatively summed; instance slots use the
table's proven maximum instance count. Mutually exclusive reward maxima may cause
a rejection even when one particular outcome would fit. This is intentional
anti-roll-shopping behavior. No outcome is shown on rejection, no source is
consumed, and duplicate/stale/foreign tickets never roll again. Existing private
late-failure outcome retention remains unchanged for trusted adapter failures.

## Current gameplay integrations

| Path | Capacity boundary |
| --- | --- |
| Monster Loot | Exact complete package before existing reward orchestration |
| Monster Box | Pre-RNG batch envelope with source debit; exact commit check |
| Merchant purchase | Canonical item preflight before gold publication |
| Merchant sale | Canonical removal; allowed when no worse |
| Crafting | Ingredients plus output as one net candidate; failure retains inputs |
| Action Item | Existing consumption; derived capacity decreases automatically |
| Equip/unequip | Same owned instance; zero delta, no double count |
| Exploration pickup | Canonical grant must succeed before pickup claim/rewards |
| Dungeon completion | One fixed mixed item package before completion rewards |
| Existing developer grants | Respect canonical capacity |

No prices, recipes, drop tables, Box tables, monster coefficients or Action Item
cooldowns change. Monster Lifecycle knows no capacity arithmetic. Dead monster
presentation timestamps are still set on a capacity-blocked death; no extra
death event or loot roll is introduced. Dungeon capacity failure keeps the
current unfinished encounter available for the same fixed-package retry; this
does not add persistence of transient dungeon runs.

## Save, runtime and trust boundaries

Save version stays **5**. Remaining Boxes, committed stacks/instances and serial
persist through existing ownership serialization. Capacity recalculates from
ownership, definitions and the current policy. No pending Box tickets, policy
override, cached capacity or AI state persists. Reload rebuilds authorities and
invalidates old tickets; death/respawn/travel do not refund or replay rewards.
Pre-v5 migration and the future-version rejection guard are retained.

ItemState checks candidates before live publication and before existing trusted
reward callbacks. Nested mutation protection/revision checks are retained. Policy
and catalog providers are trusted synchronous, stable, side-effect-free adapters.
Arbitrary external callbacks are not database transactions and cannot be rolled
back universally. This is local integrity, not tamper-proof server authority.

## Developer tools and scope

`/tools/inventory-capacity.html` uses isolated `astraeon-capacity-dev-v1` storage,
never playable save keys. It provides tiny profiles, exact/envelope preflight,
stack/gear grants, equip, buy/sell/craft, Action Item consume, controlled Box/Loot,
fixed RNG draw counts, save/reload and immutable evidence. Explicit fixture import
creates over-limit returning ownership; normal grants still respect capacity.
Isolated weights: herb .1, ore .2, shard .1, Potion .3, Ration .2, blade .4;
Box and other definitions remain zero. All are non-final proof numbers.

Only exact `dev=1` game URLs expose `AstraeonInventoryCapacityDev` with snapshot,
preflight and transient validated test-policy controls. Policy changes invalidate
prepared actions. Technical unlimited mode can be selected explicitly there;
ordinary gameplay exposes no developer mutation/bypass API. Read-only QA capacity
evidence is available to existing acceptance tooling. No production UI redesign
or Box bulk modal is introduced.

Tests: `tests/inventory-capacity.test.cjs`,
`tests/inventory_capacity_browser.py`; see the [verification handoff](CORE_SPINE_INVENTORY_CAPACITY_REPORT.md).
Future work includes final limits/weights, equipment-slot closure, capacity
progression, explicit overflow retention, Storage and gameplay encumbrance rules.
