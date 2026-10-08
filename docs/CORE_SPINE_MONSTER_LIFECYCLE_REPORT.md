# Monster Lifecycle / AI foundation — verification handoff

## Git checkpoints and scope

- Branch: `backbone/monster-lifecycle-0.0.1`.
- Starting parent branch: `backbone/monster-loot-0.0.1`.
- Starting parent HEAD: `104a817e756463b3979133e3df4057cacba5303f`.
- Runtime/test checkpoint: `535a1b114c145deee7de65573fb7ec1a8fcf48ab`.
- Final HEAD: documentation successor, printed with status/log in the chat
  handoff. This document cannot embed its own commit hash. Runtime/test changes
  after the checkpoint must be recorded before claiming verification.
- Parent was fetched, switched and pulled with `--ff-only`; clean working tree
  verified before creating the requested branch. Remote HEAD was authoritative.
- Twelve focused implementation/test commits separate immutable definitions,
  deterministic intents/combat dispatch, game/death/respawn integration,
  tests/tooling, HP-zero/time guards, contact-range closure and robust live targeting acceptance. Documentation follows.
- Only the requested branch is pushed. No merge, force push, history rewrite or PR.

This implements **only Monster Lifecycle / AI foundation**. Patch 0.0.1 and Core
Spine are **not complete**. The [contract](CORE_SPINE_MONSTER_LIFECYCLE.md) records
the detailed APIs, coefficients and trust boundaries.

## Files added

- `monster-lifecycle-definitions.js`, `monster-lifecycle.js`,
  `monster-combat-runtime.js`.
- `tests/monster-lifecycle.test.cjs`, `tests/monster_lifecycle_browser.py`.
- `tools/monster-lifecycle.html`, `tools/monster-lifecycle-harness.js`.
- `docs/CORE_SPINE_MONSTER_LIFECYCLE.md`,
  `docs/CORE_SPINE_MONSTER_LIFECYCLE_REPORT.md`.

## Files modified

- `game.js`: contained actor registration, lifecycle intent dispatch through
  existing navigation/EnemyCombat, shared incoming Combat, one death/Loot handoff,
  same-instance field respawn, immediate player-death/loading lease invalidation,
  bounded replacement population and exact dev=1 inspection.
- `boot.js`, `index.html`, `sw.js`: three modules loaded/precache; version 91.
  Five unchanged Loot v90 responses also actually precached for its old explicit
  cache assertion. No duplicate script execution.
- `tools/combat.html`, `tools/inventory.html`, `tools/monster-loot.html`,
  `tools/progression.html`: current module cache queries only.
- `tests/monster_loot_browser.py`: replacement-under-test identity is preferred
  during ordinary input targeting; stalled offscreen ground waypoints capture
  authority state and use bounded ordinary keyboard input. All prior movement,
  kill-count and reward assertions stay.
- `README.md`, `ARCHITECTURE.md`: current authority/commands/cache.
- Current Progression, Skill Tree, Combat, Action Loadout, Items, Action Items
  and Monster Loot contract docs: current cache, contained incoming Plate/guard
  adapter and Lifecycle extension. Historical verification reports untouched.

## Architecture and behavior

