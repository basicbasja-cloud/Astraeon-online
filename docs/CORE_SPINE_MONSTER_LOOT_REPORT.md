# Monster Drop / Loot Resolution foundation — verification handoff

## Git checkpoints and scope

- Branch: `backbone/monster-loot-0.0.1`.
- Starting parent branch: `backbone/action-item-0.0.1`.
- Starting parent HEAD: `e7cdddca4fa70403a2254f52df22d05c1d6fdf86`.
- Previous Action Item runtime/test checkpoint:
  `a34b7f68d271800ccc83fb6f9ac6d6ba8e2b9d99`. Its documentation successor above
  was the authoritative remote HEAD; no reset to the older checkpoint occurred.
- Monster Loot runtime/test checkpoint:
  `08152f35506d03f0001315685e27fd7e8a0366b0`.
- Final HEAD: the documentation successor of that checkpoint, printed with final
  status/log in the chat handoff. This report cannot contain its own commit hash.
  No runtime/test changes follow the checkpoint.
- Parent was fetched, switched and pulled with `--ff-only`; working tree was
  clean before the requested new branch was created.
- Six focused implementation commits separate contracts/pure roll, owned
  claims/atomic adapters, gameplay/cache integration, deterministic hardening and
  developer/browser tooling, followed by existing finite-gold compatibility. Documentation is a separate final commit.
- Only this branch is pushed; no merge, force push, history rewrite or PR.

This implements **only Monster Drop / Loot Resolution**. Patch 0.0.1 and Core
Spine are **not complete**. The [contract](CORE_SPINE_MONSTER_LOOT.md) contains
the complete API, processing guards, persistence policy and trust boundary.

## Files added

- `monster-definitions.js`, `drop-tables.js`, `loot-resolution.js`,
  `monster-loot-runtime.js`, `monster-rewards.js`.
- `tests/monster-loot.test.cjs`, `tests/monster_loot_browser.py`.
- `tools/monster-loot.html`, `tools/monster-loot-harness.js`.
- `docs/CORE_SPINE_MONSTER_LOOT.md`, `docs/CORE_SPINE_MONSTER_LOOT_REPORT.md`.

## Files modified

- `character-state.js`: owned staged dual progression validation/publication;
  uses existing Progression and Stats, including the existing Base level refill.
- `item-state.js`: mixed canonical stack/instance planning and one publication;
  bounded equipment processing guard; no second inventory.
- `player-state.js`: contained reward transaction and transient quest generation;
  low-level arbitrary publisher excluded from public Player methods.
- `game.js`: register actors, notify death, consume one successful reward result,
  retire old populations and provide exact `dev=1` tooling/read-only QA identity.
  Old parallel kill grants removed. Existing death VFX values and combat/AI rules
  retained.
- `boot.js`, `index.html`, `sw.js`: ordered five-module loading/precache, version
  90; no stylesheet or world asset content changed.
- `tools/combat.html`, `tools/inventory.html`, `tools/progression.html`: current
  module cache query alignment only.
- `README.md`, `ARCHITECTURE.md`: current contracts, commands and cache version.
- Current `CORE_SPINE_PROGRESSION`, `SKILL_TREE`, `COMBAT`, `ACTION_LOADOUT`,
  `ITEMS`, `ACTION_ITEMS` contract docs: small integration notes/current version.
  Their historical verification reports remain unchanged.

## Architecture and integration evidence

