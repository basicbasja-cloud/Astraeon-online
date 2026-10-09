# Talk / Kill / Collect Quest — foundation handoff

**TALK / KILL / COLLECT QUEST FOUNDATION ✅** — all acceptance gates verified.

Only this foundation is implemented. **Patch 0.0.1 and Core Spine are not complete.**
The five engineering quests are not final story, dialogue, UI, content or balance.
See [contracts](CORE_SPINE_QUESTS.md).

## Git identity / resume

| Field | Value |
| --- | --- |
| Branch | `backbone/quest-foundation-0.0.1` |
| Starting parent branch | `backbone/equipment-slot-closure-0.0.1` |
| Exact fetched starting parent HEAD | `a946ba4e51e20b45aaf83aa85fb08e49755f6fc6` |
| Verified runtime source HEAD | `da4f46f7ff297a2f4970a47e41af259308a1b374`; checkpoint successors change documentation only |
| Runtime/test checkpoint | `f26260f64198e9fcf3de3cefc9f27921b48b4ecf` |
| Documentation checkpoint | First documentation commit; its exact SHA will be recorded by the final documentation successor. |
| Final documentation HEAD | Documentation successor containing this report; resolve `git rev-parse HEAD` on this branch and compare the fetched remote tip. Exact final/pushed SHA is recorded in the final response and external `FINAL_HANDOFF.md`. A committed file cannot contain its own Git commit hash. |

Fetch, parent switch/ff-only pull, clean fully updated parent, exact HEAD and recent
log were recorded before creating the requested branch. The pasted parent SHA
was confirmed against remote, never used to reset history. No unrelated merge,
rebase, force push, main modification or PR. Push only this branch normally.

Resume from the **current remote tip**, not a runtime checkpoint:

```powershell
git fetch origin
git switch backbone/quest-foundation-0.0.1
git pull --ff-only origin backbone/quest-foundation-0.0.1
git status --short
git rev-parse HEAD
```

## Files added / modified

Added: `quest-definitions.js`, `quest-state.js`, `quest-evidence.js`,
`quest-runtime.js`, `tests/quests.test.cjs`, `tests/quests_browser.py`,
`tools/quest.html`, `tools/quest-harness.js`, `docs/CORE_SPINE_QUESTS.md`,
`docs/CORE_SPINE_QUESTS_REPORT.md`.

Modified: `item-state.js`, `player-state.js`, `game.js`, `boot.js`, `index.html`,
`sw.js`, `README.md`, `ARCHITECTURE.md`, `docs/CORE_SPINE_ITEMS.md`,
`docs/CORE_SPINE_MONSTER_LIFECYCLE.md`, `docs/CORE_SPINE_INVENTORY_CAPACITY.md`.
No historical verification report was rewritten.

## Architecture / authority report

