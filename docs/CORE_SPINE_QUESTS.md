# Talk / Kill / Collect Quest foundation

Working contract; full browser acceptance is pending. Patch 0.0.1 reusable gameplay contracts. The five proof quests are engineering
fixtures, not approved story, quest balance, dialogue or final UI. This milestone
does not complete Patch 0.0.1 or Core Spine.

## Authorities and modules

| Responsibility | Authority |
| --- | --- |
| Immutable authored quest registry and full validation | `quest-definitions.js` |
| Durable state normalization and derived objective/status view | `quest-state.js` |
| Semantic NPC interaction and validated Lifecycle event bridge | `quest-evidence.js` |
| Acceptance, evidence observation, prerequisites and opaque turn-in tickets | `quest-runtime.js` |
| Net canonical item transaction and capacity preflight | existing Item State / Inventory / Capacity |
| Base EXP / Job EXP | existing Character / Progression prepared reward authority |
| Gold | existing writable player gold authority |
| Save and future-version guard | existing Save authority |
| Input, semantic interaction, death delivery, functional buttons | narrow `game.js` adapters |

Quest does not own Combat, Monster HP/death/respawn, Loot, Box RNG, item ownership,
equipment, Stats, currency formulas or save storage. No Quest Inventory, separate
gold/EXP ledger or monster counter is introduced. Historical automatic Contract
Board counters in `state.quest` remain compatible and separate; new explicit
quests use `state.questState`.

## Definitions and validation

Each definition has a stable primitive `id`, one to 32 objectives with stable
unique `id`, `prerequisites` containing completed quest IDs, a known
`turnInTargetId`, deterministic `rewards`, `repeatable:false`, and JSON metadata.
The registry validates the complete set before publication and freezes clones.
It rejects duplicate quest/objective IDs, unknown objective types/references,
missing prerequisites, self-dependencies and cycles.

Required counts are positive safe integers at most 100000. Authored Base EXP,
Job EXP and gold grants are nonnegative safe integers. Item rewards reference
existing definitions with valid integer quantities and bounded package size;
aggregate stack rewards must respect maxStack. NaN, Infinity, cyclic/non-JSON
metadata, unsafe identities/numbers and malformed data reject structurally,
without player mutation. Definition IDs are authority; display labels are not.

## State and acceptance

The read model exposes `LOCKED`, `AVAILABLE`, `ACTIVE`, `READY_TO_TURN_IN`,
`COMPLETED`. Completed prerequisites derive LOCKED → AVAILABLE. Explicit
acceptance creates one ACTIVE durable entry; talking does not accept quests.
Double acceptance rejects without resetting anything. Completion cannot restart.
No abandonment, repetition, timers, failure or backward durable status edit API
exists. Objectives are unordered; multiple active quests are supported.

Durable accepted/completed entries contain only their status and capped Talk/Kill
counts keyed by objective ID. Availability, Collect counts and readiness are
derived. ACTIVE → READY occurs when all current objectives pass. READY → ACTIVE
is an intentional view change when Collect ownership falls below requirements.
Successful turn-in publishes COMPLETED only once.

## Talk evidence

The existing authored service IDs form the proof interaction registry. An actual
NPC interaction validates target identity, finite actor position/HP, alive actor,
town context, existing 2.5 interaction range and absence of loading/travel. It
issues a frozen private `NPC_INTERACTED` capability with an inspection identity.
Quest observes this semantic event before the existing service window opens.
Proximity, rendering, menu opening, Bag, map loading and querying progress issue
no evidence. Quest does not implement dialogue.

Matching active Talk objectives increment capped counts. One event may progress
independent quests; the same capability cannot be replayed. Copies, forged JSON
and another owner's evidence reject. Evidence before acceptance is not banked.
Turn-in requires a current owned interaction with the definition's turn-in
target; leaving the range/context invalidates that interaction for turn-in.

## Kill evidence and identity

`QuestEvidence.deaths(lifecycle, observer)` is a narrow consumer of the existing
Lifecycle output. It requires the exact immutable death event object issued by
that Lifecycle owner, present in its bounded event history, and matching the
actor's authoritative active instance/life/death identity. It obtains the
stable mechanical `definitionId` from that same owner's inspection.