| Requested boundary | Implemented behavior |
| --- | --- |
| Monster Drop architecture | Definition reference → registered runtime life → HP-zero event → pure resolution → owned claim → one canonical commit |
| Drop Table definition | Frozen entries with unique entry IDs, canonical item IDs, chance, inclusive quantity range, supported mode; optional currency and prototype killModulo condition |
| Authored validation | Entire table validated before entropy/mutation; structured code/path; unknown IDs, malformed quantities/chances/conditions/modes/duplicates/currency/JSON rejected |
| RNG model | Injected `next()` in [0,1); outer production Math.random adapter; exact sequence/order/boundary tests |
| Pure resolution | Frozen snapshot/result/roll evidence; no stack, currency or ItemInstance allocation |
| Monster/death identity | Private actor registration, monotonic `monster-N`, per-life `life-M:death-1`; no definition/coordinate/random-UUID authority |
| Entitlement/claim model | Cached first attempt per life; exact immutable object registered in private WeakMap |
| Duplicate protection | Repeat death returns same claim; used/copy/forged/foreign/stale claims reject; failed RNG attempt cannot reroll |
| Commit/transaction model | Prevalidate currency/quest/progression/derived Stats/items/serials/publication fields; contained synchronous publisher, then mark consumed |
| Stack reward integration | Canonical quantity add, compatibility views sync; zero equipment serial allocation |
| Equipment ItemInstance integration | Existing allocator per unit; unique item-N/definition ID, no auto-equip; existing Equip → Stats → Combat |
| Currency integration | Existing state.gold/save/merchant authority; explicit gold before/after/granted; current values retained |
| Base EXP / Job EXP | Existing Progression formula/transitions and activity ratio; separate orchestration adapter, once per death |
| Quest-credit relationship | Separate quest adapter; transient generation prevents credit to reaccepted quests; concurrent pending kills and completion once tested |
| No-drop behavior | Successful empty candidate and once-only reward lifecycle |
| Multi-drop behavior | Multiple independent entries and deterministic quantity range, plus mixed canonical stack/gear/currency publication |
| Respawn/new life | Existing replacement actor spawns register fresh ID; reused actor can explicitly increment life generation; stale old claims reject |
| Player death | Committed ownership/allocator retained; existing 8-gold respawn loss; population retirement prevents replay |
| Town/field | Existing travel cost retained; ownership unchanged; old claims retired; fresh population requires new gameplay kills |
| Save/reload | Version 5 unchanged; committed stacks/instances/serial/gold persist; claims/enemy HP/dungeon state are transient; no reward granted at load |
| Monster Box boundary | Future canonical stack reward possible; no definition/opening/content-table implementation |
| Inventory capacity boundary | Structured owner/commit rejection retains exact pending entitlement for retry; no capacity/weight/overflow policy or UI |
| Future Monster Lifecycle integration | Register / authoritative zero-death / prepare / commit / explicit newLife; inventory/RNG/save details contained |
| Developer tooling | Isolated in-memory harness and exact dev=1 live inspection/fixed fixtures/commit/duplicate/new-life; ordinary URL mutation globals absent |

## Provisional fixtures and numbers

No new ItemDefinitions, final monster catalogue, final economy or drop balance.
Production preserves Ore/Herb/Shard kill cycles 3/2/4, normal gold 4+2*zone,
Base EXP (boss ? 25 : 7)+3*zone, existing Job ratio, current quest rewards and
sparring/Echo compatibility extras. Echo's old special path remains dormant in
the current field factory; no new live Echo was authored.

Isolated non-final proof tables: Herb 2/gold 7; Potion 2; one existing Astral
Blade; empty; multi Herb .5 quantity 1–3, Potion .5, Astral Blade .25/gold 7.
Fixture quantities/odds/currency are authored and easily replaced. Proof deaths
do not advance production kill ordinals or grant Base/Job EXP/quest credit.
Technical guards: 256 table entries, metadata depth 64, 10,000 equipment units
per package; these are processing limits, not final inventory capacity/balance.

## Local verification environment and commands

Checkout: `D:\Astraeon\astraeon`; disposable artifacts outside Git:
`D:\Astraeon\backbone-verification\monster-loot`.
Windows PowerShell, Node 24.14.0, Python 3.12.14, Playwright and local Chrome
with D3D11. The documented localhost server serves port 8011. Browser suites run
sequentially to avoid contention on the Python static server.

```powershell
python -m http.server 8011 --bind 127.0.0.1
python tools/run-node-checks.py --output D:\Astraeon\backbone-verification\monster-loot\node
python tests/monster_loot_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\browser
python tests/action_item_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\action_item_browser
python tests/inventory_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\inventory_browser
python tests/action_loadout_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\action_loadout_browser
python tests/combat_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\combat_browser
python tests/skill_tree_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\skill_tree_browser
python tests/progression_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\progression_browser
python tests/cache_resume.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-loot\cache_resume
python tools/validate-world-v3.py
git diff --check
```