| Responsibility | Implemented contract |
| --- | --- |
| Definition authority | Frozen authored registry; stable quest/objective IDs, full validation before runtime registry publication |
| Definition validation | Primitive safe IDs, duplicate IDs, supported TALK/KILL/COLLECT, bounded positive whole counts, finite JSON metadata, known NPC/Monster/Item references, exact supported reward schema, prerequisite references/self/cycles and overflow/stack bounds |
| Player Quest State authority | Private runtime state; durable ACTIVE/COMPLETED entries and capped Talk/Kill counts keyed by objective IDs; own-entry lookup prevents inherited JavaScript properties from becoming state; no Quest Inventory/Gold/EXP/Monster ledger |
| Status machine | LOCKED/AVAILABLE from prerequisites; explicit acceptance; ACTIVE/READY derived from objectives; successful commit alone publishes COMPLETED; no abandonment/repeat/reset |
| Objective policy | Unordered objectives and multiple active quests; one valid event can progress independent matching quests once each |
| Talk integration | Existing NPC interaction calls semantic evidence adapter using authored service identity, real actor range/alive/town/context checks; menu/proximity/rendering/travel alone gives no credit |
| Talk identity | Frozen privately owned capability and monotonic diagnostic interaction ID; capped one-time progress; copied/foreign/replayed capabilities reject |
| Kill integration | Narrow bridge validates the exact existing Lifecycle death event object and current instance/life/death identity; definition ID comes from the same Lifecycle owner |
| Kill policy | Existing local player-owned Combat/death path only; no independent HP polling, Loot inference, party/assist/PvP credit or second death authority |
| Same/new life | Duplicate event never increments; respawned same runtime new life legitimately increments; no serialized lifetime death history |
| Collect integration | Current canonical stacks/owned instances, including equipped ownership; items from any canonical source count; no acquisition ledger |
| Collect readiness | Current ownership each evaluation; spending 3/3 down to 2/3 returns to ACTIVE; saved READY/Collect counters are not trusted |
| Collect consumption | Explicit consumeOnTurnIn; aggregate all consuming objectives, sharing same-item ownership pool; no reservation or debit before success |
| Non-stack Collect | Stable unequipped instance selection; equipped-only sources reject ITEM_EQUIPPED, preserving ownership/modifiers |
| Turn-in preparation | Alive/context/current semantic turn-in target + READY + complete source/reward plan + net existing Capacity/Character/gold preflight; non-mutating opaque ticket |
| Authorization integrity | Private WeakMap binds runtime, quest state/revision, epoch, inventory pointer/revision, progression/gold identity and complete plan; copied/forged/foreign/stale/duplicate tickets reject |
| Turn-in transaction | Narrow private Item State net transaction builds source debits and all canonical rewards locally, then contained synchronous Character/gold/completion publication and one ownership publication |
| Exactly-once completion | First commit marks ticket used and quest completed; duplicate/sibling/stale tickets cannot consume or grant again; no reward replay on load |
| Capacity / Weight | Existing exact net package calculator; consumed last stacks may free slots/weight; maxStack/serial/no-worse over-limit rules unchanged |
| Capacity failure | Sources, serial, EXP, gold, rewards and completion remain unchanged; READY remains inspectable; deterministic retry after freeing capacity |
| Base / Job EXP | Existing Character.prepareRewards/commitPreparedRewards and Progression formulas; existing level-up resource behavior retained |
| Gold | Existing writable finite player gold authority, prevalidated safe addition; no Quest currency ledger or new prices |
| Stack reward | Canonical stack merge and compatibility mirrors; no ItemInstance serial allocation |
| Equipment reward | Canonical unique ItemInstance per unit, exact serial advancement, owned and not auto-equipped; ordinary Equipment → Stats → Combat path |
| Reward RNG | None; deterministic authored Quest rewards. Loot/Box retain separate entropy authorities |
| Prerequisites | Completed quest IDs only; simple non-repeatable chain, full registry cycle rejection, availability re-derived after reload |
| Save/version decision | Deliberately v5: new optional extensible questState field changes no old field meaning; save-state.js and future >5 guard remain byte unchanged |
| Migration | Old saves start empty without acceptance/completion/rewards; unknown/invalid stored quest entries archived as inert JSON; unsupported objective keys ignored |
| Durable/transient split | Accepted identity, Talk/Kill counts and completion persist; Collect/readiness re-derive; tickets, evidence objects, actors, listeners and runtime event history do not serialize |
| Player death/respawn | Durable progress/ownership retained; existing runtime invalidation expires transient tickets; no rewards or Collect debit from death |
| Town/field/travel | Durable progress retained; loading invalidates tickets; direct observer delivery has no subscriptions to duplicate after travel/reconstruction |
| Monster Loot relationship | Death observation independent of Loot capacity acceptance; Loot resolution/commit alone never supplies Kill evidence; old EXP/gold/claim behavior unchanged |
| Monster Lifecycle relationship | Existing exact death/new-life authority unchanged; Quest observes output only, no AI/navigation/HP/respawn rewrite |
| Monster Box / Action Item | Canonical ownership may satisfy Collect; opening/consuming creates no Quest Kill/EXP completion semantics; RNG/cooldowns/learned slots remain separate |
| Equipment / merchant / crafting | Ordinary canonical sources of Collect ownership; reward gear uses existing equip authority; no new catalogue, recipes or economy |
| Legacy Contract compatibility | Existing automatic state.quest counters remain unchanged; new explicit quests use questState; migration does not fabricate new progress from legacy counters |
| Functional UI | Plain Accept/status/Turn In in existing guild/journal panels; no quest journal/tracker/marker/dialogue/art redesign |
| Developer tooling | Isolated tools/quest.html and astraeon-quest-dev-v1 storage; validation/state/plan/receipt/save/capacity inspection, real Combat HP → Lifecycle evidence and new-life controls |
| Production boundary | Only exact dev=1 exposes limited Quest diagnostics/actions; normal URL exposes no unrestricted Quest mutation global |
| Boot/cache | One deliberate generation 95; four Quest modules load before game attachment and are precached; retained historical compatibility URLs remain available |

### Atomicity / trust boundary

All deterministic failures are prevalidated against the complete net package.
No asynchronous yield, RNG or external presentation callback occurs in turn-in
publication. The private completion publisher is contained and non-throwing.
This preserves the existing trusted synchronous Item/Character publisher model;
it is not a general rollback engine for malicious callbacks or server security.

## Provisional proof quests

