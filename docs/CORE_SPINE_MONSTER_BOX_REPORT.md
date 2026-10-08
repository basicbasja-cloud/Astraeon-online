# Monster Box Item / Opening foundation — handoff

**Verified 2026-10-08.** Runtime, contract, focused acceptance and all requested
previous regressions passed. This implements only the Monster Box foundation.
Patch 0.0.1 and Core Spine are **not complete**.

## Git identity and resume point

- Branch: `backbone/monster-box-0.0.1`.
- Starting parent branch: `backbone/monster-lifecycle-0.0.1`.
- Starting parent HEAD: `05243a45737dbe5a493b7753f5517d7ea920243b`.
- Runtime/test checkpoint: `9f52bd84b51f1413d036c25be6b1dcde14655a23`.
- Contract checkpoint: `abd2750ff8e0e0619d6c8b6bba1369f3247496e0`.
- Final HEAD: documentation successor, printed with final status/log in the chat
  handoff. This document cannot embed its own commit hash; use `git rev-parse HEAD`
  after checking out the released branch. Runtime/test code is unchanged after
  the checkpoint above.

Step 0 fetched origin, switched/pulled parent ff-only, confirmed clean tree and
created this branch from authoritative remote HEAD. No reset to the older
`535a1b1` checkpoint, unrelated merge, PR, force push or history rewrite occurred.
All requested verification is finished, including a final pre-push Node rerun,
source/authored-data audit and `git diff --check`. Final publication uses only
`git push -u origin backbone/monster-box-0.0.1`; final response records exact
local/remote HEAD and clean status after push. No implementation work remains
for this foundation. Evidence is outside Git at
`D:\Astraeon\backbone-verification\monster-box`.

## Files

Added (9):

- `box-content-tables.js`
- `monster-box.js`
- `monster-box-runtime.js`
- `tests/monster-box.test.cjs`
- `tests/monster_box_browser.py`
- `tools/monster-box.html`
- `tools/monster-box-harness.js`
- `docs/CORE_SPINE_MONSTER_BOX.md`
- `docs/CORE_SPINE_MONSTER_BOX_REPORT.md`

Modified (20):

- `item-definitions.js`, `item-state.js`, `player-state.js`
- `drop-tables.js`, `monster-definitions.js`, `game.js`
- `boot.js`, `index.html`, `sw.js`
- `tools/combat.html`, `tools/inventory.html`, `tools/progression.html`,
  `tools/monster-loot.html`, `tools/monster-lifecycle.html`
- `README.md`, `ARCHITECTURE.md`
- `docs/CORE_SPINE_ITEMS.md`, `docs/CORE_SPINE_ACTION_ITEMS.md`,
  `docs/CORE_SPINE_MONSTER_LOOT.md`, `docs/CORE_SPINE_MONSTER_LIFECYCLE.md`

## Architecture / acceptance contract

Full specification: [CORE_SPINE_MONSTER_BOX.md](CORE_SPINE_MONSTER_BOX.md).

| Requested boundary | Implemented contract |
| --- | --- |
| Monster Box ItemDefinition | One immutable `monster-box-proof`, kind monsterBox, stackable, openable reference to `box-proof-basic`; no effect/rank/cooldown/runtime fields |
| Canonical ownership | Existing definition-ID stack; no Box ItemInstance or second inventory |
| Box Content Table | Separate immutable registry; ordered guaranteed entries plus one weighted choice set and integer quantity ranges |
| Monster Drop separation | Separate meaning, tables, RNG event and runtime authority; no death/life/Loot ticket in opening |
| Authored validation | Whole table/source/count/metadata validation before entropy or mutation; structured failures; unsupported grammar rejects |
| RNG | Injected next() in pure resolver; finite [0,1); authored ordering; outer production provider only |
| Anti-roll-shopping | Prepare reveals no roll; commit rolls once. Maximum package envelope checks supported deterministic failures before RNG, including after reload. Private failed post-roll outcome is retained in the same runtime and never returned as selectable contents |
| Prepare/commit | Non-mutating ownership/context eligibility; exact owned ticket; revalidate then contained synchronous debit/reward publication |
| Authorization integrity | WeakMap object ownership plus epoch, inventory identity/revision and content signature; copied/forged/foreign/stale/duplicate reject before another roll |
| Single open | Exactly one logical Box, exact source debit and exact canonical contents; ticket unusable after success |
| Bulk open | N logical rolls in continuous sequence, stable evidence, stack aggregation and distinct equipment; exact N debit |
| Bulk atomicity | Pure candidate source debit and complete reward plan; nested canonical mutation lock; single inventory publication only after all acceptance checks |
| Stack rewards | Existing canonical addStack; exact quantities and compatibility mirrors; no serial allocation |
| Equipment rewards | Existing createInstance and stable item-N; exact serial advance; no auto-equip; Equipment → Stats → Combat unchanged |
| Currency decision | Omitted; reuse item planner only. No parallel gold state or kill adapters |
| EXP / Job EXP | Opening grants neither; no Skill Points, learned ranks or action slot changes |
| Quest credit | Opening grants no kill/quest credit or monster entitlement |
| Monster Loot integration | Isolated `proof-monster-box` death reward grants ordinary unopened Box x1; production tables/RNG/rewards unchanged |
| Monster Lifecycle relationship | No lifecycle module/state/cadence/respawn edits; responsibility still ends at existing Loot |
| Action Item relationship | Separate inventory/openableItem source. Potion contents use normal Action Item; healing clocks neither block nor change on Box open |
| Inventory / Bag | Existing card/button single-open adapter; no production bulk modal or new reward reveal UI |
| Save/reload | Version 5 unchanged. Unopened stack, committed contents/instances and next serial persist; tickets/revision/RNG/pending requests are transient. Old runtime tickets reject; no automatic replay/refund/open |
| Player death/respawn | Existing lifecycle invalidation clears tickets; committed source debit/content ownership stays intact |
| Town/field/travel | Ordinary alive inventory menus permitted in town/field/dungeon; loading blocks and immediately invalidates Box tickets. Travel changes no Box ownership or content |
| Future capacity | Pre-roll envelope and exact package acceptance hooks; structured rejection before source publication; no overflow/mailbox/weight policy |
| Developer tooling | Isolated page with fixed RNG, add/prepare/single/bulk/commit/duplicate/stale/serial/save/reload; exact dev=1 bounded live API, normal URL has no Box mutation global |