The managed Python executable/dependency path and ASTRAEON_BROWSER were supplied
explicitly for this host; README's commands/files are otherwise unchanged.

## Deterministic tests

**712 passed / 0 failed**: all **548 previous checks retained unchanged**, plus
**164 new Monster Loot checks**. The new suite covers validation/entropy and
immutability/purity; exact chance/quantity boundaries and no/multi-drop; owned,
duplicate/forged/foreign/stale claims; failed entropy caching; real/proof ordinal
separation; new life and independent monsters; exact stack/consumable/instance
publication and serial uniqueness; mixed reward atomic failures/retry; currency,
progression/quest/completion, finite fractional-gold save compatibility, non-finite
currency rejection, reaccepted quest and concurrent pending death
behavior; level refill and zero-EXP cap behavior; Action Item consumption;
Equipment → Stats → Combat; v1–v5 migration/normalization and future-save reject;
reload/death/travel policy; boot/precache and ordinary URL developer gates.

Previous Node counts: Action Item 90; Action Loadout 37; Action Runtime 56;
Combat Resolution 86; Item/Inventory/Equipment 88; Skill Tree 45; Progression 10;
Save Progression 13; Stats 14; compatibility hardening 13; world/motion/locomotion
regressions 96. No old assertion was removed or weakened.

## Browser acceptance and local smoke

**Monster Loot: 26 groups passed**, runtime/page/console errors **0**, HTTP errors
**0**. Both disposable Swordsman and Mage verified ordinary character boot,
immutable mixed fixture preparation/commit/duplicate, canonical Potion execution,
looted instance equip/Stats and live learned skill Combat damage, no-drop, reused
actor life generation, actual Basic Attack kills, unique death events, original
material/gold/Base EXP/Job EXP/quest completion, actual duplicate death rejection,
existing field replacement spawn and a legitimate kill/reward of that replacement,
travel, repeated save/reload and actual enemy-caused player death/respawn.

Each class's first five real gameplay deaths produced **five distinct events**,
with **zero final Basic Attack retarget timeout retries**. The existing replacement
actor `monster-11` was observed and subsequently rewarded. Ordinary visible
ground waypoints were needed for offscreen actors; these observations are retained
in the report, rather than changing actor positions or combat.

The isolated harness exercised validation, exact RNG, non-mutating resolve,
commit, duplicate and new life, and proved it did not write the playable save.
Normal URL boot exposed none of the intended developer mutation APIs.

Previous browser verification: **all final unchanged runs passed**.

| Suite | Passed groups |
| --- | ---: |
| Action Item | 30 |
| Item / Inventory / Equipment | 15 |
| Action Loadout | 17 |
| Combat Resolution | 21 |
| Skill Tree | 11 |
| Progression | 7 |
| Previous browser total | **101** |
| Monster Loot | **26** |
| Combined browser total | **127** |

All final browser runs report empty runtime/page/console and HTTP error arrays.
Cache resume also **passed**: v90 precache, legacy-cache removal, offline town,
retained saved character, legacy-town migration and blocked-save recovery. Cache
checks are additional to the 127 browser groups. Final runs use runtime checkpoint
`08152f35506d03f0001315685e27fd7e8a0366b0`; subsequent changes are documentation only.

The automated local smoke combines the focused loot suite and unchanged previous
Action Item/inventory suites on disposable characters. It covers current merchant
buy/sell, all crafts, starter/looted gear, Basic Attack, learned skill and Action
Item input, town/field flow, enemy/player respawn, canonical save/reload and absence
of duplicate rewards. It makes no manual-device, art/visual or performance claim.

World validator: **PASS**, all Terrain, Navigation, TownObject and
AnimationManifest schemas. No world data was modified. Diff whitespace check:
**PASS**.