| Quest | Objectives | Authored reward proof |
| --- | --- | --- |
| quest-proof-talk | Guild Registrar ×1 | Base EXP 3, Job EXP 2, gold 4, Potion ×1 |
| quest-proof-kill | Existing leafmane-fox definition ×2 | Base EXP 5, Job EXP 3, gold 6, Herb ×1 |
| quest-proof-collect | Herb ×3 consumed on turn-in | gold 3, Potion ×1 |
| quest-proof-mixed | Registrar ×1 + Fox ×1 + Ore ×2 consumed | Base EXP 4, Job EXP 2, gold 5, existing offhand-proof ×1 |
| quest-proof-chain | Registrar ×1; talk quest completed prerequisite | gold 1, Ration ×1 |

All turn in at the existing guild-registrar. These values are replaceable,
configuration-driven engineering fixtures, explicitly NON-FINAL. No new NPC,
MonsterDefinition, ItemDefinition, gear balance, recipe or world placement.
Weighted/tiny capacity profiles and sandbox HP values are isolated test data;
production weights/limits/Combat coefficients are unchanged.

## Deterministic verification

**1309 inherited + 165 new Quest = 1474 passing / 0 failing** across 22 test files.
No inherited assertion was removed, weakened or fixture-adapted.
`tests/quests.test.cjs` covers registry immutability/validation/cycles, explicit
states/acceptance, owned Talk/Kill capabilities and duplicate/new-life behavior,
multiple quests/objectives, current Collect and aggregated/non-consuming sources,
private stale/foreign/copied/duplicate tickets, atomic consumption/rewards,
weighted net capacity and stack/serial failures, canonical EXP/gold/gear,
Action/Box separation, save/migration/future guard, twenty cycles for both classes,
source boundaries, actual executable harness button flow, valid prototype-named
identities and safe unknown/coercing transition rejection.

Full command: `python tools/run-node-checks.py --node D:/Node/node.exe --output <output>`.
Final evidence: `D:/Astraeon/backbone-verification/quests/node-final-confirmed/report.json`.

## Browser acceptance / local smoke

New Quest suite: **57 groups / 0 failures**, Swordsman and Mage. Actual ordinary
town walks, authored NPC picking/interaction, explicit UI acceptance/turn-in,
Basic Attack/learned Skill kills, Lifecycle death replay protection, Mage same
runtime life 1 → life 2 Kill progress 1 → 2, actual player death/respawn, travel,
current Collect, net capacity rejection/retry, canonical reward equipment/equip,
Action Item/Box separation, partial/completed reload, offline, isolated tooling
and normal URL all pass. Final new suite needs no encounter/contact retry.

No teleport, enemy HP edit, AI/collision disable, fake Kill, direct Quest progress
or completion mutation is used by the new playable acceptance flow. Base/Job
level/learned-slot setup, HP=1 for the actual enemy-caused death fixture, and
canonical material/tiny-capacity setup are isolated fixtures; actual NPC,
Combat/Lifecycle, Loot ownership and turn-in paths are also exercised. Collect
accepts current ownership from ordinary Loot and other canonical sources.

| Retained browser suite | Groups | Result |
| --- | ---: | --- |
| equipment_slots_browser | 59 | PASS |
| inventory_capacity_browser | 63 | PASS |
| monster_box_browser | 33 | PASS |
| monster_lifecycle_browser | 30 | PASS |
| monster_loot_browser | 26 | PASS |
| action_item_browser | 30 | PASS |
| inventory_browser | 15 | PASS |
| action_loadout_browser | 17 | PASS |
| combat_browser | 21 | PASS |
| skill_tree_browser | 11 | PASS |
| progression_browser | 7 | PASS |

Combined functional browser: **312 retained + 57 Quest = 369 groups / 0 failures**.
Final successful reports record zero console/page/runtime/HTTP errors.
Local smoke is the real two-class Quest flow plus retained system integration
suites; it does not certify artwork, final balance or device performance.

Evidence root: `D:/Astraeon/backbone-verification/quests/`:
`browser-final-second/report.json`, `final-regressions-summary.json`,
`final-regressions/<suite>/report.json`, `cache-final/`, `world-validation-final.log`,
`source-audit.json`, `harness-probe-fixed.log`.

## Failed-attempt evidence / timing observations

All initial failed attempts remain outside the checkout; none is hidden:

