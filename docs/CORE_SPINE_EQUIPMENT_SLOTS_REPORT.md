# Equipment Slot Closure — foundation handoff

Only this foundation is implemented. **Patch 0.0.1 and Core Spine are not
complete.** See [contracts](CORE_SPINE_EQUIPMENT_SLOTS.md). Final gear content,
balance and visual equipment appearance are not approved by these checks.

## Git identity / resume

| Field | Value |
| --- | --- |
| Branch | `backbone/equipment-slot-closure-0.0.1` |
| Starting parent branch | `backbone/inventory-capacity-weight-0.0.1` |
| Authoritative starting parent HEAD | `621b1cd214218078beb70392f647a48a9bfdef25` |
| Parent runtime checkpoint, not used as HEAD | `0e4b20f565cdd5cbac9c001bec1295e68f18cca8` |
| Runtime/test checkpoint | `1315d3f7ff7be9fd5aa6e04cb582c8e840cdba34` |
| Final HEAD | Documentation successor; resolve `git rev-parse HEAD` on this branch. Exact final/pushed SHA is recorded in final response and external FINAL_HANDOFF.md. |

Fetch/switch/ff-only pull and clean updated parent were confirmed before creating
the requested branch. No stale-SHA reset, unrelated merge, history rewrite or PR.
Core checkpoint `8f3401f` precedes the stable runtime/test checkpoint above.

**Verification in progress:** Node and final five-slot browser pass. The remaining
browser sequence is running; Capacity's first attempt timed out at learned contact.
Read external `browser-final/runner.json`, rerun failed suites unchanged with
authoritative-state diagnostics, finish audit, commit documentation and push
normally. Acceptance is not declared until verification completes.

## Architecture / integration report

| Requested field | Implemented contract |
| --- | --- |
| Equipment Slot architecture | Immutable registry, pure owned-reference validation/transitions and existing Item State publication; no second ownership authority |
| Active slot registry | Fixed order Main Hand, Off Hand, Body, Shoes, one Accessory |
| Future slot boundary | Head/Garment/Accessory 1+2/cosmetics inactive; future registry/constraint changes preserve ownership |
| Legacy slot mapping | Inspected `weapon` = Main Hand, `armor` = Body, prototype `relic` = Accessory; stored IDs retain meaning; semantic aliases mainHand/body/accessory resolve to them |
| ItemDefinition equip contract | Existing equipmentSlots explicitly lists compatible IDs/aliases; validates identity, non-stack/maxStack 1, unique active slots, plain requirements and finite JSON/modifiers |
| ItemInstance ownership model | ItemInventory owns each stable serial-backed instance exactly once |
| Equipped reference model | Five slot-ID references to owned instance IDs/null; getEquipmentSlots is authoritative; deprecated getEquipment remains the derived original three-key read view |
| Equip eligibility | Valid active slot, inventory/reference map, owned known equipment definition, compatibility, no other-slot reference and existing synchronous restriction hook |
| Equip commit | Full validation then one Item State/Character publication; immutable result includes slot/semantic alias, new/previous instance, changed and capacity/inventory evidence |
| Replacement semantics | One publication; previous occupant remains owned/unequipped; no intermediate unequip or serial allocation |
| Unequip semantics | Clear reference only, retain identity/ownership; empty slot succeeds changed=false under existing accepted-publication revision policy |
| Same-instance multi-slot policy | ALREADY_EQUIPPED rejection if referenced elsewhere; explicit unequip then equip supported; no automatic move/multi-slot occupancy |
| Main Hand behavior | Existing Blade identity/modifiers and Basic Attack retained; canonical weapon, semantic mainHand |
| Off Hand behavior | Active offHand, provisional DEF fixture only; no dual-wield/block/shield skills |
| Body behavior | Existing Garb/Plate identity/DEF retained; canonical armor, semantic body |
| Shoes behavior | Active shoes, provisional MDEF fixture only; no movement effect |
| Accessory behavior | Existing Charm/chapter sigils retain one relic reference/ATK/MATK; semantic accessory; no second accessory/future Relic sockets |
| Stats integration | All valid references collect authored modifiers once in registry order; replacement/unequip remove correct contribution through existing Stats |
| Combat integration | Existing outgoing physical/magical and incoming Monster Combat read derived Stats; no Equipment damage formula or second Warden flat reduction |
| HP/SP max-resource behavior | Existing Character setters/clamping; increasing maxima does not heal; removing resource gear cannot leave current values above maxima |
| Capacity integration | Owned equipped instance counted once; equip/unequip/replacement zero slot/weight delta, including over-limit states |
| Monster Loot integration | Generic canonical instances equip normally; injected all-slot/Off Hand proof tables; no auto-equip/RNG/death/claim changes |
| Monster Box integration | Generic canonical gear equips normally; injected all-slot/Shoes tables; anti-shopping and pre-roll envelope unchanged |
| Merchant integration | Current merchant is stack-only; prices/capacity behavior retained; no invented gear purchase catalogue |
| Crafting integration | Existing Blade/Plate/Charm ingredients/output preserved; canonical instances use ordinary slot validation; no new recipes |
| Action Loadout relationship | Eight learned slots, Skill Points/ranks and action execution independent; equipment never enters Action Slots |
| Action Item relationship | Potion/Ration effects/cooldowns/consumption remain separate |
| Save representation | Generic equippedItems map gains two recognized keys; instance dictionary/serial schema unchanged |
| Legacy migration | Old canonical maps gain null missing slots without allocation; semantic keys normalize; pre-v5 count/name importer reuses matching owned instances |
| Migration conflict policy | Explicit stored key wins even null/invalid; first valid compatible duplicate reference in registry order wins; extras stay owned/unequipped |
| Unknown/orphan safety | Unsupported/wrong/missing references contribute no Stats; normalization evidence recorded once; no fabricated replacement gear |
| Save version decision | Deliberately 5: original keys retain meaning and generic reference map supports new keys; save-state.js unchanged |
| Future-save guard | >5 rejects before normalization/write; unsupported slot keys never silently activate |
| Death/respawn | Existing policy retains five references, ownership, serial and capacity; no gear grants/refunds |
| Town/field/travel | All references/ownership/Stats persist; no duplicate instance or capacity drift |
| Developer tooling | Isolated inventory harness inspects registry/mapping, five references, eligibility/result, Stats/capacity, saves and safe legacy migration; exact dev=1 adds read APIs |
| Visual boundary | Functional Bag rows/buttons with existing classes only; no sprite/layer/attachment/renderer/motion/VFX/style changes |

