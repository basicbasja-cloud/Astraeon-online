# Shop / Storage / Town Services foundation

Only this Patch 0.0.1 system foundation is in scope. **Patch 0.0.1 and Core Spine
are not complete.** Offers, service bindings and Storage slots are engineering
data, not final economy, lore, content, UI or balance.

## Authority

| Concern | Authority |
| --- | --- |
| Service identities, type, targets; Shop offers; Storage policy | `town-service-definitions.js` |
| NPC semantic interaction | Existing `QuestEvidence.interactions`, shared by Quest and services |
| Session, owned preparation, revision/epoch integrity, complete plans | `town-service-runtime.js` |
| Canonical carried stacks, instance allocator, equipment refs, one publication | Existing Item Inventory / Item State |
| Durable stored stacks and moved exact instances; inert normalization history | `storage-state.js` and private service runtime |
| Carried slots/weight and no-worse rule | Existing Inventory Capacity |
| Currency | Existing Player state `gold`, contained private publication |
| Player resources, modifiers, Combat | Existing Character / Stats / Combat |
| Collect | Existing Quest, derived from carried ownership only |
| Persistence | Existing Save v5 and optional `storageState` normalization adapter |

Storage is a separate container, never additional carried capacity, Equipment,
Quest Inventory or implicit overflow. It has no EXP, reward RNG, kill/death
identity, cooldown or item-effect authority.

## Authored contracts and provisional data

Services have stable `id`, `type` (`MERCHANT` / `STORAGE`),
`interactionTargetId`, `enabled` and metadata. Complete registry validation
rejects duplicate IDs/target bindings, unknown type/target, unsafe JSON,
non-finite/cyclic/prototype-polluting data and conflicting Shop bindings before
publication. The live registry validates against actual imported NPC IDs.

`town-merchant` binds the existing `merchant`. No authored Storage provider was
found: existing housing implements room rent/rest/upgrade. `storage-proof`
therefore binds existing `housing-keeper` as explicitly **NON-FINAL engineering
proof**, with no NPC art, placement or lore change.

`merchant-proof` retains Potion 15, Ration 8, Herb 5/2 and Ore 7/3 buy/sell
prices. `null` explicitly means unavailable buy / unsellable. One existing
Astral Blade proof offer is 20 buy / 4 sell; these added prices are non-final.
No catalogue, recipe, stock, restock, dynamic price or buyback system is added.
The original ItemDefinition merchant data remains unchanged.

Storage uses configurable **100 logical slots**, no carried weight limit.
One positive definition stack counts once; each unique instance counts once.
maxStack remains canonical and separate. Returning over-slot Storage retains
all valid ownership; transactions may not worsen its exceeded slot count.
No final Storage expansion or capacity progression is implemented.

## Current interaction / session

Only a capability issued by the same existing semantic NPC authority can open
the matching service. The live adapter never exposes that capability in QA or
dev inspection. Session validity rechecks current interaction identity, canonical
player life, town, finite coordinates, NPC range (existing 2.5 units), loading
and transition context. A copied/forged/wrong-target capability is invalid.
An interaction can open a session once; reopening needs a new real interaction.

Closing/switching away from its service window, loading/travel, player death,
respawn and runtime reconstruction invalidate transient session/tickets. The
same current service window may perform successive transactions. There is no
wall-clock TTL: the ongoing local interaction and range/context define access.
An old visit never enables remote Shop/Storage use. No event listeners are added.

## Shop transactions

`buy(itemId,count)` supports canonical stack and non-stack definitions in the
authored offers. `sell(itemId,count)` sells carried stacks;
`sellItemInstance(instanceId)` sells one exact carried unique item. Definition-
only unique sale is invalid. Equipped sale returns `ITEM_EQUIPPED`; explicit
unequip is required. Unsold/previous items remain owned; buy never auto-equips.

Counts are positive safe whole integers, bounded at 100000 per request. Prices,
total price, current/resulting gold are safe nonnegative integers. Overflow,
underflow, unsupported offers, maxStack, serial or Capacity rejection occurs
before item/currency publication. Equipment allocation uses the existing
ItemInstance allocator once per accepted unit. Sale never changes serial.

Preparation validates and exposes an immutable deterministic plan without
charging gold or changing ownership/serial. Commit revalidates, then Item State
publishes the complete net debit/reward candidate once with contained gold
publication. There is one carried Inventory revision per successful transaction.
The live Player compatibility `buy`/`sell` wrappers route to this authority.
Historical standalone fixtures without service modules retain the physical
Item State trade contract; they cannot grant live service access.

## Storage move transaction

`depositStack` / `withdrawStack` move exact positive quantities and merge with
the destination's existing canonical definition stack. Source underflow or
destination maxStack failure changes neither container.