| Attempt | Passing groups before failure | Finding / correction |
| --- | --- | --- |
| browser-first | 13 | Player-death walking fixture timed out; real earlier Talk/Kill/reload/travel already passed |
| browser-second | 13 | Stationary death fixture assumed field gate position; authoritative field travel is center 14.5/14.5, outside all current detection ranges |
| browser-third | 20 | Real Loot increased Ore to four; removing one did not free the source slot. New fixture reads canonical quantity and removes only excess above two |
| browser-fourth | 22 | New test called a nonexistent ProgressionDev Box API; corrected to the existing MonsterBoxDev.open adapter |
| browser-fifth | 13 | Player-death wait timed out. Its last captured pre-wait state had time 8.06987 and HP 1; it was not fresh end-of-timeout evidence. A concurrent probe overlapped, but hidden-page pause was never established |
| browser-final | 13 | The same transient HP=0 double-wait timed out during a serial replay. Outer Playwright teardown prevented fresh diagnostics; the fixture now latches real HP=0 and Incoming Combat killed evidence before movement, and collects failure state while the page is alive |

The sixth run was serial, passed all 57 groups, and recorded only two
successful player-death position observations. Preliminary Equipment/Capacity/Box
and Lifecycle suites also passed unchanged. A later source review hardened
own-entry lookup for valid prototype-named Quest IDs and safe invalid transitions,
adding three Node checks. Final evidence reruns the full 57 Quest groups and all
312 inherited groups on that frozen source. The final player-death fixture is a
read-only frame observer that requires actual HP=0, existing Incoming Combat
killed=true, preserved durable progress and actual town respawn; it neither edits
progress nor fabricates death. This preserves and strengthens the assertion
without depending on a short state surviving two host polls. Failure diagnostics
now capture visibility/frame performance before teardown. A separate sandbox probe found an
unsupported HP API name; tools now call the actual shared applyCombatResult
signature, and executable Node/browser button regressions prove it. No Combat,
Lifecycle, navigation or world behavior changed to make these fixtures pass.
No inherited browser fixture or behavioral assertion was changed. All 11 retained suites pass unchanged on the final source.

The external orchestration reader initially stopped after Combat despite its
CLI exit 0, all 21 checks passing and empty errors: that historical suite writes
`ok:true`, rather than `result:"passed"`. The reader was corrected outside the
repository to accept the actual report grammar and continued the remaining
suites. Original reports/tests were not edited. Cache likewise uses its existing
boolean acceptance fields; these are checked directly with CLI exit 0.

## Cache / offline / world / source audit

Cache/offline: **PASS**. The unchanged cache acceptance verifies generation 95 (157 precached requests), saved-character retention, legacy-cache removal and offline town/art resume; the focused Quest suite additionally verifies offline durable Quest/inventory resume. Zero errors.

World validator: **PASS Terrain, Navigation, TownObject and AnimationManifest schemas**.
The bundled Python invocation requires the local verification dependency path
for Playwright/jsonschema. An initial validator retry omitted that path and failed
to import jsonschema; the configured unchanged-command rerun passed. This was an
environment setup error, with no World/source adaptation. Final validator evidence
is `world-validation-final.log`.
Source audit: **45 inherited test files + 34 protected core files = 79 source
files unchanged** (checkout line endings normalized for comparison).
`git diff --check` passes.
Protected world/visual/art path changes: **none**. Save core, Progression, Stats,
Skill Tree, Combat, Action Loadout/Item, canonical Item Inventory/Equipment,
equipment registry, Monster Loot/Lifecycle/Box and Capacity cores remain unchanged.
Only the documented Item State/Player/game/boot/cache adapters are extended.

## Known limitations / potential integration conflicts

Unordered, non-repeatable local quests only. No abandonment/failure/timers,
daily scheduling, dialogue/stage scripting, party/assist attribution, random
rewards, quest-bound items, separate Quest Inventory or server networking.
Interaction registry covers current town services. Equipped Collect items require
ordinary unequip before consumption. No overflow/storage policy is invented.
Authored objective-ID evolution needs a deliberate future migration policy.
Legacy automatic Contract behavior is retained separately, not migrated into
new accepted quests. Local opaque capabilities are integrity boundaries, not
protection against an owner controlling the client/save.

Likely integration conflicts: shared `game.js`, `player-state.js`, `item-state.js`,
boot/page/SW import/cache lists and current architecture docs. Coordinate these
adapters when integrating other branches; do not merge World/Character work here.
`authoring/**`, `RO3 Ref/**`, `assets/**`, `world/**`, renderer, navigation,
collision, lighting, camera, sprite/motion/VFX pipelines and `style.css` are untouched.
No visual-equipment or Character Rescue work was introduced.

## Next Backbone task

**SHOP / STORAGE / TOWN SERVICES FOUNDATION**. Do not start it in this branch.
Progression/Stats, Skill Tree, Combat, Action Loadout, Items/Equipment, Action
Items, Monster Loot/Lifecycle/Box, Capacity and Equipment Slot Closure remain
verified. Quest closure adds this foundation only. Dev-tool gap closure and
the **0.0.1 Integration Gate remain pending**; Patch 0.0.1 is not complete.
