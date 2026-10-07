# Core Spine foundation completion report — 7 October 2026

Branch: `backbone-design`.
Starting remote HEAD: `c5d1121a837fd13c19f3cc8d99e6dee353b0042c`.
Runtime code checkpoint tested: `b9b5bc7b6082db37ff85122fac4e22b2282218d5`.
The final verification/documentation commit and final Git status are recorded in
the completion message; a committed report cannot contain its own commit hash.

Scope: the progression/stat/save foundation of Patch 0.0.1 only. This does not
complete the whole Core Spine patch. No later patch was implemented.

## Files added

- `progression-config.js`
- `progression.js`
- `stats.js`
- `character-state.js`
- `player-state.js`
- `tools/progression.html`
- `tools/progression-harness.js`
- `tests/progression.test.cjs`
- `tests/stats.test.cjs`
- `tests/save-progression.test.cjs`
- `tests/progression_browser.py`
- `docs/CORE_SPINE_PROGRESSION.md`
- `docs/CORE_SPINE_FOUNDATION_REPORT.md`

## Files modified

- `game.js`: small progression/stat/save adapters and opt-in developer API.
- `save-state.js`: deterministic version 4 migration and serialization.
- `boot.js`, `index.html`, `sw.js`: aligned cache version 84 and new module loading.
- `tests/motion.test.cjs`: shared dependencies and current save-version expectation.
- `tests/cache_resume.py`: progression precache/offline assertions, canvas readiness
  waits and fixture injection after pagehide autosave.
- `README.md`, `ARCHITECTURE.md`: current system/run/compatibility documentation.

## Progression architecture

Frozen data definitions and pure transitions separate Base and Job levels, EXP
and point pools. Multiple level-ups consume exact requirements and grant points
once. Current caps are Base 60 and Job 50; configuration can support Base 110
without an Advanced Job implementation. Curves retain legacy Base EXP pacing.
EXP above cap is discarded, without banking. Validated setters and explicit
developer point additions cannot create repeated rewards through ordinary loads.

## Stat architecture and modifier pipeline

STR/AGI/VIT/INT/DEX/LUK persist in private authoritative state. Positive integer
allocation validates key, balance, cost and cap before mutation; reset refunds
allocated points once. Snapshots are frozen and unrelated gameplay assignments
cannot replace authoritative stats, levels, EXP, points or resource maxima.

The pure calculator combines character base/level, primary stats, equipment,
passives and temporary effects. Flat and percent contributions use one explicit
configuration and documented ordering; future conversion hooks receive frozen
inputs. All required derived outputs plus a dormant physical resilience value
exist. Current ATK/MATK and resource maxima consume the snapshot in gameplay.

## Save migration and legacy compatibility

Version 4 retains the browser key and valid historical world/economy/adventure
fields. Canonical progression and HP/SP fields take precedence. Legacy lv/xp
and hp/maxHp/energy/maxEnergy remain synchronized mirrors/accessors. Historical
capacity offsets and a one-time legacy archive preserve old resource values.
Companion HP is a modifier, so toggling/reloading it does not inflate maxima.

Migration grants no EXP, levels, items or retrospective points. Missing point
pools start at zero. Repeated save/load preserves progression and stats; existing
inventory, gear, quests, discoveries, claims, nodes and historical fields remain.
Runtime temporary effects do not become permanent resource bonuses on reload.
Existing resource costs, regeneration, guard and ability timing remain compatible.

## Developer harness

`http://127.0.0.1:8011/tools/progression.html` displays levels, EXP requirements,
points, all six stats, derived snapshots and raw persistent data. It exposes
EXP, allocation/reset, level/point/resource and save/reload controls using the
same APIs as the playable adapter. It uses an isolated developer save key.
`/?qa=1&dev=1` enables the same mutation API on a disposable playable character.
The normal game URL exposes no developer mutation API. No final UI was designed.

## Verification results

| Check | Result |
| --- | --- |
| New progression tests | 10 passed |
| New stat/modifier tests | 14 passed |
| New save/migration tests | 13 passed |
| Existing expanded town tests | 7 passed |
| Existing Golden pipeline tests | 3 passed |
| Existing locomotion transition tests | 19 passed |
| Existing motion/combat/save/navigation tests | 44 passed |
| Existing painted locomotion tests | 3 passed |
| Existing world v3 tests | 20 passed |
| Total through tools/run-node-checks.py | 133 passed, 0 failed |
| New progression_browser.py acceptance | 7 passed, 0 runtime/HTTP errors |
| Existing cache_resume.py regression | Passed; 114 cached requests, offline reload and both safe-position migration cases |

Local smoke used disposable Chrome contexts and real UI/input for creation,
quest acceptance, movement, town/field transitions, combat and loot. Combat
credited both EXP tracks and the quest. Developer API mutations then survived
save/page reload with identical progression, primary/derived stats, inventory,
equipment, quest, currency and world state. A separate legacy character retained
its capacities, gear, inventory, quest and historical data after migration.
The harness passed spending, invalid-input rejection, repeat resets and reload.

The first browser run identified the harness's missing favicon reference; it
was fixed using the existing icon. Cache regression exposed test startup and
fixture/autosave races. The test now waits for the actual game and inserts its
disposable fixture on the next document; original recovery assertions remain.
All listed final results are from passing runs, with no acceptance thresholds
weakened. These checks make no visual acceptance claim.

This Windows host's `python` command is a Store shortcut. Checks used the bundled
Codex Python runtime, existing Node 24.14.1, Chrome and Playwright 1.58.0 installed
in the verification directory outside the checkout. No runtime build dependency
or package installation was added to the game.

Local evidence is outside the repository under
`D:\Astraeon\backbone-verification`: `node/report.json`, `browser/report.json`,
`cache/report.json`, plus field/harness/offline screenshots. The system contract
documents portable run commands and API details.

## Known limitations

- Balance coefficients and EXP/point rewards are provisional configuration.
- Skill Points are a persistent foundation; no learned skill tree/spending UI.
- HIT/FLEE/CRIT/ASPD/cast/DEF/MDEF/weight are derived data; the complete combat,
  accuracy, mitigation and encumbrance systems remain outstanding.
- Resolve/Mana/Focus retain their existing behavior through the SP compatibility
  alias; separate identity resource mechanics are not introduced.
- Legacy string gear, local saves and existing dungeon lifecycle remain; this
  adds neither online authority nor item instances nor offline dungeon resume.
- Legacy characters with absent pools receive no retrospective points. Legacy
  Base levels above 60 remain preserved, but cannot gain further capped levels.

Potential merge conflicts are concentrated in `game.js`, `save-state.js`, boot/
page/SW cache versions, README/architecture documentation and save/cache tests.
Parallel visual work may touch the same orchestration or cache lines. New pure
modules are separate from world/renderer files. No branch merge or PR was made.

Intentionally untouched: `authoring/**`, `RO3 Ref/**`, `assets/**`, `world/**`,
renderer and lighting/geometry data, character manifests/sprites, animation and
motion modules, `combat.js`, `skill-nodes.js`, `style.css`, visual-review evidence
and the historical visual handoff/status documents. Their visual acceptance
remains the owner's separate work.

Recommended next Backbone task: implement the 0.0.1 Base-class skill-tree minimum
through validated Skill Point spend/refund, prerequisites/ranks, persistent
learned skills and always-active passive modifiers. Continue using the new
private state and modifier pipeline, without adding Advanced Classes or a final UI.