`depositItemInstance` / `withdrawItemInstance` move the existing immutable
instance, preserving instanceId, definitionId and nested metadata. They never
call instance creation, change serial, copy equipment state or auto-equip.
Carried and stored instance ID sets must remain disjoint. An equipped deposit
returns `ITEM_EQUIPPED`; a stored item cannot equip, affect Stats/Combat, or
execute a carried Action Item until withdrawn.

Plan both candidate containers first. Withdrawal preflights existing carried
Capacity against final ownership; deposit preflights Storage and carried
no-worse ownership. One Item State private `commitOwnershipTransfer` publishes
the carried candidate with contained Storage publication. Successful transfers
advance carried Inventory and Storage revisions once each. Failed transfers
change neither revision, ownership, gold, serial, Equipment, Stats or Quest.
There is no automatic ground/mail/overflow redirect or discarded partial grant.

## Authorization and trust boundary

Tickets are owned through private WeakMap identity, never forgeable JSON.
They bind the immutable cloned request, runtime epoch/session, carried identity
and revision, Storage identity and revision, and gold. Copies, foreign tickets,
runtime-recreated tickets, duplicates and changed ownership/currency/session
reject. Capacity policy is revalidated at commit, including late policy changes.
Preparation and publication hold existing mutation locks before injected policy
callbacks; reentrant actions reject `TRANSACTION_IN_PROGRESS`.

Production publishers are contained synchronous trusted adapters. This is local
client integrity, not server security or a general rollback database. Deliberate
arbitrary edits of client memory are outside its security boundary. Capacity
and JSON failure paths are prevalidated; normal supported packages commit all
or nothing. Shop/Storage do not invoke arbitrary reward callbacks or external I/O.

## Quest / equipment / other foundations

Collect counts current **carried** canonical ownership. Depositing one of three
required Herbs makes it 2/3 and ACTIVE; withdrawal restores READY. Stored items
do not satisfy Collect or turn-in consumption. Inventory revision changes make
prepared Quest/Box/Action Item inventory authorizations stale; no Quest counter
or listener is added. Transfers grant no Talk/Kill credit. Actual NPC interaction
can independently produce legitimate Talk evidence through the shared boundary.

Equipped gear remains carried exactly once; it must be explicitly unequipped
before sale/deposit. Buying and withdrawal create no equipped reference.
Progression, Action Loadout, Action Item, Loot, Lifecycle, Box, Capacity, crafting,
equipment slot definitions, damage formulas and visual composition retain their
authorities. Shop/Storage introduces no EXP, RNG or item-effect formula.

## Save / migration / serial safety

Save **version 5** remains deliberate: optional additive `storageState` does not
reinterpret existing equipment/inventory fields. Its schema 1 contains only
`stacks`, `instances`, inert `history`. No separate allocating serial exists.
The carried `nextItemSerial` remains the single allocator. Item State migration
reserves the highest observed stored ID, including malformed/quarantined IDs,
before canonical allocation or legacy equipped-only import. Storage moves never
rewind or advance it. Creation through Loot, Box, crafting, Shop and canonical
grant therefore cannot reuse an ID held in Storage.

Missing Storage means empty, without fabricated items/gold/progress/rewards.
Malformed/unknown stored entries remain inert normalized history. Non-JSON
metadata becomes a quarantine reason; it is not recursively frozen/granted.
Unsupported Storage schema is archived inertly rather than treated as valid
ownership. Cross-container conflicting IDs keep carried ownership and archive
the stored reference; no replacement instance is minted. All unambiguous valid
ownership is retained. Future save-version guard remains unchanged and
authoritative before migration. Serial exhaustion rejects allocation safely.

Save/reload persists both containers, remaining items, currency, exact gear IDs,
metadata and global serial. It serializes no sessions, tickets, subscriptions or
pending transaction. Reload never replays/refunds operations. Travel and player
death/respawn preserve Storage and ordinary durable ownership under their
existing policy; currency travel/death costs remain existing gameplay.

## Presentation / development / future work

Existing Merchant and Housing panels gain functional stack/exact-instance actions
only. Remote menu access may inspect data but cannot acquire service authority.
Normal URLs expose no service mutation globals. Exact `?dev=1` diagnostics use
the same current-session APIs and have no NPC, capacity or currency bypass.
`tools/town-services.html` uses isolated actors, real semantic capabilities and
public canonical fixture grants with key `astraeon-town-services-dev-v1`.
It exposes plans, receipts, duplicate rejection, both containers, revisions,
serial, Capacity, Collect and save/reload. No playable save is touched.

No final UI/art, equipment appearance, bank/account/guild stash, trade/auction,
mailbox/ground overflow, equipment binding, repair, economy redesign, service
fees or server/network authority. Future access restrictions, capacity profiles,
offers and authoritative transport may extend these contracts. The next task
is **DEV-TOOL GAP CLOSURE**, not automatic expansion in this branch.

See the [verified handoff report](CORE_SPINE_TOWN_SERVICES_REPORT.md).
