# Developer Tool Gap Closure - working report

## Git / resume

Branch: `backbone/dev-tool-gap-closure-0.0.1`.
Parent: `backbone/shop-storage-town-services-0.0.1`.
Exact fetched parent HEAD: `5456a6a42adf6e9084caf881b09c97a95ea389f3`.
Fetched, switched, pulled ff-only; parent and new branch were clean.
Actual parent baseline: **1614 Node checks / 0 failures**, 23 suites.
Parent browser evidence: 409 functional groups / 0 failures in verified Town Services report.
Runtime/test and documentation checkpoints: pending.
Evidence root: `D:\Astraeon\backbone-verification\dev-tools`.

## Source audit matrix

| Required tool | Existing implementation / authority | Safe? / gap | Action |
| --- | --- | --- | --- |
| Set Base Level | ProgressionDev -> Player -> Character -> Progression.setLevel | Canonical; errors throw, no coherent receipt | Reuse with validated receipt |
| Set Job Level | Same, setBaseJobLevel | Canonical; same gap | Reuse |
| Add EXP | Player.grantBaseExp / grantJobExp | Canonical point/cap rules | Reuse |
| Give item | ProgressionDev.addStack/createItemInstance; isolated Inventory harness | Canonical capacity/serial | Reuse package acquisition |
| Give money | No validated standalone grant API; plain Player gold publishers | Missing | Narrow safe Player gold helper |
| Learn/reset skill | Player Character SkillTree APIs; exact dev gate | Canonical gates/refunds/loadout reset | Reuse; preserve gates |
| Reset stats | Player Character.resetStats | Paid refund/clamp canonical | Reuse |
| Spawn monster | Normal enemy factory + Lifecycle.register; isolated harness only | Missing real game command | Narrow definition-aware factory adapter |
| Kill target | LifecycleDev.damage -> hit -> Combat.apply -> kill -> Lifecycle; Loot.repeatDeath | Existing canonical path, policy unclear | Explicit real actor kill receipt/policy |
| Teleport map/point | LifecycleDev.placePlayer writes coordinates and centerCamera | Same-map only; target/session reconciliation incomplete | Validated travel/transform adapter; compatibility wrapper |
| Inspect derived stats | Player getters / Character snapshot | Canonical | Reuse, include modifier groups |
| Inspect effects/status | QA active combat/monster statuses; passive getter | Partial, fragmented | Read current supported groups/statuses only |
| Save snapshot | ProgressionDev.snapshot -> Save.snapshot | Canonical | Reuse frozen inspector |
| Wipe test character | No scoped command | Missing | Exact save-key removal; stop runtime, require reload |

Other existing exact-dev globals: Combat, Quest, Lifecycle, Capacity, Box, Loot,
Town Services. They remain compatible. QA exposes inspection only. Existing isolated
harnesses are not sufficient proof for real game commands. Normal game has no
mutation globals; preserve the exact `dev=1` boundary.

Progression lowering refuses negative point pools; no manual EXP/point rewrite.
Skill learn/rank retains class/job/prerequisite/point gates. New commands do not
invent a status system. Kill follows existing hit/Combat HP application and exact
Lifecycle death, including normal Loot/EXP/gold/kill counters and eligible Quest
Kill evidence; duplicate same-life kill rejects. Teleport may bypass grind/gate
cost, but validates map/point/collision and clears transient combat/target/services.
Storage and durable Quest/item state remain unchanged.

## Exact next step

Add one coherent `AstraeonDev` adapter and real-game console with canonical
receipts. Add only narrow Gold/modifier/monster/teleport/wipe owner adapters.
Then deterministic tests, real two-class browser, all inherited suites/cache,
source audit, clean runtime checkpoint, final docs and normal target-only push.
Do not start Integration Gate. This report is not completion evidence.

## Implementation checkpoint

