# Equipment Slot Closure foundation

Only the Patch 0.0.1 equipment slot foundation is implemented. Patch 0.0.1 and
Core Spine remain incomplete. Gear content, coefficients and visuals are not
approved by these system checks.

## Registry and compatibility

`equipment-slots.js` owns an immutable ordered registry. Definitions contain no
ownership or equipped instance. Display names are presentation, never authority.

| Stored canonical ID | Semantic ID / accepted API alias | Active label |
| --- | --- | --- |
| `weapon` | `mainHand` | Main Hand |
| `offHand` | `offHand` | Off Hand |
| `armor` | `body` | Body |
| `shoes` | `shoes` | Shoes |
| `relic` | `accessory` | Accessory |

The existing definitions, legacy name importer, crafting output and chapter
reward path establish these meanings: blades occupy `weapon`, Garb/Plate occupy
`armor`, and Charm/chapter sigils occupy `relic`. This prototype's single relic
slot behaves as an accessory; this does **not** implement the roadmap's future
Relic socket/advanced itemization system. Existing IDs are retained deliberately
to preserve version-5 storage and callers. Semantic aliases normalize to one
stored ID, never create additional active slots or duplicate references.

Head, Garment, Accessory 1/2 and cosmetic slots remain inactive. Future work can
extend the registry and authored compatibility without changing inventory
ownership. Future two-handed, pairing, multi-slot, unique-equipped or class rules
belong in the existing restriction boundary; none are activated here.

## Definition and ownership contracts

Existing `ItemDefinition.equipmentSlots` is the explicit allowed-slot list.
`AstraeonItemEquipment.validateDefinition` returns immutable `allowedSlots` in
stored IDs, or a structured failure. It requires a nonempty item ID, non-stack
equipment with `maxStack:1`, a nonempty
list of known active IDs/aliases without duplicates (including alias duplicates),
plain requirements and finite acyclic JSON data. Modifiers must be an array with
plain numeric `primary`/`add`/`multiply` maps when present;
the existing Stats calculator validates its own operation/stat grammar and
finite arithmetic. No derived formula is copied into Equipment.

Malformed definitions cannot equip or contribute modifiers. Non-equipment
cannot equip. Runtime publication also derives the actual combined modifiers
through Character before installing equipment, catching composition overflow
or custom Character configuration failures atomically.

Canonical ItemInventory owns each stable `item-N` instance exactly once.
Equipment stores only `slotId -> instanceId|null`. Equip, replacement and unequip
do not create/delete instances, change their definition/metadata or advance
`nextItemSerial`. Equipped instances stay in inventory.

## Authoritative APIs and transitions

```js
player.getEquipmentSlotRegistry(); // immutable ordered definitions
player.getEquipmentSlots();        // authoritative five-key references
player.getEquipped('mainHand');     // aliases supported
player.canEquip(instanceId, 'offHand');
const result = player.equip(instanceId, 'offHand');
player.unequip('offHand');
```

`getEquipment()` deliberately remains the deprecated, immutable three-key
`weapon/armor/relic` compatibility projection. It is recomputed from the same
private references and owns no state. New consumers use `getEquipmentSlots()`.
Legacy name mirrors/setters remain contained adapters for the original three
slots; new slots use instance-ID APIs. They never become a second gear ledger.

Eligibility requires a nonempty primitive string instance ID before property
lookup: boxed strings, objects/arrays with coercion, numbers and symbols reject
without executing conversion callbacks. It checks active slot, valid canonical inventory/references, owned
instance, validated equipment definition, allowed slot and the existing
`equipmentRequirements(requirements,instance,canonicalSlot)` hook. Production
requirements remain empty. No new level/class/combat restriction is invented.
The hook must return exactly true; false/throw rejects. Live validation locks
nested inventory/equipment transactions so a hook cannot publish a second
mutation during the check. Providers remain trusted synchronous local code.

Successful equip installs one new reference map after full validation and one
Character modifier publication. An occupied slot returns `previousInstanceId`;
its occupant remains owned and becomes unequipped. There is no intermediate
unequip publication. Results include canonical/semantic slot, new/previous
instance, `changed`, immutable equipment, inventory and capacity evidence.

Unequip clears one reference and removes only that contribution. Empty-slot
unequip succeeds with `changed:false`; the retained Item State transaction
revision policy still advances on accepted publication. Re-equipping the same
instance in its current slot succeeds without modifier accumulation. A reference
already in another compatible slot rejects `ALREADY_EQUIPPED`. Moving requires
explicit unequip then equip; no automatic multi-slot move is implemented.

Useful codes: `INVALID_EQUIPMENT_SLOT`, `INVALID_EQUIPMENT`, `UNKNOWN_INSTANCE`,
`NOT_EQUIPMENT`, `INVALID_EQUIPMENT_DEFINITION`, `WRONG_EQUIPMENT_SLOT`,
`ALREADY_EQUIPPED`, `EQUIPMENT_REQUIREMENTS`, `INVALID_EQUIPMENT_MODIFIERS`,
`TRANSACTION_IN_PROGRESS`. Rejection preserves ownership, serial, Stats, capacity
and transaction revision.

## Stats, Combat and capacity

Validated five-slot references resolve owned definitions and collect authored
modifiers once in registry order. Player supplies that group to existing Stats;
Character owns current resources and calculated maxima. Replacement removes the
previous contribution, and unequip removes the correct slot. Increasing maxHP/SP
does not heal; decreasing them clamps current resources through existing Character
behavior. No final ATK/DEF is written directly into persistent character data.