| Requested boundary | Implemented contract |
| --- | --- |
| MonsterDefinition architecture | Frozen authored mechanical profiles with existing reward-definition reference; validation returns structured failures |
| Spawn identity | Authored/supplied unique active spawn ID and immutable home; distinct from definition ID |
| Runtime instance identity | Existing Loot `monster-N` registration; same actor/ID across per-life respawn |
| Life generation | Existing Loot generation increments only on valid new life; old claim/token cannot authorize it |
| Lifecycle states | SPAWN, IDLE, DETECT, AGGRO, CHASE, ATTACK, LEASH, RETURN, DEAD, RESPAWN_WAIT |
| Transition model | Declared legal edges; immutable reason/time/from/to/runtime/spawn/life events; bounded diagnostics |
| Clock/time | Caller-supplied finite monotonic simulation seconds; menu/loading/hidden/hit-stop freeze existing game timeline |
| Perception | Alive finite target, active combat context, inclusive detection and home leash |
| Target acquisition | Explicit DETECT/AGGRO acquisition events; single eligible player target |
| Target release | Invalid/dead/disappeared/replaced target, home leash, loading, death or retirement invalidates ownership |
| Chase/movement | Immutable chase/home movement intents; existing collision/A* adapter executes movement |
| Attack intent | Private owned token and exact-once impact consumption; copied/foreign/stale tokens rejected |
| Cadence | Explicit readiness/windup/impact/cadence, independent of sprite frames; no catch-up burst |
| Combat integration | Existing EnemyCombat geometry → staged Combat resolver → canonical Player HP setter |
| Leash | Both actor and target distance from home; clears offense before RETURN |
| Return | Home movement, no re-aggro until returned to IDLE; no alive teleport |
| HP return/reset | Retain HP, matching absence of old return healing; full restore only at legitimate respawn |
| Authoritative death | HP zero blocks attacks immediately and generates one DEAD/death event per life |
| Monster Loot | Existing prepare/commit once; no new tables/RNG/claims/inventory/progression formulas |
| Dead behavior | No movement, perception, target, contact or second reward; presentation observes state |
| Respawn wait | Explicit next-step DEAD→RESPAWN_WAIT; death time + authored delay |
| Respawn/new life | Restore HP/home, existing Loot.newLife, clear old target/cadence/death/claim, SPAWN→IDLE |
| Multiple monsters | Independent actor HP/private target/timing/death/entitlement/respawn, including same-definition actors |
| Player death | Immediate all-target release and attack lease cancellation; existing town respawn and 8-gold loss |
| Town/field/travel | Hostile AI suppressed in town; loading cancels leases before await; successful travel retires population |
| Save/reload | Unchanged version 5; committed player rewards persist; transient AI/death/attack state rebuilds without replay |
| Animation/presentation | Existing plans/transforms observe lifecycle/attack events; no new art/frame authority |
| Developer tooling | Isolated in-memory fixture/time/target/damage/death/loot/respawn harness; exact dev=1 live inspector |

Incoming integration intentionally activates derived DEF. Warden Plate's DEF
enters once; the historical extra flat subtraction is removed. Guard uses the
existing configured .7 reduction in the resolver's defense→mitigation order.
Results can differ from old guard-before-plate damage; no final balance approval
is implied. Existing invulnerability/hurt/death presentation is retained.

## Provisional fixtures and data

Three normal definitions: `lifecycle-normal-a`, `lifecycle-normal-b`,
`lifecycle-normal-c`. Tougher fixture: `lifecycle-tough-a`.

| Fixture | HP | Speed | Detect / attack | Windup / cadence | Respawn |
| --- | ---: | ---: | --- | --- | ---: |
| normal-a | 20 | 1 | 6 / 1.5 | .5 / 2 | 4 |
| normal-b | 24 | 1.2 | 7 / 1.8 | .6 / 2.4 | 5 |
| normal-c | 28 | .8 | 5 / 2 | .7 / 2.8 | 6 |
| tough-a | 60 | .7 | 8 / 2.2 | .9 / 3 | 8 |

Common authored provisional leash 12, home tolerance .15, initial delay 1.8.
Production retains existing HP coefficients, species speeds/detection 8,
ordinary cadence 2.8 and guardian cadence 2.4. Initial random attack jitter is
replaced by explicit readiness. Field respawn delay 12 is provisional.
Melee stationary attack bands reuse old chase reach 1.4/1.5/2.2/1.6; guardian
uses old close reach 3.5. Charge/projectile/field bands retain their prototype
values. These ensure contact geometry is reachable, not final encounter balance.
Bounded coexistence with old replacement identities: initial 7, max 8 entries/
alive, refill below 7 at the existing 12-second gate. These are replaceable data,
**not final spawn density**. No special-case AI code is needed for the four proof
definitions. Existing names, art and guardian compatibility behavior are not
approval of final monster design. No new loot balance/economy values.

## Deterministic verification

Command: `python tools/run-node-checks.py` (installed Node 24.14.0).

**859 pass / 0 fail**, across 18 existing/new test files:

