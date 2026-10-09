# Shop / Storage / Town Services - verified handoff

**TOWN SERVICE FOUNDATION: PASS. SHOP FOUNDATION: PASS. STORAGE FOUNDATION: PASS.**
Only this foundation is closed. Patch 0.0.1 / Core Spine are not complete.
Next: **DEV-TOOL GAP CLOSURE**; do not start it in this branch.

## Git identity / resume

| Field | Value |
| --- | --- |
| Repository | `basicbasja-cloud/Astraeon-online` |
| Branch | `backbone/shop-storage-town-services-0.0.1` |
| Starting parent branch | `backbone/quest-foundation-0.0.1` |
| Exact fetched starting parent HEAD | `fea51986a0dd1b5f9d94710b0d48261deab5f175` |
| Clean runtime/test checkpoint | `b08421cd3e186b1987aa13e6721aa51639b436d1` |
| Verified documentation checkpoint | `72a1631cbfa81cefffe83112b181f3411ddef2a6` |
| Final documentation successor / remote HEAD | Current target branch HEAD; resolve using commands below and final push receipt |

Parent was fetched, switched and pulled ff-only, and was clean before creating
this branch. No pasted older checkpoint was used as a reset. No merge, rebase,
force push, PR, main/World/Character branch modification was performed.
The runtime/test checkpoint has all passing results below and a clean tree.
Later commits update documentation only. A commit cannot embed its own hash;
the final push receipt records exact local and remote hashes externally.

```powershell
git switch backbone/shop-storage-town-services-0.0.1
git rev-parse HEAD
git ls-remote origin refs/heads/backbone/shop-storage-town-services-0.0.1
git status --short
git log --oneline -20
```

Resume from latest remote target, not from parent or runtime checkpoint.
Implementation and acceptance are complete; no remaining implementation failures.
Local evidence: `D:\Astraeon\backbone-verification\town-services`.
`final-verification-summary.json` aggregates successful final reports, not failed
attempts; `source-audit.json` records retained source/assertion evidence.

## Actual source audit / architecture

The source audit read existing runtime authorities and current contracts before
implementation: Item Inventory / Item State, Equipment, Capacity, Character,
Progression / Stats, Combat, Action Loadout / Action Item, Loot, Lifecycle, Box,
Quest evidence/runtime, Save/migration, merchant/crafting, NPC interaction,
travel/death, developer tools and boot/cache. This was not documentation-only
architecture. No Storage authority existed; Housing only rented/rested/upgraded.

| Responsibility | Authority / integration |
| --- | --- |
| Immutable service registry, Shop offers, Storage policy | New `town-service-definitions.js` |
| Semantic NPC interaction | Existing privately owned `QuestEvidence.interactions` |
| Current service session, owned tickets, transaction plans | New `town-service-runtime.js` |
| Canonical carried stacks/instances, one allocator | Existing Item Inventory / Item State |
| Separate stored ownership and inert history | New `storage-state.js`, private service runtime |
| Carried capacity / weight / net candidate | Existing Inventory Capacity |
| Gold | Existing Player `gold`, contained private publication |
| Equipment / Stats / Combat | Existing owned references and downstream authorities |
| Collect | Existing Quest derives carried ownership only |
| Save | Existing Save v5; optional Storage normalization adapter |

No ShopGold, second carried Bag, Quest Inventory, equipment object type, reward
RNG, Combat formula or EXP authority is introduced. Crafting/recipes remain
unchanged and continue through canonical Item State.

## Definitions, service access and bindings

Complete registry validation freezes authored definitions and rejects duplicate
IDs/target bindings, invalid type/target/Shop/item references, malformed metadata,
cycles, non-finite numbers and prototype keys. Live target validation uses actual
NPC IDs, not DOM names, sprite filenames or display text.

Merchant: `town-merchant` -> existing `merchant`.
Storage: `storage-proof` -> existing `housing-keeper`, explicitly **NON-FINAL
engineering proof only**, not authored Housing Storage, room ownership or lore.
No new NPC, map placement, art or navigation behavior is added.

A fresh same-runtime semantic capability opens the matching session once.
Copies/forgeries/wrong targets do not. Access rechecks town, alive player, finite
coordinates, existing 2.5-unit NPC range, current interaction, loading/travel and
session epoch. Closing/switching window, death/respawn, travel and reconstruction
invalidate access. No remote menu, QA inspection or past visit grants authority.
No wall-clock TTL or extra event listeners are added.

## Shop authority / atomicity

- Stack buy: original authored prices, exact quantity, canonical merge/maxStack
  and complete carried Capacity preflight before permanent gold charge.