The bridge does not detect HP zero, inspect sprites, infer death from Loot or
replace Lifecycle identity. Existing game `kill()` and update death-output paths
deliver immediately; the bridge and Quest each reject repeated evidence. There
are no event listeners to accumulate through travel or respawn.

Same runtime / same life / same death counts at most once per matching active
objective. Respawned new life produces a new legitimate capability. Multiple
quests may each increment once. Counts cap at authored requirements. Only the
current single-player, player-owned combat/death orchestration is integrated;
party/assist/server attribution is future scope. Loot resolution/commit alone,
Box opening, Action Item and Quest rewards do not create Kill credit.

Kill observation is independent of Loot acceptance: a genuine death may count
even when existing Loot item capacity rejects its reward package. The inherited
Loot reward/EXP/gold/legacy Contract behavior is unchanged. Quest turn-in rewards
are separate deterministic authored grants, never a replay of death rewards.

## Collect: current canonical ownership

Collect reads existing Inventory stacks or owned ItemInstances, including
equipped ownership. It displays `min(owned, required)`. Existing items, Loot,
Box, merchant, crafting and ordinary canonical grants all count regardless of
source. There is no acquisition event requirement or Collect item ledger.

Ownership reaching the threshold does not latch completion, reserve items or
consume anything. Spending/selling items before turn-in makes the quest
incomplete again. Save/reload re-derives from restored ownership.

Each objective explicitly authors `consumeOnTurnIn`. Multiple consuming
objectives for the same item share an ownership pool in stable authored order;
requirements 3 and 2 need five items, not three. Non-consuming objectives read
ownership independently. The complete consuming plan aggregates item quantities.
Non-stack consumption selects existing unequipped matching instances in stable
canonical order; if only equipped instances satisfy the requirement, turn-in
rejects `ITEM_EQUIPPED` and preserves ownership/modifiers. No automatic unequip.

## Turn-in and exactly-once rewards

1. Validate alive actor, context, READY status and current semantic turn-in target.
2. Re-evaluate all objectives and aggregate complete Collect debits.
3. Build exact deterministic rewards; no Quest RNG exists.
4. Preflight the full net Item/Capacity transaction and existing Character
   Progression/currency publication. No source debit or serial allocation yet.
5. Issue an immutable ticket privately owned by this Quest runtime.
6. Commit revalidates owner, durable state/revision, transient epoch, Inventory
   object/revision, Progression/gold identity, objectives, target and exact plan.
7. Existing Item State constructs a local debit/reward candidate and allocates
   equipment through the existing canonical serial authority. All deterministic
   validation/capacity/serial/resource planning happens before publication.
8. Contained synchronous publication commits prepared Character rewards, gold
   and COMPLETED state, then canonical Item State ownership. Receipt reports
   consumption, rewards, stack/instance results, serial and capacity evidence.

Tickets live in a private WeakMap, not ordinary authorizing JSON. Copied,
foreign/forged, stale, duplicate and sibling tickets cannot mint rewards.
Preparation is non-mutating. Any relevant inventory/equipment/progression/gold
change invalidates the prepared identity. Context/transition/death invalidation
advances a transient epoch. Currency accepts inherited finite fractional
balances, but authored grants are whole safe amounts and overflow is rejected.

Stack rewards merge canonical stacks without allocating ItemInstance serials.
Equipment rewards create ordinary unique owned instances, advance serial exactly
per unit and do not auto-equip. Rewarded gear follows Equipment → Stats → Combat.
No Skill Point/rank/Action Slot/Action Item cooldown mutation is added.

### Atomicity and trust boundary

Supported packages publish as one canonical net transaction; failure leaves
Collect sources, EXP, gold, rewards, serial and durable Quest completion intact.
No asynchronous yield, external presentation callback or RNG exists between
validated reward publication and completion. The internal completion publisher
is private and non-throwing. This follows the existing trusted synchronous
Item/Character reward publisher contract; it is not a universal database
rollback engine for hostile/custom side-effect callbacks or server security.

