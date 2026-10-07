# Item Instance / Inventory / Equipment foundation — verification handoff

## Git checkpoints and scope

- Branch: `backbone/item-inventory-equipment-0.0.1`.
- Starting parent branch: `backbone/action-loadout-0.0.1`.
- Starting parent HEAD: `b7378b22bbaf5a7f7bde7bfacddda209f7230cd9`.
- Runtime/test checkpoint: `0cb2b2c55ed3341d278e5bc3ed24bcefc3f39bcc`.
- Final HEAD: the documentation successor of this checkpoint, printed with the
  final status/log in the chat handoff. The report cannot contain its own commit
  hash. No runtime/test changes follow the checkpoint.
- Parent was fetched, switched and pulled with `--ff-only`; the initial working
  tree was clean before creating the requested branch from remote parent HEAD.
- Focused commits separate pure models, Player/Save/cache integration, gameplay
  adapters, deterministic tests, developer/browser tooling and documentation.
- Only this branch is pushed; no merge, force push, history rewrite or PR.

This implements the requested item identity/ownership/equipment foundation.
**Patch 0.0.1 and Core Spine remain incomplete.** The release roadmap is the
design authority. The attachment narrows this step to weapon/armor/relic and
provisional weight/requirements; full roadmap inventory/gear/UI rules remain open.

## Files added

- `item-definitions.js`, `item-inventory.js`, `item-equipment.js`, `item-state.js`.
- `tools/inventory.html`, `tools/inventory-harness.js`.
- `tests/item-inventory-equipment.test.cjs`, `tests/inventory_browser.py`.
- `docs/CORE_SPINE_ITEMS.md`, `docs/CORE_SPINE_ITEMS_REPORT.md`.

## Files modified

- `player-state.js`, `save-state.js`: canonical authority, modifier bridge,
  consumables and deliberate version 5 migration.
- `game.js`, `exploration.js`: contained gameplay item mutation adapters.
- `boot.js`, `index.html`, `sw.js`, `tools/progression.html`, `tools/combat.html`:
  dependency imports/precache/version 88; production presentation stays unchanged.
- `tests/action-loadout.test.cjs`, `tests/action-runtime.test.cjs`,
  `tests/combat-resolution.test.cjs`, `tests/compatibility-hardening.test.cjs`,
  `tests/motion.test.cjs`, `tests/save-progression.test.cjs`,
  `tests/skill-tree.test.cjs`: required item imports and explicit supported/future
  version expectations. Existing behavioral assertions are retained.
- `tests/combat_browser.py`: future-version fixture 5 → 6, keeping the same
  overwrite/reload rejection assertions.
- `tests/cache_resume.py`: additionally requires all four item modules in precache.
- `README.md`, `ARCHITECTURE.md`, `docs/CORE_SPINE_PROGRESSION.md`,
  `docs/CORE_SPINE_SKILL_TREE.md`, `docs/CORE_SPINE_COMBAT.md`,
  `docs/CORE_SPINE_ACTION_LOADOUT.md`: current item/save/cache contract references.

## Architecture and integration results