## Proof gear / provisional data

Only **offhand-proof** (“Off Hand (proof)”, DEF +1) and **shoes-proof** (“Shoes
(proof)”, MDEF +1) are added. Both are non-stack/maxStack 1, explicit zero /
unconfigured weight and non-final fixture metadata. No production drop/shop/recipe
is added. Existing Blade ATK/MATK +6, Plate DEF +2 and accessory ATK/MATK +3
remain unchanged. Injected test catalogues add temporary maxHP/SP, flexible slots
and .125 weights solely for boundary proof; production data is unchanged.

No final gear catalogue, class/level/stat restriction, stat budget, rarity,
enhancement, affix/socket/durability/set, two-handed or dual-wield rule. No final
visual equipment or UI design. Future visual layers may consume semantic IDs.

## Deterministic verification

`python tools/run-node-checks.py --node D:\Node\node.exe`

**1309 pass / 0 fail, 21 files: 1155 previous checks + 154 new checks.**
Evidence `node-identity-final/report.json`. Nine additional edge checks reject
non-string/empty instance IDs before property coercion or mutation. This focused
review fix changes no behavior for canonical string IDs. The recorded runtime/test
checkpoint includes this guard and browser coercion coverage. Final focused browser
replay is scheduled after the first complete regression sequence and diagnostic retries.
New tests cover registry/definition validation,
all-five equip/replace/unequip, wrong/unowned/duplicate references, immutable
results, callback nesting, combined Stats/Combat, max-resource safety, weighted
and over-limit zero capacity delta, Loot/Box canonical instances and serial/claim
safety, craft/current merchant, aliases/conflicts/unknown slots, pre-v5/v5/future
guard, twenty normalization/save/load cycles for both classes, death/travel/action
independence and protected-source/import/cache contracts.

All original test declarations/behavioral assertions retained. Thirteen old Node
files receive the registry import. One Capacity authored-source guard was adapted
to permit the requested proof additions: it now compares **every original
definition field**, recipe, merchant price, counter and old name mapping exactly
to historical source. All other protected source guards remain intact; no old
gameplay assertion was removed or weakened. Audit checks twenty old Node suites
and twelve unchanged browser/cache sources (including unrelated world browser).

## Browser acceptance / local smoke

Disposable Swordsman and Mage, local Chrome, ordinary Bag controls, real learned
Skill/Basic Attack encounters and isolated fixtures. Final five-slot suite passed
**59 groups**, no console/page/runtime/HTTP errors. Counts count each successful
suite once, not repeat attempts. Final previous-suite sequence is pending.

| Suite | Pass groups | Status |
| --- | --- | --- |
| equipment_slots_browser.py | 59 | passed |
| inventory_capacity_browser.py | 63 baseline | initial contact timeout; rerun pending |
| monster_box_browser.py | 33 baseline | initial contact timeout; rerun pending |
| monster_lifecycle_browser.py | 30 | passed |
| monster_loot_browser.py | 26 baseline | initial alive-enemy wait timeout; rerun pending |
| action_item_browser.py | 30 | passed |
| inventory_browser.py | 15 | passed |
| action_loadout_browser.py | 17 | passed |
| combat_browser.py | 21 | passed |
| skill_tree_browser.py | 11 baseline | pending |
| progression_browser.py | 7 baseline | pending |

