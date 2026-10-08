# Core Spine — Monster Drop / Loot Resolution

Patch **0.0.1 foundation only**. Save version **5**; current boot/page/cache
version **91**. This continues the Action Item foundation. Patch 0.0.1 and the
Core Spine are **not complete**.

## Responsibilities

| Boundary | Owner |
| --- | --- |
| Existing actor reward references | `monster-definitions.js` |
| Immutable authored tables | `drop-tables.js` |
| Validation and pure deterministic roll | `loot-resolution.js` |
| Runtime instance/life/death/entitlement authority | `monster-loot-runtime.js` |
| Kill progression, quest and currency orchestration plan | `monster-rewards.js` |
| Mixed canonical stack/instance transaction | `item-state.js` |
| Staged Base/Job EXP using existing Progression and Stats | `character-state.js` |
| Contained transaction across these authorities | `player-state.js` |
| HP-zero notification, actor spawning, existing presentation/save | `game.js` |

The existing actor factory still owns combat HP and prototype movement data.
Reward definitions reference `id`, `dropTableId`, `rewardProfileId`; they do not
duplicate AI stats, renderer data or runtime claims. Eight existing species,
the current guardian, sparring compatibility and the old Echo reward path are
references for existing prototype behavior, **not a final monster catalogue**.

## Authored Drop Table and validation

```js
{
  id: 'proof-multi',
  entries: [{
    id: 'material', itemId: 'herb', rollMode: 'independent',
    chance: 0.5, minQuantity: 1, maxQuantity: 3
  }],
  currency: {base: 7, perZone: 0},
  metadata: {fixture: true, balance: 'non-final'}
}
```

Tables and nested entries are frozen authored data. No claim or ownership state
is stored in them. Probabilities are fractions in **[0,1]**. Supported modes are
`independent` and `guaranteed`; guaranteed requires chance 1. Each independent
entry is considered in authored order. IDs are nonempty unique strings within a
table. Quantities are positive safe integers, inclusive minimum/maximum.

`validate(table, {catalog})` and `validateReference(id, {tables,catalog})` return
frozen structured success or `{ok:false,code,path,itemRewards:[],currencyRewards:[]}`.
Unknown references/items, malformed tables/entries, duplicates, unsupported modes,
negative/out-of-range/non-finite chances, invalid integers/ranges and invalid
currency/conditions reject. All entries validate **before any RNG is called**.
Production authored data is never repaired or clamped into validity.

Metadata/context must be finite, acyclic plain JSON data. Technical safety bounds
are 256 entries, metadata nesting 64, and at commit 10,000 equipment units per
package. These are bounded processing guards, **not inventory capacity or final
drop balance**. Extremely large stack grants still use the canonical maxStack
and safe-integer overflow checks.

The only implemented conditional extension is `{killModulo:N}`. It retains the
prototype's global kill cycles: Ore every third kill, Herb every second, Shard
every fourth. It is not a probability or a new balance decision. Future weighted
groups/conditional predicates must introduce validated semantics separately;
unknown modes already reject rather than silently being interpreted.

## RNG and pure resolution

```js
const result = AstraeonLootResolution.resolve(table, {
  monsterDefinitionId: 'leafmane-fox', monsterInstanceId: 'monster-1',
  deathId: 'monster-1:life-1:death-1', lifeGeneration: 1,
  zone: 2, killOrdinal: 1, quest: null
}, {next: () => 0.25});
```

No Math.random, time, inventory, currency setter or ItemInstance allocator exists
in the pure resolver. It validates and snapshots authored data and context before
calling the injected `next()`. Same data/context/sequence produce identical frozen
results. Production adapts Math.random only through the existing outer runtime
RNG helper. Tests inject exact sequences; thrown/exhausted/non-finite/out-of-range
entropy rejects the entire candidate.

Roll values must be **0 <= value < 1**. A chance roll succeeds exactly when
`value < chance`. Zero and guaranteed chances consume no entropy. Successful
ranged quantities consume the next value and calculate
`min + floor(value * (max - min + 1))`; equal quantities consume none.

Results explicitly contain death/monster/table identity, captured context,
`rolls`, `itemRewards`, `currencyRewards` and authored metadata. Resolving grants
nothing and allocates no serial. An empty `itemRewards` array is successful;
currency/progression/quest may still be present independently.

## Death identity and entitlement

```js
const loot = AstraeonMonsterLootRuntime.create({
  commit: (resolution, profile) =>
    player.commitMonsterRewards(resolution, profile, authoredContracts)
}, {initialKillOrdinal: savedPlayer.kills});

loot.register(actor, 'leafmane-fox'); // Actor must initially have positive HP.
// Existing combat authority applies damage and reaches EXACT HP zero.
const claim = loot.prepareDeath(actor,
  player.getMonsterRewardContext(zone), rng);
const committed = claim.ok ? loot.commit(claim) : claim;
```

Private WeakMaps own actor registrations and claim tickets. Instance serials
increase throughout one controller lifetime and are not reused on travel.
Identity is `monster-N:life-M:death-1`. It uses neither definition ID alone,
coordinates, random UUIDs nor equality of item results. Equal species at equal
coordinates are independent actors. Negative HP is not an accepted authoritative
zero-death notification; the existing Combat HP application clamps to zero.