| Requested area | Implemented contract |
| --- | --- |
| ItemDefinition architecture | Deeply frozen stable-ID definitions with name/key/kind/stackability/maxStack/slots/weight/modifiers/requirements/tags/metadata; no definitions in saves |
| Stackable inventory architecture | Definition-ID quantities; positive safe integers, unknown/non-stack/insufficient/overflow/maxStack validation; zero entry removal |
| ItemInstance architecture | `instanceId`, `definitionId`, cloned frozen serializable metadata; future fields do not replace identity |
| Instance-ID generation | Persisted `nextItemSerial`, deterministic `item-N`, no RNG/clock; deletion never reuses; malformed observed IDs reserve serial; exhaustion rejects |
| Canonical inventory state | One private stacks/instances/serial/history state; frozen getters and read-only counter compatibility view |
| Equipment architecture | Weapon/armor/relic reference owned instance IDs; equip/replacement/unequip retain ownership |
| Equipment validation | Known owned instance/definition, equipment kind, supported slot, no duplicate use, injected requirement hook, equipped deletion guard |
| Equipment modifier integration | Equipped definitions compile into the existing `equipmentModifiers` group once; legacyEquipment mapping never adds again |
| Stats integration | Existing primary/add/multiply pipeline and Character remain authoritative; no new derived formulas |
| Combat integration | Existing derived snapshot reaches unchanged Combat Resolution; live browser records observe gear damage increase |
| HP/SP equipment behavior | Increasing max does not heal, removal clamps, failure leaves resources intact; temporary modifiers stay out of persisted capacity |
| Legacy inventory migration | Existing stack quantities preserved, counted crafted gear becomes distinct instances, unknown historical keys retained |
| Legacy equipment migration | Fixed known-name mapping; reuse counted ownership; equipped-only imports once; unknown strings archived with no invented effect |
| Save version decision | Genuine ownership/allocator/reference schema generation: bump exactly once to 5; retain save key; reject >5 without overwrite |
| Migration idempotency | Exact historical fixture deterministic; 20 Node round trips preserve IDs/serial/quantities/modifiers/currency/point pools |
| Crafting integration | Plan all inputs plus output before commit; stack output or new unique equipment instance; failures consume nothing |
| Merchant integration | Existing authoritative prices; validate currency plus item plan; failures preserve both gold and ownership |
| Consumable integration | Potion +45 HP, Ration +20 SP consume exactly one canonical stack; validate effects before debit; Character clamps; Potion stays outside eight slots |
| Weight foundation | Pure owned stack × weight plus each owned instance once, including equipped; production weights zero/unconfigured |
| Developer tooling | Isolated harness supports all requested inspection/actions and migration view; live mutations require exact dev=1; normal URL has no developer mutation globals |

See [the full contract](CORE_SPINE_ITEMS.md) for API details, examples and schema.
Warden Plate's old incoming reduction 2 now comes from definition data; its DEF
contribution stays in Stats. Current enemy damage orchestration is retained.
Camp cooking/shrine effects retain current behavior with canonical item costs.
Discovery commits item rewards before claim/gold; kill/quest/dungeon item paths
use canonical batches, and chapter rewards create/equip stable owned gear.

## Provisional definitions and explicitly non-final decisions

Fourteen existing definitions only: three materials, two consumables and nine
existing gear objects (including four authored chapter relics). No new catalogue
is invented. Traveler Blade/Adventurer Garb retain empty modifiers; Astral Blade
retains ATK/MATK +6, known relics +3, Warden Plate DEF +2 and old incoming reduction
2. Current five recipe costs/outputs and merchant prices remain provisional.

Production weights are zero with explicit unconfigured metadata, stack caps use
safe integer limits, and requirements are empty extension data/hooks. Unit
fixtures inject maxStack/weight/requirements/primary/percentage/HP/SP modifiers
into existing definitions solely to prove architecture. They do not author
production restrictions or balance. No final rarity, item level, economy, drop
table, affix, enhancement, durability, binding, socket, set, bank, market/trade,
encumbrance or complete gear-slot design is implemented.

## Verification environment and commands

Windows local checkout `D:\Astraeon\astraeon`; Node v24.14.0, bundled Python
3.12.14, Python Playwright/jsonschema and local Chrome using ANGLE D3D11.
Disposable browser contexts/storage only. Local server:

```powershell
python -m http.server 8011 --bind 127.0.0.1
python tools/run-node-checks.py
python tests/inventory_browser.py --url http://127.0.0.1:8011
python tests/action_loadout_browser.py --url http://127.0.0.1:8011
python tests/combat_browser.py --url http://127.0.0.1:8011
python tests/skill_tree_browser.py --url http://127.0.0.1:8011
python tests/progression_browser.py --url http://127.0.0.1:8011
python tests/cache_resume.py --url http://127.0.0.1:8011
python tools/validate-world-v3.py
git diff --check
```

