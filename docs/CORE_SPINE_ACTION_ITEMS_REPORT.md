# Action Item / Consumable Execution foundation — verification handoff

## Git checkpoints and scope

- Branch: `backbone/action-item-0.0.1`.
- Starting parent branch: `backbone/item-inventory-equipment-0.0.1`.
- Starting parent HEAD: `51ec24cf494f599022372596c8844aad2514dfd2`.
- Runtime/test checkpoint: `a34b7f68d271800ccc83fb6f9ac6d6ba8e2b9d99`.
- Final HEAD: the documentation successor of this checkpoint, printed with final
  status/log in the chat handoff. This report cannot contain its own commit hash.
  No runtime/test changes follow the checkpoint.
- Parent was fetched, switched and pulled with `--ff-only`; working tree was clean
  before creating the requested branch from authoritative remote parent HEAD.
- Five focused implementation commits separate contracts/effects, runtime/atomic
  adapters/cache dependencies, gameplay integration, deterministic tests and
  developer/browser tooling. Documentation is a separate final commit.
- Only the requested branch is pushed. No merge, force push, history rewrite or PR.

This implements only the Action Item / Consumable Execution foundation.
**Patch 0.0.1 and Core Spine remain incomplete.** Final catalogue, hotbar, item
balance, status/utility effects and other roadmap systems remain open.

## Files added

- `action-item-config.js`, `item-effects.js`, `action-item.js`,
  `action-item-runtime.js`.
- `tests/action-item.test.cjs`, `tests/action_item_browser.py`.
- `docs/CORE_SPINE_ACTION_ITEMS.md`, `docs/CORE_SPINE_ACTION_ITEMS_REPORT.md`.

## Files modified

- `item-definitions.js`: only the existing two consumables gain authored action
  metadata; all existing numbers/catalogue retained.
- `character-state.js`: atomic current-resource pair setter.
- `item-state.js`: private effect/debit publication callback and nested transaction
  guard; existing canonical inventory remains the only ownership authority.
- `player-state.js`: contained item runtime attachment, compatible use alias and
  combined ticket invalidation at existing lifecycle boundaries.
- `game.js`: explicit gameplay context provider, Potion request and live developer
  API adapter. Existing Bag path now delegates through Player's shared use alias.
- `boot.js`, `index.html`, `sw.js`: imports/precache and aligned cache version 89.
- `tools/inventory.html`, `tools/inventory-harness.js`: isolated item execution
  inspection and deterministic time controls.
- `tools/progression.html`, `tools/combat.html`: aligned module dependencies/cache.
- `tests/action-loadout.test.cjs`, `tests/action-runtime.test.cjs`,
  `tests/combat-resolution.test.cjs`, `tests/compatibility-hardening.test.cjs`,
  `tests/item-inventory-equipment.test.cjs`, `tests/motion.test.cjs`,
  `tests/save-progression.test.cjs`, `tests/skill-tree.test.cjs`: only add new module
  imports; all existing assertions retained.
- `tests/cache_resume.py`: assert all four new modules are in version 89 precache.
- `README.md`, `ARCHITECTURE.md`, current `CORE_SPINE_PROGRESSION.md`,
  `CORE_SPINE_SKILL_TREE.md`, `CORE_SPINE_COMBAT.md`,
  `CORE_SPINE_ACTION_LOADOUT.md`, `CORE_SPINE_ITEMS.md`: current contracts/cache and
  Action Item links. Historical verification reports remain historical.

## Architecture and behavior