## Live-targeting/timing observations

The previous Action Item handoff's unchanged Mage inventory-browser timeout is
retained as historical evidence in its report. The old browser suites remain
unchanged in this task.

The first complete previous-suite pass in this task was green. During the final
rerun after finite-gold compatibility validation, unchanged `inventory_browser.py`
again timed out at its 60-second Mage Basic Attack kill wait (10 prior groups
passed). Console/page/runtime and HTTP error arrays were empty. That failure is
retained separately as `inventory-browser-final-initial-failure.json`; the original
file and assertions were not edited. The unchanged rerun passed every original
assertion (15 groups), with no console/page/runtime/HTTP errors; all remaining
previous suites also passed before push.
The final focused loot suite retained real kills for both classes and passed,
and currency-predicate changes do not alter normal integer-balance combat input.

Four initial versions of the new browser driver failed during targeting, with
successful core fixture/real reward evidence and no console/page/HTTP errors:

- `browser-initial-failure.json`: bounded Basic Attack drive stopped after four
  unique real deaths; Tab cycled away from the selected actor.
- `browser-held-attack-failure.json`: direct click still held warrior attacks
  before approach; the unchanged warrior movement scale is zero during attack.
- `browser-approach-failure.json`: range wait exposed an unselected far actor.
- `browser-offscreen-target-failure.json`: diagnostic click x=1306.77 was outside
  the 1280-pixel viewport; elementFromPoint was null and no navigation target existed.

The final **test driver only** waits on actual actor identity/HP/distance before
holding attack and first walks through visible ground waypoints when an actor
projects offscreen. All original five-kill/replacement/quest assertions remain.
It preserves at least one real gameplay kill (in fact multiple for each class),
does not teleport actors or fake combat damage, and records bounded retries.
No Combat, movement, navigation, animation or AI rule was rewritten to pass waits.
The final suite passed all 26 groups and reported no kill-wait timeout retries.

## Known limitations, conflicts and untouched files

- Local owned-object integrity only; JavaScript edits are not server security.
- Trusted catalogs/hooks/custom owner publishers must be side-effect-free during
  planning and synchronous/non-throwing at publication. Arbitrary external side
  effects have no universal rollback. Normal contained publisher prevalidates all
  deterministic failure conditions and plain writable fields.
- Direct death-to-inventory remains current behavior. No ground pickup entity/UI.
- Active enemy combat/dungeon/claims are not persisted. Reload creates a fresh
  population, without replaying a dead claim; later new kills can reward normally.
  Durable encounter/claim persistence is a future lifecycle contract.
- Commit rejection retains a pending result for retry; current travel/retirement
  discards transient pending claims. A future capacity/pickup system must specify
  retention before enabling capacity failure/overflow during production travel.
- An invalid first resolution attempt stays failed for that life; no free reroll.
  A failed real death can leave an ordinal gap. Valid prototype direct commits
  retain the exact existing cycles.
- No weighted-group grammar, final monster catalogue, final odds/economy, Box
  opening, party distribution, full AI/lifecycle, final capacity, affixes or server
  authority is implemented.

Potential merge conflicts: `game.js`, the small Character/Item/Player adapter
extensions, boot/index/SW version lists, harness imports and current docs. No
unrelated branch was merged; protected parent branches remain untouched.

Intentionally untouched: `authoring/**`, `RO3 Ref/**`, `assets/**`, `world/**`,
Blender files, renderer/geometry/lighting/camera, sprites/atlases/motion/animation
art, VFX modules, `style.css`, visual-review evidence; ItemDefinitions,
ItemInventory/Equipment, Save, Progression/Stats, Skill Tree/Runtime,
Combat Resolution/Runtime, Action Loadout/Runtime, Action Item/Runtime and all
previous test files. Their stable formulas/schemas/assertions remain intact.

Recommended next Backbone task: **Monster Lifecycle / AI foundation**, calling
the established registration/death/claim/commit/new-life boundary. Monster Box
opening and inventory capacity remain separate later tasks. **Patch 0.0.1 and
Core Spine are not complete.**