On this host normal `python` resolves to a Store alias; verification used the
bundled runtime's absolute path and external dependency PYTHONPATH. README's
ASTRAEON_BROWSER override selects the installed Chrome executable. Reports are
outside Git at `D:\Astraeon\backbone-verification\items`.

### Deterministic checks

| Suite | Pass / fail |
| --- | --- |
| New item/inventory/equipment | 88 / 0 |
| Action Loadout | 37 / 0 |
| Action Runtime | 56 / 0 |
| Combat Resolution/runtime | 86 / 0 |
| Compatibility hardening | 13 / 0 |
| Skill Tree | 45 / 0 |
| Progression | 10 / 0 |
| Stats | 14 / 0 |
| Save/progression | 13 / 0 |
| Motion/current runtime | 44 / 0 |
| Locomotion transitions | 19 / 0 |
| Expanded town | 7 / 0 |
| Golden pipeline | 3 / 0 |
| Painted locomotion | 3 / 0 |
| World v3 | 20 / 0 |
| **Total** | **458 / 0** |

All 370 previous individual checks remain, plus 88 new. Additional edge cases
cover serial exhaustion/quarantine, cyclic versus shared acyclic metadata,
canonical precedence, invalid modifier rejection, batch reward/output overflow,
currency overflow, unknown historical objects and malformed consumable effects.

### Browser acceptance

| Suite | Result |
| --- | --- |
| `inventory_browser.py` | 15 groups passed; no console/page/HTTP errors |
| `action_loadout_browser.py` | 17 groups passed |
| `combat_browser.py` | 21 groups passed |
| `skill_tree_browser.py` | 11 groups passed |
| `progression_browser.py` | 7 groups passed |
| `cache_resume.py` | Cache migration, all four item modules in v88 precache and offline saved-character reload passed |
| `validate-world-v3.py` | Terrain, Navigation, TownObject and AnimationManifest schemas passed |
| `git diff --check` | Passed |

Final browser reports contain zero console/page/runtime/HTTP errors. Accepted
browser total: **71 groups passed**, plus cache/offline acceptance and world
schema validation. Final full Node total: **458 passed, 0 failed**.

The new browser initially had a mistaken baseline assertion and waited for three
enemies to approach a stationary player. The assertion was corrected and input
now selects/walks toward actual existing field actors before Basic Attack.
No monster fixture or gameplay behavior was changed. Running five fresh browsers
at once exceeded the local static server's connection backlog (connection refused
before creation); final browser regressions were rerun sequentially and passed. These
diagnostic attempts are not accepted as successful verification.

## Disposable local smoke — both Swordsman and Mage

1. Normal creation yields the existing stacks and two stable starter instances.
2. Existing merchant buys/sells Herb at the old price; shared dev grants current
   materials; normal UI crafts Potion, Blade, Plate, Charm and Ration. Each gear
   output gets its own item-3/4/5 ID and recipe materials are consumed canonically.
3. Existing Bag buttons equip owned weapon/armor/relic. ATK/MATK increases by 9,
   DEF by 2, with three compiled contributions. Unequip weapon removes exactly 6
   and retains ownership. Twenty loops preserve current HP 40 and both maxima.
4. Potion/Ration restore 45/20 from resource 1 and debit once; legacy and canonical
   quantities agree. Learn/rank the first active to 2, learn passive, set Qi/Fire
   Node and assign slot 8 using existing Skill/Loadout APIs.
5. Town → field retains ownership/equipment/configuration. Learned slot 8 hits an
   actual actor; resolver input carries gear-derived stats, rank and Node and
   its HP application matches. For the recorded input/rolls, equipped damage is
   **91** versus **79** with only the weapon's +6 contribution removed, both classes.