Main Hand reaches physical/magical outgoing Combat via the ordinary derived
snapshot. Body and Off Hand DEF reach the existing incoming Monster Combat
adapter; Shoes MDEF reaches the same Stats grammar. The retained Warden flat
reduction metadata is not applied a second time by incoming Combat. Equipment
owns no attack timing, damage formula, guard mechanic or movement modifier.

Capacity derives from owned stacks/instances, never equipment references.
Equip/unequip/replacement preserve occupied inventory slots and total weight,
including over-limit states. Five equipped instances count five owned instance
slots once. No artificial free-bag-slot requirement is added to unequip.

## Rewards, recipes and independent action systems

Monster Loot and Monster Box still create ordinary canonical instances without
auto-equip. All five compatible definitions can use their existing generic item
reward path; no drop table, content table, RNG, claim, lifecycle or pre-roll
capacity-envelope semantics change. Controlled acceptance fixtures award Off Hand
and Shoes through injected tables. There is no new production gear drop balance.

Existing Blade/Plate/Charm recipes retain their inputs/output and equip via the
same validator. Current merchant sells stack items only; no equipment inventory
or price is invented. Normal acquisition and crafting capacity preflight stay
intact. Potion/Ration, eight learned Action Slots and Basic Attack remain separate
systems. Gear neither consumes Skill Points nor uses Action Item clocks.

## Save representation, migration and conflict policy

Save version deliberately stays **5**. The persistent representation remains a
generic slot-ID reference map pointing into the same owned instance dictionary;
old keys retain exactly their old meaning. Adding two recognized keys does not
reinterpret the original three. No allocator, resource, capacity or ownership
schema changes, and `save-state.js` remains byte unchanged.

```json
{"equippedItems":{"weapon":"item-1","offHand":"item-3",
 "armor":"item-2","shoes":"item-4","relic":"item-5"}}
```

`normalizeDetailed`/`normalizeSlots` produce all five keys in fixed order.
Old version-5 maps gain null entries for missing slots without allocation.
Known semantic alias keys migrate to stored IDs. An explicitly present stored
key wins over its alias, including null or a malformed reference: the conflicting
extra stays owned and unequipped, never auto-granted or deleted. Duplicate instance
references retain the first valid compatible slot in registry order. Unsupported,
orphan, non-equipment and wrong-slot references contribute no Stats.

Normalization evidence is stored once in `itemHistory.equipmentSlotNormalization`
when repairs are necessary, preserving key, safe instance ID and reason. It is
diagnostic history, not an executable equipment map. Unknown slots are archived
there and remain inactive. All their valid owned instances remain owned. Repeated
normalization/load/save is idempotent; no history accumulation, reimport or serial
advance occurs solely because slots normalize.

Pre-v5 counted equipment/name migration remains the established one-time bounded
import. It reuses matching owned instances and represents historical equipped-only
gear once. Original input/name history survives; unknown names grant nothing.
Future save versions above 5 still reject before normalization/overwrite. A future
schema with changed slot meaning/ownership must make its own deliberate version
decision; this task does not claim arbitrary future-save compatibility.

Death/respawn, class change and town/field travel preserve references, ownership,
serial and capacity. Existing runtime ticket invalidation remains independent.
Reload reattaches modifiers from saved references, never creates replacement gear.

## Provisional fixtures and tooling

Only two proof definitions are added: `offhand-proof` with existing-stat DEF +1,
and `shoes-proof` with MDEF +1. Both are non-stack equipment, explicit zero /
unconfigured weight, tagged by non-final fixture metadata. Existing Blade +6,
Plate DEF +2 and prototype accessory ATK/MATK +3 remain unchanged. No movement
effect, rarity, shields skills, gear catalogue or economy progression is implied.

The Bag gains plain functional rows/buttons using existing classes: five active
labels, owned instance equip and per-slot unequip. Existing legacy item controls
remain supported. No layout/style/art redesign, drag/drop, tooltip or appearance
composition is introduced. Gameplay IDs are available to future visual layers;
sprites, attachments, renderer and animation do not determine equipment authority.

`/tools/inventory.html` displays registry, legacy mapping, five references,
eligibility/results, modifiers, Stats, capacity and saves. It creates proof gear,
equips/replaces/unequips and inspects migration with the existing isolated key
`astraeon-inventory-dev-v1`. Exact `dev=1` exports the new read methods alongside
existing canonical mutations for disposable live acceptance. Ordinary URLs expose
no equipment harness/developer mutation API. Cache/boot/page v94 precaches the
registry; previous explicit compatibility cache URLs remain actual responses.

## Limits and future work

Local client integrity only: catalogues, restriction hooks and synchronous Stats
providers are trusted, not server security against modified JS/storage. No final
class/level constraints, two-hand/dual-wield, cosmetic slots, enhancement, affixes,
sets, sockets, durability, final UI or visual equipment are implemented. Proof
gear has no new normal-world acquisition path; owner-authored content comes later.
Future Slot additions must update registry/definitions/migrations and tests.

Run README verification commands and see the [verified handoff](CORE_SPINE_EQUIPMENT_SLOTS_REPORT.md).
Recommended next Core Spine foundation: **Talk / Kill / Collect Quest contracts**;
Storage interaction remains a separate remaining roadmap requirement.

## Shop / Storage ownership relationship

[Shop and Storage](CORE_SPINE_TOWN_SERVICES.md) retain normal owned instances.
Shop equipment buy uses the canonical allocator and does not auto-equip. Sale
and deposit of an equipped instance reject `ITEM_EQUIPPED`; explicit unequip
comes first. Stored instances are not carried and cannot equip or modify Stats.
Withdrawal moves the same identity/metadata back, without serial or automatic
slot assignment. The five-slot registry and equipped reference semantics remain
unchanged; no appearance layer is introduced.