- Unique buy: existing allocator creates N distinct canonical ItemInstances,
  serial advances N once, and nothing auto-equips.
- Stack sell: exact carried debit and safe contained gold credit. Capacity-
  reducing/no-worse sale remains possible for over-limit ownership.
- Unique sell: exact carried `instanceId`, never definition-only selection.
  Equipped sale rejects `ITEM_EQUIPPED`; explicit unequip is required.
- Quantity is a positive safe integer, technically bounded at 100000/request.
  Existing canonical non-stack package budget still applies. Prices/gold/product/
  resulting gold are safe nonnegative integers; overflow and invalid currency
  reject unchanged, without silent repair.

Preparation is immutable and non-mutating. WeakMap-owned single-use tickets bind
request, player/runtime, current session/epoch, carried pointer/revision, Storage
pointer/revision and gold. Commit revalidates context, stale state and capacity.
Copied/foreign/forged/duplicate tickets cannot mint items or gold. Success is one
carried revision; failure leaves ownership, gold, serial, equipment and Stats
unchanged. Existing mutation lock is held before injected capacity callbacks;
reentrant attempts reject `TRANSACTION_IN_PROGRESS`.

Original Potion 15, Ration 8, Herb 5 buy / 2 sell and Ore 7 buy / 3 sell are
retained. Potion/Ration sale stays unsupported. One existing `astral-blade` offer
uses **20 buy / 4 sell as NON-FINAL proof values**. No final catalogue, economy,
stock, restock, buyback, fees or equipment content was designed.

## Storage ownership, identity and capacity

Storage is durable separate ownership: schema 1 `stacks`, `instances`, `history`.
It is not extra carried capacity, auto-overflow, Equipment or Quest Inventory.
One positive canonical definition stack takes one logical slot; each unique
instance takes one. Policy is **100 provisional logical slots**, unweighted;
carried Capacity/Weight is never reused as a Storage weight rule.
Over-slot returning ownership is preserved; no-worse/reducing transactions remain
possible. maxStack remains a separate canonical constraint.

Stack transfer validates both complete source/destination candidates and exact
quantity before publication. Unique transfer moves the **same instanceId,
definitionId and nested metadata**, with no allocation, clone, replacement or
serial change. Carried and stored instance IDs are disjoint. Equipped deposit
rejects `ITEM_EQUIPPED`; explicit unequip is required. Withdrawal never auto-equips.

One narrow private Item State publisher commits final carried ownership with
contained Storage publication. Each successful transfer advances carried and
Storage revision once. Failed access, underflow, maxStack, Storage slot limit,
carried capacity or stale ticket changes neither container/revision, gold,
serial, Equipment, Stats or Quest. Withdrawal uses existing carried net Capacity
preflight; failed withdrawal does not debit Storage or partially grant items.
No ground/mailbox/overflow/discard policy is invented.

Stored gear cannot equip/apply Stats/Combat modifiers. Stored Potion/Ration cannot
execute carried Action Item effects. Buying/withdrawing normal gear uses existing
Equipment -> Stats -> Combat; exact unequip/deposit leaves no stored modifiers.

## Quest, death, travel and other foundations

Collect derives **carried canonical ownership only**. Depositing one of three
required Herbs changes 3/3 READY to 2/3 ACTIVE; withdrawing restores readiness.
There is no stored Collect ledger. Transfers mutate carried revision and stale
prepared Quest turn-in; failure cannot consume sources or grant rewards. Service
operations grant no Kill/EXP/quest completion. Real NPC interaction may separately
produce legitimate Talk evidence through the shared interaction authority.

Death/respawn and town/field travel retain both durable containers and exact gear
identity, serial and Quest progress. Transient sessions/tickets expire. Existing
travel/death gold costs remain existing gameplay. Lifecycle, Loot, Box, Action
Item, Loadout, Equipment, Capacity, Progression and Combat retain their contracts.
Full inherited browser suites exercise real Basic Attack, learned Skill kills,
respawn/new-life reward, Box, crafting/merchant and equipment integration.

## Save decision / migration / serial safety

Save **version 5 is retained deliberately**: `storageState` is additive optional
data; no existing persistent field is reinterpreted and Save core is unchanged.
Old saves get empty Storage, no fabricated progress/items/gold/rewards. Session,
capabilities, tickets, revisions and pending operations do not serialize.

The single carried `nextItemSerial` allocator reserves highest observed stored
IDs **before legacy equipped-only import or new canonical creation**. Reservation
includes malformed and quarantined instances and restored unsupported-schema
history. Storage moves neither advance nor rewind serial. Grant, crafting, Loot,
Box and Shop allocation after reload cannot reuse a stored ID. Exhaustion rejects.