| Area | Implemented contract |
| --- | --- |
| Action Item architecture | Distinct `source:'actionItem'`; definition, ownership, effect preview, eligibility, clocks and presentation remain separate |
| Definition contract | Frozen descriptor with ID, kind, self target, typed effects, item/group duration, usable states, tags and provisional metadata; no timestamps |
| Authored effect validation | Current HP/SP positive finite effects only; malformed, missing, unknown, unsupported target, NaN/Infinity/negative/overflow reject before mutation |
| Eligibility model | Canonical positive ownership, actor/resources/alive state, loading/menu/generic hook, authored zone, useful effect and ready clocks |
| Prepare/commit boundary | Immutable inspectable package owned by a private WeakMap; revalidate inventory identity, revision, effect/resource signature and time; duplicate/stale/copied/foreign/forged reject |
| Cooldown architecture | Private item-ID map, function-group map and optional global item hook; maximum ready time; publish after successful transaction only |
| Shared cooldown groups | Production `hp-potion` / `sp-potion`; same-function sibling ID fixture cannot bypass group; unrelated functions independent |
| Clock/time model | Explicit nonnegative monotonic simulation seconds; exact expiry; no core wall clock; menus/loading/hidden simulation pauses pause cooldown |
| Effect application | Pure dispatcher preview followed by Character's validated pair setter; clamp to existing maxima; no derived-stat writes |
| Inventory debit | Existing canonical stack transaction consumes exactly one; nested mutation rejects; no second inventory or ItemInstance allocation |
| HP/SP integration | Existing Potion +45 HP / Ration +20 SP retained; maxima/equipment/serial/Stats unchanged |
| Full-resource policy | Reject `FULL_RESOURCES` without consumption or clocks; tested for both resources; useful mixed-effect fixture consumes once |
| Action-state restrictions | Dead/loading/restricted reject; existing active Timeline permitted; Q/button menu input blocked; intentional Bag menu use allowed; future pure synchronous restriction hook |
| Input integration | Existing Q and Potion button request new runtime; Bag Potion/Ration use the same core through compatibility alias |
| Action Loadout relationship | Eight learned slots, Skill Points/ranks/prerequisites and Basic Attack remain independent; skill clocks never share item groups |
| Death/respawn behavior | Remaining canonical quantities/gear retained with no refund/free item; retain timestamps on same timeline; invalidate outstanding tickets |
| Town/field behavior | Ownership unchanged across both travel directions; retain timestamps; existing travel/dungeon lifecycle invalidates tickets |
| Save/reload behavior | Save contains canonical remaining ownership; no item clocks/tickets; reload attaches fresh clocks and time floor zero; no offline timer |
| Returning-save compatibility | Deliberately keep save version 5; canonical precedence and pre-v5 migrations unchanged; no free consumables; >5 future-save guard retained |
| Developer tooling | Isolated add/use/prepare/commit, low/full resources, descriptor/effects/eligibility/results, exact time advance and clock reset; live mutations gated by exact dev=1 |

See [the full contract](CORE_SPINE_ACTION_ITEMS.md) for API/error details and trust
boundaries. `useConsumable` uses explicit context, injected game/harness provider,
or deterministic time-zero compatibility fallback for historical isolated callers.
Camp cooking and shrine offering keep separate gameplay effects/cost semantics
while debiting canonical Ration/Herb. They are not direct consumable execution.

## Provisional coefficients and explicitly non-final decisions

The only new numeric defaults are configured **2-second item cooldown**,
**2-second HP group**, **2-second SP group**, and **0-second global hook**.
These are executable proof, not final cooldown approval or balance. Existing
+45 HP/+20 SP content is not retuned. No new production consumable ID is added.
No final potion sickness, combat lock, item animation, item slot count, hotbar,
PvP/boss restrictions, rarity or consumable economy is decided here.

## Verification environment and commands

Windows checkout `D:\Astraeon\astraeon`; Node v24.14.0, bundled Python 3.12.14,
Python Playwright/jsonschema, local Chrome with ANGLE D3D11, disposable contexts
and saves. Static server uses port 8011. Reports are outside Git in
`D:\Astraeon\backbone-verification\action-items`.

```powershell
python -m http.server 8011 --bind 127.0.0.1
python tools/run-node-checks.py
python tests/action_item_browser.py --url http://127.0.0.1:8011
python tests/inventory_browser.py --url http://127.0.0.1:8011
python tests/action_loadout_browser.py --url http://127.0.0.1:8011
python tests/combat_browser.py --url http://127.0.0.1:8011
python tests/skill_tree_browser.py --url http://127.0.0.1:8011
python tests/progression_browser.py --url http://127.0.0.1:8011
python tests/cache_resume.py --url http://127.0.0.1:8011
python tools/validate-world-v3.py
git diff --check
```

This host's normal Python is a Store alias; commands used the bundled absolute
executable, external dependency PYTHONPATH and ASTRAEON_BROWSER override. Browser
suites run sequentially to keep the local static server's connection backlog
bounded. They do not alter the user's ordinary browser or save.

### Deterministic checks

| Suite | Pass / fail |
| --- | --- |
| New Action Item | 90 / 0 |
| Item / Inventory / Equipment | 88 / 0 |
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
| **Total** | **548 / 0** |

All **458 previous checks retained**, plus 90 new. New checks cover the requested
execution, ownership, resource, cooldown, lifecycle and save policies, including
same-count inventory ABA, two tickets at zero cooldown, foreign/copy authorization,
shared-group ID switching, global-hook separation, reentrant callbacks, pair-setter
failure, effect/clock overflow, future restrictions and twenty save/load cycles.

### Browser acceptance and local smoke