Each life caches its **first resolution attempt**, including invalid entropy.
Repeated notification returns the same claim/result and does not reroll.
Immutable inspectable claim data confer authority only when the exact object is
in the creating runtime's WeakMap. Copies, forged values and another controller's
claims reject `INVALID_CLAIM`. Used claims reject `ALREADY_COMMITTED`. Actor revival,
new life and retired populations reject unconsumed stale claims.

Commit failure retains a pending exact claim; retry uses the same resolved items,
not fresh entropy. A future capacity owner can reject a commit with a structured
reason and retain that entitlement for an explicit retry. There is no overflow
mailbox/ground redirect, final capacity rule or production pending-loot UI here.
Travel/retirement currently discards unresolved transient entitlements; a later
capacity/pickup system must explicitly choose retention before allowing travel.

Ordinary death notifications reserve distinct kill ordinals even if multiple
claims are pending; out-of-order commits cannot reroll those item results. Proof
fixtures do not advance the production kill cycle. A failed notification may
leave a reserved ordinal gap; valid current direct commits have no gap. This
technical death counter is local and transient, not server authority.

## Atomic reward commit

The Player adapter performs these operations synchronously, without yielding:

1. Validate the profile, current compatibility currency/counters and quest rewards.
2. Build a pure reward plan with explicit currency, Base/Job EXP and quest credit.
3. Validate plain writable publication fields and precompute both progression
   transitions plus derived Stats through the existing Progression/Stats functions.
4. Plan every stack addition and canonical equipment allocation against a local
   immutable inventory candidate. Any malformed item, stack/serial overflow or
   processing bound failure stops before publication.
5. Validate equipment modifiers using the existing item transaction boundary.
6. Publish the owned prevalidated Character plan and plain local currency/quest
   fields, then publish the planned canonical inventory once.
7. Mark the claim used and record one immutable commit event.

There is no second inventory. Stack rewards call canonical `addStack` planning;
compatibility counters read the canonical view automatically. Stack-only packages
do not advance `nextItemSerial`. Each equipment unit calls canonical
`createInstance`, gets the next unique `item-N`, and remains **unequipped**.
Existing Equipment → Stats → Combat remains the route for using looted gear.
Affixes, enhancement, sockets, rarity, durability and binding are excluded.

Commit results include claim/death ID, `committed`, `stackRewards` with exact
before/after quantities, canonical `instanceRewards`, serial before/after,
currency before/after/granted, Base/Job EXP and levels gained, kill/quest credit
and completed quest evidence. Presentation consumes these results directly.
Failure exposes a structured code/blockedReason and `committed:false`.

### Trust boundary

This is local client integrity, **not security against modified JavaScript or a
server transaction**. The current internal publisher uses owned staged Character
plans and prevalidated plain writable save fields. It cannot throw halfway under
the normal local-state contract. Generic callback exceptions before publication
leave ownership unchanged; nested inventory/claim transactions are blocked.

Custom owner callbacks, conversion hooks, catalogs and low-level publication
callbacks are trusted synchronous code. Arbitrary external side effects, Proxy
objects, hostile accessors or a callback that mutates unrelated authorities and
then throws are not rollback-capable. Do not install such a publisher. The low-level
arbitrary item publication callback is excluded from Player/live developer exports.
Future unrelated authorities must prevalidate and honor a non-throwing publisher,
or introduce a real transaction coordinator before being added.

## Currency, progression and quests

Gold remains the existing `state.gold` authority shared with merchant/save/travel.
Its existing nonnegative finite balance range is retained, including fractional
legacy balances; rewards are authored safe-integer amounts. No currency model or
denominations are redesigned.
Normal kill gold remains **4 + zone*2**. Sparring retains the additional 10 and
one PvP win; the legacy outdoor Echo table retains additional 50 gold/3 Shards.
That Echo compatibility path remains dormant in the current eight-species field
factory; this task does not create new Echo content.

Loot does not own progression. `monster-rewards.js` profiles request the existing
Base EXP value **(boss ? 25 : 7) + zone*3**, with Job EXP using the existing activity
ratio. Quest completion keeps its existing gold, two Shards, EXP, clear count,
five reputation, journal and rank behavior. Separate kill/quest XP contributions
retain their individual Job-EXP flooring. Character uses Progression's existing
grant transitions and refills HP/SP on a Base level gain, preserving gameplay.
Zero-EXP proof packages do not normalize/discard existing capped residual EXP.

Quest credit is not a Drop Table entry. The death context captures the current
quest and a transient Player quest generation. Multiple pending deaths can advance
the same active quest, but completion fires once. A newly accepted quest, including
the same authored ID, cannot inherit an older death's credit. Quest changes do not
delete that death's item/gold/EXP rewards. No full Quest foundation is implemented.

Production `kill()` has one reward route: prepare/commit, followed only on success
by the original audio/spark/toast/UI/save calls. The old material/gold/EXP/quest
grants were removed from that function, preventing old-plus-new double awards.
Dungeon **encounter-clear** rewards and exploration/crafting/merchant rewards
remain their existing separate event authorities.

