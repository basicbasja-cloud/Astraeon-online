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
| Runtime/test checkpoint | `645ddc77a26f0005c9c9cbcb490505856f76162b` (final source/test checkpoint) |
| Final HEAD | Documentation successor; resolve `git rev-parse HEAD` on this branch. Exact final/pushed SHA is recorded in final response and external FINAL_HANDOFF.md. |

Fetch/switch/ff-only pull and clean updated parent were confirmed before creating
the requested branch. No stale-SHA reset, unrelated merge, history rewrite or PR.
Core checkpoint `8f3401f` and identity/browser checkpoint `1315d3f` precede
the stable runtime/test checkpoint above.

**Verification complete for this foundation:** Node **1309/0**, functional
browser **312/0** (253 retained + 59 new), cache/offline and world schemas pass.
Final mapped Loot and fresh Lifecycle/Action Item/Inventory replays pass. Original
assertions are retained; inherited encounter-fixture failures and diagnostics are
recorded below. All source changes are committed at the runtime/test checkpoint;
the final commit is this verified documentation successor. Push only this branch
normally; confirm local/remote equality and clean status. No PR/merge.

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
Final evidence `node-checkpoint-645ddc7/report.json`; earlier identity run
`node-identity-final/report.json`. Nine additional edge checks reject
non-string/empty instance IDs before property coercion or mutation. This focused
review fix changes no behavior for canonical string IDs. The recorded runtime/test
checkpoint includes this guard and browser coercion coverage. Final focused browser
replay passed 59/0 in `browser-identity-final/`, with no runtime/HTTP errors.
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
and twelve prior browser/cache sources (including unrelated world browser).
Nine remain byte unchanged; three contain only encounter-fixture adapters. AST
comparison retains every original assertion and wait predicate/total deadline.

## Browser acceptance / local smoke

Disposable Swordsman and Mage, local Chrome, ordinary Bag controls, real learned
Skill/Basic Attack encounters and isolated fixtures. Final five-slot suite passed
**59 groups**, no console/page/runtime/HTTP errors. Counts count each successful
suite once, not repeat attempts. **312 passing functional groups / 0 failures:
253 previous + 59 new.**
All eleven functional suites and cache/offline ran; repeat attempts are not added
to totals. Lifecycle, Action Item and Inventory were replayed after the final
identity guard; current final Loot fixture was replayed separately.

| Suite | Pass groups | Status |
| --- | --- | --- |
| equipment_slots_browser.py | 59 | passed |
| inventory_capacity_browser.py | 63 | recovery replay passed |
| monster_box_browser.py | 33 | recovery replay passed |
| monster_lifecycle_browser.py | 30 | fresh final replay passed |
| monster_loot_browser.py | 26 | final mapped replay passed |
| action_item_browser.py | 30 | fresh final replay passed |
| inventory_browser.py | 15 | fresh final replay passed |
| action_loadout_browser.py | 17 | passed |
| combat_browser.py | 21 | passed |
| skill_tree_browser.py | 11 | passed |
| progression_browser.py | 7 | passed |

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
and Basic Attack retarget. All three error arrays were empty. Unchanged diagnostic
reruns reproduced all three. Parent `621b1cd` served through a read-only HTTP
overlay also reproduced Capacity contact cancellation and Loot's alive-enemy
timeout, without changing the checkout or parent history.

Capacity parent evidence: anticipation at 4.642s, incoming hit at 4.751s,
zero outgoing results at the original 30-second deadline. Current runtime shows
the same incoming-hit cancellation. Fixture adapters now observe a real incoming
attack, then wait for target cadence/recovery before the original single cast.
They do not disable AI, change Combat or loosen the original exact skill-source
assertion. Capacity and Box recovery replays pass all 63/33 groups.