## Provisional proof data

- Monster Box proof definition: `monster-box-proof`, neutral display name
  `Monster Box (proof)`, one canonical stack, weight unconfigured/0.
- Box Content proof table: only `box-proof-basic`.
- Relative weights 1/1/1 select existing Herb x2–3, Potion x1 or Astral Blade x1.
  Material quantity range consumes its own subsequent draw.
- Isolated Monster Drop proof: guaranteed Box x1. No production field table
  receives a Box entry, and a monster award never opens it.
- Technical processing guards: 256 entries, JSON depth 64, 10,000 opens and the
  existing 10,000 non-stack reward-unit bound. These are not final UI or capacity.
- All probabilities, quantities, labels and fixture coefficients are NON-FINAL,
  authored/config-driven and replaceable. No rarity, catalogue, economy, paid
  box, pity, key/chest, affix or recursive auto-opening design is approved.
- Valid nonempty tables always yield a reward; empty/no-reward Box tables reject.
  Valid no-drop Monster Loot remains unaffected.

## Deterministic verification

`python tools/run-node-checks.py` with the actual Node executable passed
**1010 checks / 0 failures** in 19 files, repeated before final publication.
Evidence: `node-final/report.json` and `node-prepush/report.json`.

- New deterministic tests: **150** in `tests/monster-box.test.cjs`.
- Previous tests retained: **859** historical checks; all 18 previous Node files
  are unchanged. Their authored-table loop also validates the one new isolated
  Drop Table, adding one check without changing an old assertion (Loot 165).
- Coverage: immutable separate definitions, malformed authored data/counts/RNG,
  exact choice/quantity sequencing, pure resolution, non-rolling prepare,
  stack/instance serial safety, single/bulk equivalence, duplicate/copied/foreign/
  stale tickets, nested transaction rejection, entire-batch failures, pre-roll
  envelopes, hidden post-roll retry retention, no kill/action semantics, Loot
  unopened award, Lifecycle independence, Potion/Equipment/Stats/Combat bridges,
  v1–5 migration/future-save guard and 20 save/normalize/load cycles.
- Source audit: all 18 prior Node and 10 prior browser/cache source files unchanged;
  no protected world/art path or stable core source changes. The additional
  historical world visual browser itinerary was not part of this functional gate.
- Authored-data audit: all 14 previous ItemDefinitions, 8 previous Drop Tables
  and 16 previous monster reward definitions remain semantically identical.
  Evidence: `source-audit.json`, `authored-data-audit.json`.
- Initial new test driver had a syntax typo and then two wrong fixture requests:
  Combat needs explicit physical damageType; Lifecycle needs canRespawn policy.
  Corrected new requests and required valid Combat output; no prior assertion or
  runtime contract was weakened. Initial evidence `focused-initial.log` retained.
- World validator passed Terrain, Navigation, TownObject and AnimationManifest
  schemas. Evidence: `world-validation.log`. World files are unchanged.

## Browser acceptance / local smoke

Final focused Box suite passed **33 groups / 0 failures**, no console/page/runtime
or HTTP errors, no bounded encounter retries. Swordsman and Mage both exercise
actual Bag single-open, mixed deterministic bulk, copied/duplicate/stale guards,
canonical equipment → Stats/Combat, Potion → Action Item, merchant/crafting,
real learned skill/Basic Attack death rewards, same-monster life 2 respawn/death,
actual enemy-caused player death/respawn, ticket invalidation, save/reload and
field/town ownership retention. Isolated harness and ordinary normal-URL character
creation also passed. This is automated live functional smoke, not art acceptance.