| Suite | Assertions |
| --- | ---: |
| New Monster Lifecycle | 147 |
| Existing Monster Loot | 164 |
| Action Item | 90 |
| Item/Inventory/Equipment | 88 |
| Combat Resolution | 86 |
| Action Loadout + Action Runtime | 37 + 56 |
| Skill Tree | 45 |
| Progression + Save + Stats | 10 + 13 + 14 |
| Existing world/motion/compatibility suites | 109 |

All **712 prior assertions retained**, with no prior Node test file edits. New tests
cover definition validation/immutability, identities, transitions, target/range/
cadence, copied/foreign intent rejection, explicit pause/time failures, home
leash/return HP, immediate HP-zero delivery rejection, death/Loot exactly once,
respawn and second-life rewards, multi-actor independence, four generic profiles,
shared incoming resolver/gear/guard/HP, player death/travel/loading, update
partitioning, no catch-up burst, bounded population, save versions/migrations and
boot/cache/source boundaries. Existing suites retain ownership/Stats/Combat and
Action Item proof.
An independent source audit verifies all 17 previous Node files unchanged and
all 37 original Loot browser assert expressions identical; only driver targeting/
approach changes. Evidence: `retained-assertions.json`.

## Browser acceptance and local smoke

Latest focused suite: **30 groups pass**, disposable Swordsman and Mage, normal
boot plus isolated harness. Console/page/runtime/HTTP errors: **0**.

The live encounters use ordinary actor selection and held Basic Attack, not
fake death damage. Controlled safe dev player placement tests detection/chase/
leash positions. The player remains stationary after detection so actual chase
must reach a hittable attack band. Actual enemy contact reduces Player HP through shared
Combat. Each class verifies return/HP retention, first death/reward exactly once,
duplicate rejection, paused wait, stable-instance/spawn life 2, real learned
skill contact plus Basic Attack second death, canonical equipment retained,
Action Item use, actual player death/all-target release, town respawn, canonical
save/reload and field/town travel without stale attack or reward replay.

| Browser suite | Final result |
| --- | --- |
| Monster Lifecycle | 30 groups pass |
| Monster Loot | 26 groups pass |
| Action Item | 30 groups pass |
| Inventory/Equipment | 15 groups pass |
| Action Loadout | 17 groups pass |
| Combat | 21 groups pass |
| Skill Tree | 11 groups pass |
| Progression | 7 groups pass |
| Cache/resume | v91 migration, 143 precached responses, offline saved-character reload pass |

All **157 browser acceptance groups pass**, with zero console/page/runtime/HTTP
errors in the final runs, plus passing cache/resume checks. World validator passed
Terrain, Navigation, TownObject and AnimationManifest schemas. `git diff --check`
passes. Local smoke is automated live Playwright gameplay with disposable
Swordsman/Mage characters, not a manual art or animation review.

Evidence lives outside Git in
`D:\Astraeon\backbone-verification\monster-lifecycle`: `node/report.json`,
`browser/report.json`, prior-suite reports, `final-verification.json` and preserved
initial failure evidence. The final Node run was repeated at the recorded
runtime/test checkpoint. Browser runs share that runtime; the final Loot run also
includes the recorded driver fixes. Later changes are documentation only.
No generated gameplay saves/screenshots/art are committed.

## Failure evidence and timing observations

- Initial unchanged Monster Loot browser reached its real kill/reward assertions
  but waited for a replacement identity. Per-life respawn had suppressed that
  compatibility path. Bounded coexistence restores replacement identities.
- Initial new browser then exposed a genuine alive-budget starvation: a new
  replacement filled the old seven-alive cap and blocked the original actor's
  respawn. Authored max entries/alive now both eight; a deterministic regression
  proves a dead slot always has budget when all other registered entries live.
- New browser driver initially treated `getEquipped`'s canonical string return
  as an object. Corrected only the new driver; no runtime/old assertion change.
- All behavior groups then passed but the new isolated harness requested absent
  `/favicon.ico`. Reproduction identified the exact URL; the page now links the
  existing `icon.svg`. The successful rerun keeps the zero-console-error gate.