New suite proves each ordinary Bag slot, replacement/old ownership/serial,
combined Stats and both Combat directions, wrong-slot/no-mutation, flexible
duplicate-ref rejection, controlled Loot Off Hand and Box Shoes/no auto-equip,
existing Box bulk/stale/duplicate/Action Item, actual death/new-life loot and
EXP/gold/quest, actual player death/respawn retaining five references, actual
all-five save/reload/town-field travel, isolated legacy/conflict twenty cycles
and normal-URL absence of mutation APIs. Existing regressions cover merchant,
crafting, capacity, loadout, skills and progression. No visual appearance claim.

### Timing / attempts

Initial new suite timed out waiting for learned contact before slot assertions;
`browser-focused/report.json` retained. Only new-suite targeting was adjusted:
inspect actual runtime position, reselect, wait for readiness, at most three
ten-second contact attempts, still requiring the exact Skill Combat source.
Basic Attack uses bounded authoritative kill state and records retargets. No
Combat/AI/action change or old browser assertion modification. Focused rerun and
final stable-runtime replay each passed all 59 groups; focused rerun had no
retarget observations. Final previous Capacity attempt hit the unchanged 30-second
learned-contact wait after 17 groups; Box hit the same wait after 10 groups.
Loot passed six groups including learned Combat, then timed out on a 40-second
alive-enemy wait during its real five-kill itinerary, after a recorded waypoint
and Basic Attack retarget. All three error arrays were empty. The unchanged suites
will rerun sequentially with read-only wait-boundary snapshots; no assertions or
timeouts are altered. Evidence will be added after completion; failures retained.

### Cache / world / audit

- Cache/offline final verification pending. Boot/page/cache **94** includes registry
  before Equipment and actual v90/v92/v93 compatibility precache responses.
- World validator passed Terrain, Navigation, TownObject and AnimationManifest.
  Initial missing-jsonschema environment error was corrected with existing
  external dependencies; no repository change.
- Runtime diff check passed; final audit pending. Source audit verifies 23 stable
  core files unchanged after Git newline normalization, all previous browser
  sources unchanged, Node declarations retained, visual/world paths untouched.

## Limitations / merge risks / untouched files

Legacy canonical IDs are deliberate; new consumers use registry aliases and
**getEquipmentSlots()**, not deprecated getEquipment. Older clients cannot
interpret new equipped keys; current-client returning-save support does not
claim compatibility when downgrading to old application code. Same-instance
cross-slot assignment requires explicit unequip first. Off Hand/Shoes proof gear
has no new ordinary acquisition balance. Current merchant is stack-only; original
zero weights and conservative Box/full-loot capacity limits remain unchanged.
Catalogues/restriction/Stats callbacks remain trusted synchronous local code;
nested item mutations are blocked, arbitrary external callback effects are not
universally rollbackable. No server security claim.

Potential conflicts: Item definitions/equipment/state, Player adapter, game.js Bag
binding, boot/cache imports and harness script lists. No unrelated branches merged.

Untouched: authoring, RO3 Ref, assets/world/Blender, renderer, lighting/geometry,
sprites/atlases/animation, motion/VFX/camera/style/visual evidence; Progression,
Stats, Skill, Combat, Action Loadout/Item, Loot/Lifecycle/Box/Capacity/Inventory/
Save cores; original authored gear/recipes/prices/drop/content and historical reports.

## Files

Added: equipment-slots.js; tests/equipment-slots.test.cjs;
tests/equipment_slots_browser.py; docs/CORE_SPINE_EQUIPMENT_SLOTS.md;
docs/CORE_SPINE_EQUIPMENT_SLOTS_REPORT.md.

Modified: README.md; ARCHITECTURE.md; boot.js; index.html; sw.js; item-definitions.js;
item-equipment.js; item-state.js; player-state.js; game.js;
docs/CORE_SPINE_ITEMS.md; docs/CORE_SPINE_INVENTORY_CAPACITY.md;
tools/inventory.html; tools/inventory-harness.js; tools/inventory-capacity.html;
tools/monster-box.html; tools/monster-lifecycle.html; tools/monster-loot.html;
tools/progression.html; tests/action-item.test.cjs; tests/action-loadout.test.cjs;
tests/action-runtime.test.cjs; tests/combat-resolution.test.cjs;
tests/compatibility-hardening.test.cjs; tests/inventory-capacity.test.cjs;
tests/item-inventory-equipment.test.cjs; tests/monster-box.test.cjs;
tests/monster-lifecycle.test.cjs; tests/monster-loot.test.cjs;
tests/motion.test.cjs; tests/save-progression.test.cjs; tests/skill-tree.test.cjs.

## Evidence / final Git state

External evidence `D:\Astraeon\backbone-verification\equipment-slots`:
node-final/report.json; browser-final/runner.json and suite logs/reports;
browser-focused/report.json (initial timeout); browser-focused-retarget/report.json;
world-validation.log; source-audit.json; final FINAL_HANDOFF.md. Repository
source/tests/contract/report suffice to resume without session memory.

After documentation commit and ordinary push:

```powershell
git status --short   # expected empty
git rev-parse HEAD   # exact final documentation HEAD
git log --oneline -12
```

Recommended next Backbone task: **Talk / Kill / Collect Quest foundation**.
Storage remains separate required work. Patch 0.0.1/Core Spine remain incomplete.