6. Normal target/walk/Basic Attack kills produce canonical Ore/Herb and preserve
   Base/Job EXP, gold and quest credit. No rewards are injected for this check.
7. Town → disposable low-HP field fixture dies from an existing enemy and respawns
   in town; instances/serial/equipment/learned ranks/payment/slots remain identical.
   Three ordinary save/reloads preserve gear, stacks, resources, paid ledgers,
   ranks, Nodes, quest and world claims.
8. Returning version 4 Mage with counted and equipped Blade/Plate/Charm reuses
   four total gear objects; historical inventory/slot/loadout/currency/quest/world
   data survives. Five reloads preserve exact IDs/serial/quantities/modifiers and
   old fixed-button execution remains usable without free ranks/points.
9. Actual isolated harness controls add/remove/create/equip/reject equipped delete/
   unequip/delete/create/save/reload/inspect migration; deleted ID never returns,
   and migration inspection leaves live state/playable storage untouched.
10. Ordinary URL boots with no progression/combat/item harness mutation globals.

Existing browser suites independently retain all eight slot execution, native
input/cost/cooldown/lock behavior, class dormancy, combat hit/miss/dodge/crit,
paid Stat/Skill refunds, passive/Nodes, future-save preservation and offline load.
These checks make no visual, artwork approval or physical-device performance claim.

## Known limitations and potential merge conflicts

- Local trusted synchronous controllers/hooks are not network authority or
  authentication. The historical name setter remains a bounded compatibility
  acquisition path; production code uses instance-ID equip.
- Normalization/validation clones/scans owned state; large inventories need later
  performance work. Legacy counted gear >10,000 blocks import with preserved
  source bytes rather than truncating or allocating an unbounded object count.
- Only metadata reserves future item fields; no affix/enhancement/durability or
  item-action framework executes. Merchant sells current materials only.
- Current weights/requirements and production gear catalogue remain provisional;
  no slot capacity, pickup cap, encumbrance, full gear suite or inventory UI.
- Unknown historical equipment remains display/history data with no executable
  modifier. This deliberately avoids the old blanket +3 for arbitrary relic names.
- Item reward batches reject atomically on stack overflow. Existing combat/quest
  lifecycle remains game orchestration; there is no full multi-system economy
  transaction coordinator or overflow mailbox in this step.

Potential merge conflicts: `game.js` item/reward/menu/dev adapters; Player/Save
authority; boot/page/SW module/version lists; developer imports; shared test
dependencies/version expectations and README/architecture/current contracts.
Future UI work should call the canonical APIs and display names from definitions.

## Files intentionally untouched and next task

No changes to `authoring/**`, `RO3 Ref/**`, `assets/**`, `world/**`, Blender,
renderer, geometry, lighting, sprites/atlases/animation art, motion, VFX, camera,
`style.css` or visual-review evidence. No changes to Progression/Stats formulas,
Character implementation, Skill definitions/tree/Nodes, Combat resolver/Timeline,
Action Loadout/Action Runtime implementation. Existing tests gain dependency/
version adapters only; their regression assertions remain.

`CURRENT_HANDOFF.md`, `REQUESTS_AND_STATUS.md`, `MASTER_PLAN.md`, the authoritative
roadmap and earlier verification reports remain historical/unmodified. Their
world/art acceptance state is not changed by this gameplay task.

Recommended next Backbone task: **Patch 0.0.1 Action Item / consumable execution
foundation** using canonical stacks, authored effect validation and shared
function cooldown groups, before broader item content/UI. Keep Potion outside
the eight learned-skill slots and explicitly scope returning-save policy. The
roadmap's remaining monster/loot-box/quest/storage/gear/capacity/status work still
needs separate implementation and acceptance; this report closes only the
requested Item Instance + Inventory + Equipment foundation.

Final chat includes the exact output of:

```powershell
git status --short
git log --oneline -12
```