All nine functional browser suites passed sequentially: **190 groups / 0 failures**
including **157 previous groups**, with zero captured console/page/runtime/HTTP
errors. Every prior suite and assertion was retained.

| Suite | Groups | Result |
| --- | ---: | --- |
| `tests/monster_box_browser.py` | 33 | PASS |
| `tests/monster_lifecycle_browser.py` | 30 | PASS |
| `tests/monster_loot_browser.py` | 26 | PASS |
| `tests/action_item_browser.py` | 30 | PASS |
| `tests/inventory_browser.py` | 15 | PASS |
| `tests/action_loadout_browser.py` | 17 | PASS |
| `tests/combat_browser.py` | 21 | PASS |
| `tests/skill_tree_browser.py` | 11 | PASS |
| `tests/progression_browser.py` | 7 | PASS |

`tests/cache_resume.py` also passed: `astraeon-static-v92`, **146 cached requests**,
old cache removed, saved character retained, offline town boot/reload,
legacy-town migration, same-layout blocked-save recovery and exact offline
source/ground SHA256 parity. Zero captured page errors. Evidence:
`final-browser/cache_resume/report.json`. Save version remains **5**.

Evidence: `final-browser/<suite>/report.json`, per-suite logs and `runner.json`.
One Mage Loot waypoint timeout triggered the unchanged driver's existing bounded
keyboard approach; subsequent replacement/reward assertions passed. The driver
preserved authoritative state (`navigation:null`, `action:null`) in its evidence.
This is the prior navigation/timing signal, not a demonstrated Box regression.
No combat/navigation/lifecycle rewrite or weakened assertion was introduced.

## Reproduction and final Git checks

Run from this repository with the documented static server on 127.0.0.1:8011.
Commands and all functional browser filenames are in README. This Windows pass
used `D:\Node\node.exe`, the bundled Python at
`C:\Users\Drink beer ai sus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`,
`PYTHONPATH=D:\Astraeon\backbone-verification\python` and
`ASTRAEON_BROWSER=C:\Program Files\Google\Chrome\Application\chrome.exe`.

```powershell
python tools/run-node-checks.py --node D:\Node\node.exe --output D:\Astraeon\backbone-verification\monster-box\repeat-node
python tests/monster_box_browser.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-box\repeat-browser
# Run all eight prior functional browser suites in the table, then:
python tests/cache_resume.py --url http://127.0.0.1:8011 --output D:\Astraeon\backbone-verification\monster-box\repeat-cache
python tools/validate-world-v3.py
git diff --check
git status --short
git log --oneline -12
```

Final diff inspection covers all 29 changed paths: 9 additions and 20 modified
files. Protected paths and historical reports are untouched; source data and
previous assertions are retained. Final status is expected clean after the
report-only commit; exact final status/log and remote match are returned in the
chat handoff. No art/visual, physical-device-performance or full-patch acceptance
is claimed.

## Known limitations / next integration

- Local integrity under trusted synchronous providers/adapters, not server or
  browser-script/storage security. Arbitrary external callback side effects are
  not rollback-capable. Canonical nested mutations are blocked.
- The maximum envelope is deliberately conservative: an opening may reject if
  any supported possible outcome exceeds technical bounds, even if a different
  outcome would fit. It uses no speculative equipment allocation.
- Current production has no outcome-sensitive late capacity rejection. A custom
  post-roll rejection retains one hidden outcome only in the same runtime;
  pending outcomes are not saved. Future capacity must use pre-roll envelope
  acceptance or establish a durable pending-outcome policy before enabling
  outcome-sensitive rejection across reload. Stock deterministic failures already
  reject before entropy. Invalid RNG/provider attempts remain pending/failed in
  that runtime; no free abandon/reroll API is provided.
- Only one Box/content fixture and a small guaranteed/weighted grammar. No final
  catalogue, balance, progression/quest/currency contents, capacity, overflow,
  production bulk selector, animation or reward reveal.
- Existing transient monster/AI reload and targeting/navigation limits remain as
  documented by Lifecycle. Box does not persist or redesign them.

Potential merge conflicts: Item State/Player adapter APIs, game Bag/loading/dev/QA
sections, definition registries, boot/index/SW versions, developer HTML imports
and current architecture docs if later branches edit the same areas.

Files intentionally untouched: `authoring/**`, `RO3 Ref/**`, `assets/**`,
`world/**`, Blender, renderer/lighting/geometry/camera, sprite/atlas/animation art,
motion/VFX, `style.css`, visual evidence and historical verification reports;
Progression/Stats/Skill, Action Loadout/Runtime, Action Item/Runtime, Combat
Resolution/Runtime, Item Inventory/Equipment, Loot core, Lifecycle core,
Monster Combat, Exploration and Save core. Existing test assertions remain intact.

Recommended next Backbone task: **Inventory Capacity / Weight foundation**,
using the preflight boundary without replacing Box content resolution. Quest,
Storage and other roadmap foundations remain separate. Do not declare Patch
0.0.1 or Core Spine complete.