- Latest focused suite recorded **zero bounded Basic Attack retries**. Historical
  live-targeting variability remains a signal, not a reason to weaken assertions
  or rewrite Combat. Final Monster Loot acceptance recorded ten ordinary
  intermediate ground waypoints and two bounded keyboard approach fallbacks
  (one per class). It recorded no bounded Basic Attack retarget; all 26 groups
  pass. The movement timeout evidence is described below.
- Review added an immediate authoritative HP-zero delivery guard, including the
  interval before the caller has notified death. The new deterministic assertion
  rejects both contact authorization and impact consumption without granting
  reward; the later valid death notification still hands off once.
- The first unchanged Action Item run passed Swordsman and Mage item/kill checks,
  then timed out waiting for Mage player death. Review found a genuine stationary
  ATTACK dead band: some old launch thresholds exceeded existing contact shapes.
  Added geometry regressions reproduced four unreachable thresholds (three
  ordinary profiles and guardian sweep). Mechanical data now uses old melee
  chase/guardian close reach; existing geometry/formulas and old assertions stay
  intact. Focused browser acceptance is strengthened to require chase reaching
  contact with a stationary player. The incomplete inventory run was stopped;
  the complete previous browser sequence is rerun from the corrected checkpoint.
- After that contact fix, the old Loot driver killed three nearer respawned lives
  and then waited for a replacement death it had never targeted. This was a driver
  assumption, not duplicate/missing loot. Its target selection now prioritizes
  the replacement identity under test. The same three real kills and every old
  reward/identity assertion remain, with ordinary gameplay input and bounded waits.
- A later Loot rerun stopped at its 15-second offscreen ground-waypoint movement
  wait, before attacking the replacement. The final driver records position/HP,
  navigation, action, window and click coordinates on that timeout, then uses
  ordinary keyboard input toward the actor with the identical displacement wait.
  Both classes recorded one such timeout with no active navigation/action/menu
  and an alive player. The fallback reached the replacement and its original
  real-kill/reward assertions passed. Click overlap remains an inference, not a
  confirmed navigation bug or a reason to rewrite navigation. Initial failure
  evidence is preserved as `loot-offscreen-waypoint-initial-failure.json/.log`.

## Known limitations and future work

- Local trusted actor/catalog/publisher integrity, not server/network authority.
  Existing Loot transaction/trust boundary is unchanged. Failed reward handoff
  is inspectable and does not automatically reroll or replay progression.
- One target; no threat tables, party AI, complex perception, navigation rewrite,
  full authored monster stat sheet, final status/monster skill framework or new boss phases. Existing guardian
  phase/add presentation remains a compatibility consumer. Its generic lifecycle
  windup/cadence replaces historical phase-specific interruption/recovery timing;
  final boss behavior and a full live dungeon/boss acceptance pass are not claimed.
- Existing navigation can block a return path. No teleport/pathfinding escape
  subsystem is introduced. LOS remains minimal contact-path eligibility.
- Delayed updates emit at most one attack; sampling partition may shift observed
  deadlines, with no catch-up burst or duplicate impact/death. This is not a
  frame-exact replay engine.
- Active enemy AI/lives and dungeon state do not persist. Reload creates fresh
  populations without replaying committed deaths. Durable encounters remain
  future work, with committed player ownership preserved by existing save.
- Population and all new timing/range/fixture coefficients remain provisional.
  No final names, monster catalogue, stats, aggro, leash, respawn or density are
  approved. No visual-animation/art acceptance claim.

Potential merge conflicts: `game.js` factory/update/death/dev blocks, boot/page/
service-worker version, developer HTML queries and current architecture/contracts
if later branches edit these same sections. Stable foundation core modules and
historical reports were not broadly rewritten.

Files intentionally untouched: `authoring/**`, `RO3 Ref/**`, `assets/**`,
`world/**`, Blender, renderer/lighting/geometry, sprites/atlases/animation art,
VFX/camera, `style.css`, visual evidence; Progression/Stats/Skill/Action/Item core,
Monster Loot core and `save-state.js`. Existing browser/Node assertions retained; Loot driver targeting adapted.

Recommended next Backbone task: **Monster Box item/opening foundation**, separate
box-content table with existing canonical item ownership. Capacity/weight, Quest,
Storage and other roadmap systems remain separate. This handoff does not declare
Patch 0.0.1 or Core Spine complete.
