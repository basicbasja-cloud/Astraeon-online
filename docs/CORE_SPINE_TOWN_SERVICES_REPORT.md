# Shop / Storage / Town Services — working checkpoint

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

Implement validated service/shop/storage contracts, private sessions and atomic
Shop/transfer plans through narrow Item State and Player adapters. Then add live
NPC UI adapters, isolated harness, deterministic and browser regressions. Keep
all inherited assertions; any fixture adaptation required by new NPC access
must retain behavior and be recorded. Full verification, cache/offline, world
validation, runtime checkpoint, final documentation and push remain pending.