One `AstraeonDev` namespace and real-game framed console now implement the list.
Only exact dev mode loads dev-tools.js. Canonical Gold and modifier inspection
are narrow Player additions. Definition-aware spawn reuses enemy()/Lifecycle;
kill uses hit()/Combat HP application and existing death orchestration. Map/point
teleport validates authored collision, invalidates tickets/services/targets/input,
uses prepareZone and centerCamera/transform. Wipe removes only astraeon-iso-v1,
stops old runtime/save writes and requires reload. Cache advances once to v97.

Focused Node: 79 / 0. Full integration: 1614 retained + 79 new = 1693 / 0.
First focused run had two new-fixture expectations inconsistent with existing
data (Skill Points gate at Job 1; proof-material grants Herb x2); corrected to
actual definitions without runtime balance changes. First new browser run passes
16 Swordsman groups including real Lifecycle spawn/death/Quest credit, then
compares save snapshots while town simulation is running. Snapshot fixture now
opens the existing Character menu before comparing, preserving the exact
Save-authority equality assertion. Raw attempt remains browser-attempt-1.
Full new two-class rerun, all inherited browser/cache and final source audit
remain pending. Do not mark complete or start Integration Gate yet.

## Browser error-gate checkpoint

Second run passes all 40 functional groups across both classes and four normal/
non-exact dev URLs, but correctly fails the final error gate: the new console
page had no icon link and the server log records `/favicon.ico` 404 requests.
Console now references existing `../icon.svg`; no art change or error suppression.
Raw `browser-attempt-2` is retained. Rerun3 must show zero unexpected errors.
All runtime source remains at the 1693-check implementation; final regression
queue/source audit and documentation checkpoint remain pending.

## Integrity edge-case checkpoint

New focused suite is now **86 / 0**. Seven added cases cover primitive registry
identity, spent-point Job lowering, canonical learned/temporary modifier inspection,
invalid snapshot lock recovery, explicit persistence failure and immutable receipts.
The full 1693 integration run predates these seven test-only additions; rerun full
suite before final checkpoint. Browser rerun3 has passed Swordsman through wipe/
reload; remaining class/exposure/error gate and inherited acceptance stay pending.

## Two-class browser milestone

`browser-attempt-3/report.json`: **40 groups / 0 failures**, no unexpected console,
page/runtime or HTTP errors. Both classes run all commands through the real-game
console; normal/QA-only/dev=0/dev=01 expose no mutation module/API. Kill delivers
one existing Lifecycle death, reward and active Quest increment; same-life repeat
grants nothing. Scoped wipe preserves unrelated keys and pagehide does not recreate
the removed save. First two raw attempts remain diagnostic evidence.

Full `node-final-1`: **1614 retained + 86 new = 1700 / 0**, 24 suites.
Source audit verifies 23 inherited Node files unchanged, inherited browser AST
assertions unchanged and 38 protected cores identical. The external inherited
runner is active, starting Town Services then Lifecycle and other foundations,
ending with Quest/cache. Do not infer final acceptance before all actual reports.

## Final acceptance extension queued

The new browser suite now also prepares a valid existing Action Item ticket,
teleports, and verifies STALE_PACKAGE with no consumption in both classes.
This is test-only; previously passing 40-group report remains valid evidence
for unchanged runtime. Expanded final 42-group run is queued after inherited
browsers finish, to avoid concurrent browser resource contention. No inherited
test/assertion is edited. Integration Gate remains out of scope.

## Legacy diagnostic semantic preservation

Review found that delegating old Lifecycle.placePlayer to the new full teleport
would release AI targets before inherited perception/home-leash fixtures could
observe normal AI transitions. The old diagnostic helper is now exactly unchanged
from parent. It retains collision/transform validation and intentionally lets AI
observe the moved player. The new coherent world.teleport alone performs complete
travel reconciliation. No inherited assertion or diagnostic meaning is weakened.
Node/final new browser must rerun after this narrow compatibility correction.
The active Town Services suite does not use Lifecycle.placePlayer; the later
Lifecycle suite will load the preserved helper.