Unknown/malformed entries are inert normalization history, not grants or effects.
Non-JSON metadata is quarantined safely. Unsupported Storage schema is archived;
cross-container duplicates keep carried ownership and archive stored conflicts.
Unambiguous valid ownership/metadata survives; no replacement gear is minted.
Future save-version rejection remains the existing authoritative first guard.
Twenty normalization/save/load cycles preserve containers, serial and Collect.

## Developer tooling / functional presentation

Existing Merchant and Housing panels receive minimal stack/exact-instance actions.
No UI layout/style redesign or visual acceptance is claimed. Exact `?dev=1`
`AstraeonTownServicesDev` calls the same guarded high-level APIs; no service-opening
capability or capacity/gold bypass is exposed. Normal URL exposes no service
mutation/harness globals. QA adds read-only service/container evidence.

`/tools/town-services.html` uses disposable isolated actors, the same semantic
capabilities and canonical grants, with separate key `astraeon-town-services-dev-v1`.
Registry validation, plans, receipts, duplicate/stale rejection, both containers,
revisions, exact IDs, capacity, Collect and save/load are inspectable. Production
save is not touched. Historic isolated Item State trade fixtures lacking these
modules retain their physical primitive; they cannot open a live service session.

## Deterministic verification

**1474 inherited + 140 new = 1614 pass / 0 fail**, 23 suites.
Full `python tools/run-node-checks.py` ran at `node-final` and `node-pre-push`.
All 22 inherited Node files are identical to parent after line-ending normalization;
no old assertion was deleted/weakened. New `tests/town-services.test.cjs` covers
registry/metadata/price safety, semantic access, session expiry, owned/stale/
foreign/duplicate tickets, stack and unique Shop, overflow/serial/capacity,
atomic exact Storage transfer, equipped rejection, stored effect isolation,
carried-only Collect/stale turn-in, version guards, legacy/global serial,
quarantine/idempotent persistence and callback/reentrancy failures.

## Browser acceptance / smoke

| Successful final suite | Groups |
| --- | ---: |
| Inventory Capacity | 63 |
| Monster Box | 33 |
| Monster Lifecycle | 30 |
| Monster Loot | 26 |
| Action Item | 30 |
| Inventory | 15 |
| Equipment Slots | 59 |
| Action Loadout | 17 |
| Combat | 21 |
| Skill Tree | 11 |
| Progression | 7 |
| Quest (`regression-quests-rerun2`) | 57 |
| **Inherited retained** | **369** |
| **New Town Services (`browser-two-class-1`)** | **40** |
| **Total** | **409 / 0 failures** |

New suite includes 19 groups each for disposable Swordsman and Mage, plus isolated
harness and normal URL. Actual ordinary movement/NPC interactions and existing
Merchant/Storage/Bag controls prove stack buy/sell, canonical unique purchase and
exact sale, equipped rejection, no-gold-loss capacity failure, Collect readiness,
stale Quest ticket, same-ID/metadata/serial transfer, failed withdrawal atomicity,
Action Item isolation, actual save/offline reload, field travel and real enemy-
caused death/town respawn. No teleport, enemy-HP edit, AI/collision disable or
fabricated Kill/Quest completion is used. Canonical player-resource fixture is
isolated to Action Item / actual enemy death tests.

Merchant acceptance: PASS. Storage acceptance: PASS. Quest/Storage acceptance:
PASS. Local two-class smoke is covered by these actual runtime flows and full
inherited suites, not a separate unrecorded manual visual claim.
**Zero unexpected console, page, runtime or HTTP errors** in successful reports.
Sixteen expected structured service rejections are separately recorded.

## Fixture adaptations / retained failure evidence

- `action_item_browser.py`, `inventory_browser.py`, `equipment_slots_browser.py`,
  `monster_box_browser.py`, `inventory_capacity_browser.py`: prior remote-menu
  Merchant setup now ordinarily walks/interacts with actual Merchant via shared
  `town_service_navigation.py`. Capacity fixture reinteracts after policy change
  invalidates sessions. All old behavioral assertions remain unchanged.
- `quests_browser.py`: cache assertion checks active generation, retaining four-
  module precache and offline durability. The player-death fixture waits for
  authoritative chase arrival, then if needed walks 0.2 units toward actual actor
  using keyboard. Original HP-zero, Incoming Combat killed, Quest preservation
  and town-respawn assertions remain unchanged.

