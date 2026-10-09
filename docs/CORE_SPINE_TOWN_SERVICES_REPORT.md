# Shop / Storage / Town Services - working checkpoint

Foundation is IN PROGRESS. Patch 0.0.1 / Core Spine are not complete.

## Git / resume

- Branch: `backbone/shop-storage-town-services-0.0.1`.
- Authoritative fetched parent: `backbone/quest-foundation-0.0.1`.
- Exact parent HEAD: `fea51986a0dd1b5f9d94710b0d48261deab5f175`.
- Parent fetched, switched and pulled ff-only; clean before branch creation.
- Baseline: **1474 Node checks / 0 failures**, all 22 suites retained.
- Baseline evidence: `D:\Astraeon\backbone-verification\town-services\node-parent`.
- Runtime/test checkpoint: pending. Final documentation / remote HEAD: pending.

## Source audit and implementation boundary

Current Item State privately publishes canonical carried ownership and revision.
ItemInventory creates serial-backed instances; Equipment references carried IDs.
Capacity evaluates final ownership; Quest Collect reads carried ownership and
prepared Quest turn-in binds the Inventory identity/revision. Save v5 spreads
optional fields and already rejects future versions before Item normalization.
QuestEvidence owns semantic NPC interaction capabilities, not DOM interactions.

Current merchant offers are four stack items, with existing authored prices.
Its Item State compatibility trade has no NPC access boundary and no unique-item
trade support. No Storage module or saved container exists. Housing currently
supports room rent/rest/upgrade only. It is not established Storage lore.

Planned minimal binding: existing `merchant` for Merchant; existing
`housing-keeper` for explicitly NON-FINAL engineering Storage proof. No world,
NPC, visual, collision, navigation or Character source changes are required.
Fresh same-runtime interaction sessions will gate live operations; isolated
fixtures inject the same semantic authority. Inventory/Storage transfers move
exact instances and preserve metadata/serial. Storage reserves observed IDs at
load so carried allocation cannot reuse stored identity. No stored item affects
carried Capacity, Collect, Action Item or Equipment/Stats.

## Remaining work / exact next step

Implemented immutable full registry validation, existing stack prices plus one
explicit provisional Astral Blade offer, Storage normalization/global serial
reservation and private single-use current-interaction sessions. Owned tickets
bind both container identities/revisions, currency and runtime epoch. Atomic
Shop uses Item State's existing net transaction; transfers use one narrow exact
ownership publication without allocation. Capacity preflight/publication now
hold the existing mutation lock before injected policy callbacks.

New deterministic suite: **140 checks**, passing. Current full run:
**1474 inherited + 140 new = 1614 / 0** (`node-final`).
Prior integration run was 1613 / 0; the added check proves that restored
unsupported-schema quarantine IDs reserve serial even without a carried serial.
First core full run was 1585 / 0 (`node-core`); affected lock rerun 571 / 0.
Initial focused run had two rejection-code mismatches for NaN/Infinity count;
runtime now returns `INVALID_QUANTITY` consistently before JSON validation.

Live actual-NPC service adapters, functional existing Merchant/Housing panels,
isolated harness and deliberate boot/page/cache v96 are implemented. Save core,
Quest core, Loot/Box/AI/Combat, definitions/recipes and visual/world files remain
unchanged. Source adjacency assertion in inherited Box check initially failed
after adding service invalidation between Box invalidation and the loading flag;
adapter order was corrected, preserving the original assertion unchanged.

Browser attempt 1 reached actual Merchant with valid session and zero errors,
then failed a copied navigation helper's hardcoded Guild-window fixture check.
Generic target-kind assertion fixes only that fixture. Attempt 2 passed 18
Swordsman service/Storage/Collect/persistence/travel/harness groups, then hit a
30-second normal-URL create click timeout. Normal/harness contexts now use the
same bounded 180-second timeout as playable contexts. Both raw reports remain
under `browser-attempt-1` / `browser-attempt-2`; no console/page/HTTP error was
recorded. Final two-class run adds offline Storage reload and actual enemy-caused
player death before closure.

Inherited fixture adapters (behavioral assertions retained): action Item,
Inventory, Equipment Slots, Monster Box and Capacity browser merchant setup now
walks/interacts with the real Merchant. Capacity policy changes invalidate
sessions, so its buy/sell setup explicitly reinteracts after policy changes.
Quest cache fixture checks the active cache generation instead of literal v95,
retaining four-module precache and actual offline durable-state assertions.

Next: run final new two-class browser, all inherited suites, cache/offline,
world validator and source audit; fix any genuine failures. Keep
all inherited assertions; any fixture adaptation required by new NPC access
must retain behavior and be recorded. Full verification, cache/offline, world
validation, runtime checkpoint, final documentation and push remain pending.

## Verification checkpoint update

Current implementation HEAD before this report update: `71b883d` (resolve the
full SHA from Git). Full Node `node-final`: 1614 / 0. Source audit confirms all
22 inherited Node files byte-identical, inherited browser AST assertions intact
except one active-generation cache fixture, and protected paths untouched.
`browser-two-class-1` is still running; Swordsman actual Shop/Storage/Collect/
capacity/Action Item groups have passed through stored-Potion withdrawal.
All inherited browser suites and final cache remain pending. World validator
was interrupted to avoid concurrent large-scene validation competing with live
software WebGL; rerun it serially after browsers. This is not a schema result.
External evidence root and runner remain as above; do not mark accepted yet.

## New browser milestone

`browser-two-class-1/report.json`: **40 groups / 0 failures**, Swordsman and
Mage, 0 unexpected console/page/runtime/HTTP errors. Sixteen structured
rejections are expected acceptance evidence, not runtime errors. Actual NPC
movement/interactions, Shop and exact Storage transfers, Capacity failures,
carried-only Collect and stale Quest ticket, Action Item, offline reload,
ordinary field travel and actual enemy-caused death/town respawn pass.
Normal URL and isolated harness pass. All inherited browser suites are now
running sequentially using the external `run-browser-regressions.py`; inspect
`regression-runner.json` and per-suite command logs/reports. Do not treat the
new-suite success as final acceptance until all inherited/cache/world results
are confirmed. Runtime/test checkpoint and final documentation remain pending.