## Respawn, travel, player death and persistence

The existing field replenisher creates a new actor object/registration. It still
uses the existing alive-count/12-second timer/placement rules. A future lifecycle
that reuses an actor object sets its authoritative new positive HP, then calls
`newLife(actor)` before the next death; old claims become stale and generation
increments. Loot does not schedule this transition or own AI/leash/aggro.

`spawn()`/`spawnWave()` retire the previous population before registering new
actors. Town/field/dungeon transitions and player respawn therefore cannot replay
old pending actors. Player death changes no item ownership or serial; existing
respawn gold loss remains 8 and does not refund loot. Committed claims stay consumed.

Save version remains **5**: no persistent schema was added. Canonical stacks,
instances, allocator and existing gold/progression/quest fields persist through
the current save authority. Claims, actor HP, life IDs and reward event history do
not persist. Reload recreates a fresh enemy population and controller; it does
not deserialize or replay a dead actor/claim or grant reward on load.

Enemy combat state and dungeon runs already are not saved. Reload may reset a
living encounter, and subsequent **new gameplay kills** may reward again. This
existing prototype population-reset limitation is explicit; there is no persisted
drop reroll for the same dead actor because no unresolved ground loot/claim is
loadable. Durable encounter identities/pending pickup persistence require a later
lifecycle/save contract. Current production table rolls are guaranteed kill-cycle
conditions, so there is no randomized pending gear roll to reload for free.

## Extension boundaries and provisional proof content

The [Monster Box foundation](CORE_SPINE_MONSTER_BOX.md) now adds an ordinary
canonical stackable ItemDefinition and separate opening/content-table authority.
This Loot owner's table/RNG/death claim contract does not change. The isolated
`proof-monster-box` table grants `monster-box-proof` x1 (guaranteed, NON-FINAL);
it never opens the Box or rolls its contents. Existing production tables and
reward values remain unchanged. There is no automatic production Box drop.

Drop generation, entitlement, ownership commit and presentation are separate.
Patch 0.0.1 retains **direct-to-inventory on death**. Future ground entities/pickup,
party ownership, weighted groups, capacity rejection and server authority must use
the explicit boundaries; this patch introduces none of their policy/UI.

Proof fixtures only: Herb quantity 2 / gold 7; Potion quantity 2; one Astral Blade;
empty table; independent multi table with Herb chance .5 quantity 1–3, Potion .5,
Astral Blade .25, gold 7. These numbers are **NON-FINAL**, authored/configurable,
and reachable only through isolated tooling or exact `dev=1` live fixture APIs.
They introduce no new ItemDefinitions, production gear progression or economy.

## Developer tooling and verification

`/tools/monster-loot.html` is an in-memory disposable sandbox. It reads/writes no
playable save key and exposes definition/validation, fixed RNG, candidate/claim,
commit/duplicate, new life, stack ownership, serial/instance and gold evidence.
`/?qa=1&dev=1` exposes the bounded live loot inspector/fixture APIs; normal URLs
expose no intended developer mutation API. QA records immutable reward events and
per-actor identity for robust state-based acceptance waits.

Run the full Node suite, focused `tests/monster_loot_browser.py`, previous browser
suites and cache/world validators as listed in README. Keep existing assertions.
See [verified handoff](CORE_SPINE_MONSTER_LOOT_REPORT.md) for commands, results,
smoke evidence and recorded targeting observations. No art acceptance is claimed.

## Monster Lifecycle integration extension

The [Lifecycle foundation](CORE_SPINE_MONSTER_LIFECYCLE.md) now owns explicit AI
state, target/attack intents, home leash/return and per-life respawn. It consumes
registration → authoritative HP-zero death → cached claim → commit, then calls
this owner's `newLife` at deterministic respawn readiness. It does not change
tables, RNG, claims, inventory internals or reward formulas. Loading/player death
invalidate offensive leases; travel retires both owners. Committed rewards persist
through unchanged version 5; AI/death linkage stays transient. Current cache is 93.
See [lifecycle verification](CORE_SPINE_MONSTER_LIFECYCLE_REPORT.md).

The Box extension reuses only Item State's small item reward planner; it does not
reuse Loot claims, life generations, currency/EXP/quest orchestration or tables.
See [verified Box handoff](CORE_SPINE_MONSTER_BOX_REPORT.md).
## Inventory Capacity integration

The [capacity foundation](CORE_SPINE_INVENTORY_CAPACITY.md) preflights the exact
resolved package before canonical publication and existing currency/progression/
quest adapters. Capacity rejection is atomic: no partial items, serial, gold,
Base/Job EXP or quest credit, and no reroll or fitting subset. The same live
entitlement can retry its unchanged package after space is freed. Existing
respawn/retirement/travel/reload can expire uncommitted transient claims; no
durable overflow, pending-loot UI or mailbox is added. Lifecycle owns no capacity
arithmetic. A blocked runtime death still receives its presentation timestamp.
Recommended next Backbone task: **Equipment Slot Closure foundation**.