Earlier new-suite attempts remain `browser-attempt-1` (copied Guild-target helper
check after valid Merchant arrival) and `browser-attempt-2` (normal create click
30-second session timeout after 18 passing groups). Correct target-kind check and
consistent bounded 180-second context timeout affect fixture only.

First inherited Quest run (`regression-quests`) passed 13 groups, then stationary
CHASE reached 1.4000000000000008 against range 1.4 (Boar 4.800000000000001 vs 4.8),
HP 1, no incoming Combat. First contact-step rerun passed 40 groups, then Mage
reached 1.4000000000000012; the step had happened before chase arrived. Final
bounded arrival + ordinary contact step passes both classes and all 57 groups.
The inherited stationary contact rounding signal remains a documented production
limitation, not a gameplay fix. AI/Combat/navigation are unchanged. Raw failures
are retained, excluded from final passing counts and not hidden.

## Cache/offline, world and final source checks

One deliberate cache generation **v95 -> v96**, matching boot/page/SW and three
new modules. All are initialized before game consumers. Historical compatibility
URLs remain cached. `tests/cache_resume.py`: PASS, **164 precached requests**,
legacy cache removal, offline town, saved character, migration and blocked-save
recovery retained, errors empty. New two-class suite additionally proves offline
Storage ownership and no transient access/replay.

`python tools/validate-world-v3.py`: exit 0, PASS Terrain, Navigation, TownObject,
AnimationManifest. An earlier concurrent attempt was intentionally stopped for
resource ordering, without schema verdict; final run was serial after browsers.
`git diff --check`: PASS. Source audit: **38 protected core files unchanged**,
22 inherited Node files retained, inherited browser assertion ASTs retained apart
from documented active-cache expression. No protected visual/world paths changed.

## Files added

- `town-service-definitions.js`, `storage-state.js`, `town-service-runtime.js`
- `tests/town-services.test.cjs`, `tests/town_service_navigation.py`,
  `tests/town_services_browser.py`
- `tools/town-services.html`, `tools/town-services-harness.js`
- `docs/CORE_SPINE_TOWN_SERVICES.md`, `docs/CORE_SPINE_TOWN_SERVICES_REPORT.md`

## Files modified

- `item-state.js`, `player-state.js`, `game.js`, `boot.js`, `index.html`, `sw.js`
- `README.md`, `ARCHITECTURE.md`
- Current contracts `CORE_SPINE_ITEMS.md`, `CORE_SPINE_QUESTS.md`,
  `CORE_SPINE_INVENTORY_CAPACITY.md`, `CORE_SPINE_EQUIPMENT_SLOTS.md`
- Six inherited browser fixtures listed above. No inherited Node test changed.

## Known limitations / integration conflicts / untouched systems

This is local private authorization with contained synchronous trusted publishers,
not server security or general rollback across arbitrary external callbacks.
Malformed/fractional gold can remain in a returning save, but services reject it
as `INVALID_CURRENCY`; no silent migration repair occurs. Quarantine recovery
requires deliberate future migration. Storage proof binding, 100 slots and unique
price are explicitly non-final. Existing zero/unconfigured item weights remain
unchanged. No final capacity, economy, fees, overflow or Housing Storage design.

Likely integration conflicts: focused Game/Player/Item State adapters, boot/index/
SW/current docs. Protected Progression/Stats, Combat, Skill, Action Loadout/Item,
ItemInventory/Equipment, Loot/Lifecycle/Box/Capacity, Save core, definitions,
recipes, exploration/navigation and Character renderer remain unchanged.
No authoring, RO3 references, assets/world, Blender, renderer/lighting, collision,
camera, sprites/atlases, animation, style or visual-review evidence changed.
Historical verification reports were not rewritten.

No account/guild stash, mail/ground overflow, auto-sell, player trading, auction,
premium systems, repair, stock/restock/buyback, final content/UI/visual work or
server authority was implemented. Do not interpret functional verification as
visual/art/performance acceptance. Next recommended task: **DEV-TOOL GAP CLOSURE**.

## Final documentation successor / publication gate

Verified documentation checkpoint: `72a1631cbfa81cefffe83112b181f3411ddef2a6`.
This final successor records publication readiness without runtime changes.
All final verification results above apply to clean runtime checkpoint
`b08421cd3e186b1987aa13e6721aa51639b436d1`; subsequent diff is documentation only.
Source audit and full parent-to-HEAD diff check pass. Push only
`backbone/shop-storage-town-services-0.0.1` normally, confirm local/remote exact
HEAD equality and empty `git status --short`, and stop. Final external push
receipt and response contain this successor's exact SHA. No next task starts here.