Loot initially showed zone 0 / no enemies / four kills, which was provisionally
interpreted as fixture death. A health-only diagnostic replay disproved that:
HP 179/184, gold unchanged at 98, navigation to (2.5,14), reach 1.2, followed by
the town **gate return arrival**, not death respawn. Its clamped offscreen ground
waypoint overlapped a map gate. The health heartbeat was removed; no additional
healing remains in the final fixture. Ordinary keyboard movement now handles
offscreen approach first with the original 15-second / >1 movement condition,
then visible monsters are clicked using authoritative Lifecycle position. Original
kill/range/reward/actual-death/travel assertions and total deadlines remain.
No gameplay collision, input, Combat, AI or gate code changes. The coordinate-only
attempt also failed at the gate, confirming waypoint handling was required.
Keyboard replay passed the gate/Swordsman itinerary but exhausted the unchanged
Mage second-itinerary 240-second bound. Read-only evidence showed repeated
active/recovery cast phases, no new hits, player (21.469,20.050), target
(26.189,17.427), direction (.874,-.486). Existing `.45` projectile muzzle reaches
(21.863,19.832), inside the existing field inn collider (22,20) with its .2 margin.
Range alone does not guarantee a clear muzzle. The fixture now takes an ordinary
bounded keyboard step closer after a seven-second Basic Attack miss, preserving
the original movement condition, range/death/reward assertions and overall bound.
No extra HP mutation, teleport, enemy HP edit or collision bypass is introduced.
The final keyboard step selects the best dot-product direction from the game's
existing eight input mappings; a screen-sign pair can head south under the
non-square basis. A focused external Node check confirms the north-east corner
approach chooses D with world direction (.844,-.537). First closer-step replay
and final mapped replay each passed **26/0**. Final
mapped evidence records eight ordinary offscreen waypoints, one bounded Mage
miss and one closer approach; no runtime/HTTP errors. Fresh final Lifecycle
30/0, Action Item 30/0 and Inventory 15/0 replays also pass. All failed attempts
and snapshots remain retained; no live failure is concealed by the totals.

### Cache / world / audit

- Cache/offline passed: `astraeon-static-v94`, **152** precached responses, obsolete
  cache removal, saved-character/offline town/world resume and hash/error checks.
  Registry loads before Equipment; actual v90/v92/v93 compatibility URLs retained.
- World validator passed Terrain, Navigation, TownObject and AnimationManifest.
  Initial missing-jsonschema environment error was corrected with existing
  external dependencies; no repository change.
- Final `git diff --check` and source audit passed. Source audit verifies 23 stable
  core files unchanged after Git newline normalization, original browser assertions
  and waits retained, Node declarations retained, visual/world paths untouched.

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
tests/motion.test.cjs; tests/save-progression.test.cjs; tests/skill-tree.test.cjs;
tests/inventory_capacity_browser.py; tests/monster_box_browser.py;
tests/monster_loot_browser.py (fixture setup only; all prior assertions retained).

## Evidence / final Git state

External evidence `D:\Astraeon\backbone-verification\equipment-slots`:
node-checkpoint-645ddc7/report.json; verified-manifest.json;
browser-final/runner.json and initial suite logs/reports;
browser-identity-final/; browser-recovery-fixture/ (Capacity/Box passes and retained
failed health-only Loot attempt); parent-capacity/ and parent-loot/;
browser-loot-authoritative/ (coordinate-only failure), browser-loot-keyboard/
(retained corner failure), browser-loot-approach/ (26 pass), browser-loot-mapped/
(final 26 pass), browser-guard-final/ (fresh three-suite passes);
browser-focused/report.json (initial timeout); browser-focused-retarget/report.json;
world-validation.log; source-audit.json; final FINAL_HANDOFF.md. Repository
source/tests/contract/report suffice to resume without session memory.

At verified runtime/test checkpoint, `git status --short` is empty. Log below
is the source checkpoint; final documentation/pushed HEAD is its successor and
its exact final log/status are recorded in final response / external handoff.

```text
git status --short
(empty)

git log --oneline -12 645ddc7
645ddc7 Select acceptance approach keys through the existing eight-direction input mapper
d3305b1 Approach blocked ranged encounters through ordinary input in loot acceptance
3014ab5 Record final fixture checkpoint and remaining runtime verification
aeb1931 Use ordinary keyboard waypoints to avoid inherited loot fixture gate clicks
dc058c1 Stabilize inherited encounter fixtures using authoritative recovery and bounded health checks
d73e169 Record identity checkpoint and retained browser timing evidence
1315d3f Cover instance identity rejection in two-class equipment browser smoke
0f4c0fb Reject equipment instance identity coercion before slot publication
0e45913 Document equipment slot contracts migration and verification checkpoint
2c6a7eb Expose five owned equipment slots in Bag and isolated acceptance tooling
8f3401f Add five-slot equipment contracts and canonical reference authority
621b1cd Finalize verified inventory capacity and weight handoff
```

After documentation commit and ordinary push:

```powershell
git status --short   # expected empty
git rev-parse HEAD   # exact final documentation HEAD
git log --oneline -12
```

Recommended next Backbone task: **Talk / Kill / Collect Quest foundation**.
Storage remains separate required work. Patch 0.0.1/Core Spine remain incomplete.