## Capacity and integration boundaries

Existing `canAcceptItemPackage` evaluates final ownership after Collect debits
plus rewards. Last-stack removal may free slots/weight. Partial debits retain
the source slot. Existing maxStack, serial feasibility, weight precision and
no-worse over-limit rules remain authoritative.

Capacity failure preserves READY, consumes no required items and grants no
partial reward. Freeing ownership permits a deterministic retry. There is no
overflow/mailbox/ground-drop policy. Quest uses exact authored packages; Box
maximum pre-roll envelope/anti-reroll behavior is unchanged. Lifecycle remains
unaware of Quest inventory arithmetic. Merchant/crafting remain ordinary sources
of Collect ownership. Equipment/Capacity keep one canonical ownership authority.

## Persistence, migration and runtime lifetime

Save version **5** deliberately remains: the existing extensible player state
preserves the optional new `questState` field without reinterpreting any old
field. Existing Save core and future-version guard are unchanged. On Player
attachment, definitions reconnect by stable IDs and normalize durable entries.
Old saves without the field start with no accepted/completed/fabricated progress
or migration reward. Unknown/invalid stored entries are archived as inert JSON
history, never activated or used as prerequisite completion; ownership is not
changed. Unsupported progress keys, including stored Collect counts, are ignored.

Talk and Kill counts persist. Completed identity persists and unlocks chains.
READY is never trusted as a durable flag. Tickets, event capabilities, actor/NPC
references, event history and subscriptions are not serialized. Reload creates
a new owner, rejects old tickets/evidence and does not replay historical deaths
or rewards. The observer uses bounded diagnostics plus weak object identity,
not an ever-growing serialized monster-death history.

Player death/respawn and town/field travel preserve durable Quest state and
ordinary ownership under their existing policies. They invalidate prepared
transient transactions through existing runtime boundaries. Travel does not
count as Talk/Kill or repeat event wiring. New monster lives remain legitimate.

## Proof content and developer tooling

All proof coefficients are data-driven, replaceable and NON-FINAL:

| Quest ID suffix | Objectives | Reward proof |
| --- | --- | --- |
| talk | Guild Registrar interaction ×1 | Base 3, Job 2, gold 4, Potion ×1 |
| kill | existing Leafmane Fox definition ×2 | Base 5, Job 3, gold 6, Herb ×1 |
| collect | ordinary Herb ×3, consumed | gold 3, Potion ×1 |
| mixed | registrar ×1, Fox ×1, Ore ×2 consumed | Base 4, Job 2, gold 5, existing Off Hand proof ×1 |
| chain | registrar ×1; requires talk completed | gold 1, Ration ×1 |

Every proof turns in at the existing `guild-registrar` service ID. No NPC/monster,
gear definition, map placement or final content catalogue is added.

Existing journal/guild panels expose plain functional Accept/status/Turn In
buttons using existing layout classes. No final Quest UI, tracker, dialogue,
marker/VFX or art claim. `/tools/quest.html` uses isolated
`astraeon-quest-dev-v1` storage for definition/plan/state/save inspection, canonical
grant/consume, real resolver HP → Lifecycle evidence, new-life tests, capacity
profiles, private prepare/commit/duplicate and recreation rejection. The sandbox
never edits Quest progress directly. Only exact `?dev=1` exposes the game's
limited `AstraeonQuestDev` diagnostics/actions; normal URLs expose no unrestricted
Quest mutation API. Boot/cache generation 95 includes all four runtime modules.

## Known limitations and future boundaries

Unordered non-repeatable quests only; no stage scripting, failure, timers,
abandonment, daily scheduling, party credit, branching dialogue, story flags,
random reward, quest-bound items or separate Quest Inventory. NPC interaction
registry currently covers existing town services only. Local opaque authority
cannot secure a client controlled by its owner. Authored definition evolution
requires deliberate stable objective-ID migration policy. Archived unknown quest
history is inert, not support for arbitrary future save semantics.

Quest UI/art, content and balance are separate work. Shop/Storage/Town Services,
dev-tool gap closure and the 0.0.1 integration gate remain outstanding.
