# Monster Box Item / Opening — working checkpoint

Branch: `backbone/monster-box-0.0.1`.
Parent: `backbone/monster-lifecycle-0.0.1` at
`05243a45737dbe5a493b7753f5517d7ea920243b` (latest fetched remote HEAD).

## Resume point

Step 0 completed with fetch/switch/ff-only pull and clean tree before branch
creation. Immutable canonical proof item and separate Box Content grammar/resolver
are implemented. Owned non-rolling authorization and commit-time RNG connect
to a contained Item State transaction. Player APIs, existing Bag single-open,
isolated Monster Loot box proof and cache v92 are integrated. Lifecycle/Combat
core remains unchanged. Isolated harness is authored; browser acceptance next.

One box, `monster-box-proof`; one separate table, `box-proof-basic`, with equal
weighted material/consumable/equipment outcomes and a material quantity range.
All new content/coefficients are provisional. This is not final balance.

## Verification / remaining work

- Focused check passed: prepare consumed no entropy; bulk 3 committed material,
  consumable and canonical equipment; source quantity 3→0; four exact draws;
  nested RNG inventory mutation and duplicate commit rejected without reward.
- Full prior Node regression passed **859/859, zero failures** against the Item
  State extension; evidence `backbone-verification/monster-box/node-integration`.
- Full integrated Node suite passed **1001/1001, zero failures**: 141 new Box
  tests, all 859 previous checks retained, one additional automatic existing
  Loot validation case for the new isolated table. Evidence
  `backbone-verification/monster-box/node/report.json`.
- Initial new test driver had a syntax typo, then two incorrect assumptions:
  Combat requires explicit physical damageType; Lifecycle requires caller
  canRespawn policy. Corrected those new requests and required valid Combat
  output; all new/old assertions remain. Initial evidence `focused-initial.log`.
- Historical browser baseline 157 groups has not yet been rerun on this task.
- Item State revision and existing frozen inventory identity authorize tickets.
  Hidden post-roll failure retention prevents retry/new-prepare roll shopping.
  No reward data is exposed in rejected commit output.
- Remaining: focused browser acceptance, all previous browser regressions,
  world/cache verification, contract/final handoff documentation and push.
- Save version stays 5; no schema change planned. No lifecycle/combat/art/world
  edits are needed.

This is an incomplete working checkpoint, not an acceptance report. Patch 0.0.1
and Core Spine remain incomplete.