| Suite | Final checkpoint result |
| --- | --- |
| `action_item_browser.py` | 30 groups passed |
| `inventory_browser.py` | 15 groups passed on unchanged rerun |
| `action_loadout_browser.py` | 17 groups passed |
| `combat_browser.py` | 21 groups passed |
| `skill_tree_browser.py` | 11 groups passed |
| `progression_browser.py` | 7 groups passed |
| `cache_resume.py` | Old cache removed; all four new modules precached in v89; offline saved-character boot and byte-identical world/ground checks passed |
| `validate-world-v3.py` | Terrain, Navigation, TownObject and AnimationManifest schemas passed |
| `git diff --check` | Passed |

Final accepted browser total is **101 groups passed**, including all 71 previous
groups, plus cache/offline acceptance and world-schema validation. All final
browser reports contain zero reported console/page/runtime/HTTP errors; cache
reports zero page errors. Deterministic Node total is **548 passed, 0 failed**.
The separate initial live-targeting timeout is retained and described below.

The new suite exercises both Swordsman and Mage from ordinary creation, current
craft/merchant/gear APIs, Q/Potion pointer and Ration Bag execution, repeated input,
full resources, non-mutating prepare and duplicate commit. Native learned slot 1
and developer slot 8 retain rank/Node contacts; derived equipment ATK reaches live
Combat Resolution and produces greater damage than the fixture without the weapon
bonus. Actual Basic Attack kills retain canonical material loot, Base/Job EXP,
gold and quest credit. Both town/field directions, actual enemy death/respawn,
stale ticket rejection and repeated reloads retain remaining ownership and follow
the documented clock policy. A pre-v5 playable save and the isolated deterministic
harness remain usable; ordinary URLs have no developer mutation globals.

During test construction, the throwing restriction fixture incorrectly evaluated
the hook outside the runtime; its expected code is now authored separately.
Browser assertions were corrected to set low SP after opening the paused Bag
(excluding live regeneration) and to dispatch the original key 1 input after
moving a skill (the button's disabled presentation updates on the next frame).
No gameplay behavior was changed to accommodate these test setup mistakes.

The first unchanged inventory browser regression timed out waiting for a Mage
Basic Attack kill, with no console/page/HTTP errors. Its report is retained at
`inventory-browser-initial-failure.json` outside Git. The rerun retains every
original assertion. Live enemy targeting/timing can vary between disposable
sessions; this is recorded separately from deterministic core results.

## Known limitations and potential merge conflicts

- Only current self HP/SP effects execute. Future handlers need explicit authority
  and transaction contracts; no general effect VM/status framework exists.
- Local owned tickets provide execution integrity, not server/network authority.
  Restriction hooks are trusted and side-effect-free. Internal synchronous owner
  callbacks must prevalidate; arbitrary unrelated side effects cannot be rolled
  back. The canonical production callback is contained and not publicly exported.
- Cooldowns reset on reload by deliberate Patch policy; no offline persistence.
  Menu/loading/hidden pauses stop simulation seconds. Time-zero compatibility
  callers must provide advancing context/provider for repeated uses.
- Current UI/keys are retained; no final item hotbar, drag/drop, catalogue, economy
  or balance acceptance. Browser passes are not visual/art/device acceptance.
- Likely concurrent conflict files: `game.js`, `player-state.js`,
  `character-state.js`, `item-state.js`, `item-definitions.js`, boot/page/SW lists,
  developer import lists and current system documentation. Reconcile adapters
  without changing other branches' visual, camera, world or skill contracts.

## Files intentionally untouched

`assets/`, `world/`, `authoring/`, `style.css`, directional/character artwork,
renderer/lighting/terrain/buildings, animation/motion/VFX/camera modules and visual
review evidence. Cache query revisions do not change their bytes. Also untouched:
`item-inventory.js`, `item-equipment.js`, `stats.js`, `progression.js`,
`skill-tree.js`, `combat-resolution.js`, `action-loadout.js`, `action-runtime.js`,
`skill-runtime.js`, `combat-runtime.js`, `save-state.js`, `input.js`,
`exploration.js`, roadmap and historical verification reports. Game movement,
camera math, combat damage/contact formulas and death mechanics are unchanged.

## Recommended next Backbone task

Inspect the roadmap's remaining Core Spine acceptance gaps and implement the
Monster Drop / Loot Resolution foundation: deterministic authored drop candidates,
canonical reward commit and duplicate-claim protection, retaining existing loot
without introducing final economy/content or unrelated UI. Action Item content
and final balance should wait for their own explicit design pass.

Final clean `git status --short`, twelve-entry log, final HEAD and verified remote
tracking parity are printed in the chat handoff after documentation commit/push.
